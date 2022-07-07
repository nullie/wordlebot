from typing import List
import irc.bot
import irc.strings
import irccodes

import wordle


BACKGROUND_COLORS = {
    wordle.Status.MISS: ('white', 'grey'),
    wordle.Status.RIGHT_PLACE: ('white', 'green'),
    wordle.Status.RIGHT_LETTER: ('black', 'yellow'),
}


def format_wordle_hint(guess: List[wordle.Letter]):
    return ' '.join(
        irccodes.colored(
            ' ' + irccodes.bold(letter.letter) + ' ',
            *BACKGROUND_COLORS[letter.status], '')
        for letter in guess
    )


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.wordle = wordle.Game()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel, self.wordle.hint())

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            self.do_command(e, a[1].strip())
        return

    def do_command(self, e, cmd):
        c = self.connection

        try:
            correct, hint = self.wordle.guess(cmd.lower())
        except wordle.GuessError as e:
            c.privmsg(self.channel, e.args[0])
        else:
            if correct:
                nick = e.source.nick
                self.wordle.restart()
                c.privmsg(
                    self.channel,
                    f'{format_wordle_hint(hint)}, congrats, {nick}, next word: {self.wordle.hint()}'
                )
            else:
                c.privmsg(self.channel, format_wordle_hint(hint))


def main():
    import sys

    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    main()
