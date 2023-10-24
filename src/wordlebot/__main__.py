from typing import List
import irc.bot
import irc.client
import irc.strings
import irccodes

from . import wordle


BACKGROUND_COLORS = {
    wordle.Status.MISS: ('white', 'grey'),
    wordle.Status.RIGHT_PLACE: ('white', 'green'),
    wordle.Status.RIGHT_LETTER: ('black', 'yellow'),
}


def format_wordle_letter(letter: wordle.Letter):
    return irccodes.colored(
        ' ' + irccodes.bold(letter.letter) + ' ',
        *BACKGROUND_COLORS[letter.status], '')


def format_wordle_reply(guess: List[wordle.Letter]):
    if ''.join(letter.letter for letter in guess) == 'rainbow':
        return ''.join(
            format_wordle_letter(letter) + (
                ''
                if separator is None else
                irccodes.colored(' ', color='black', background_color=separator, padding='')
            )
            for letter, separator in zip(
                guess,
                [
                    'light red',
                    'orange',
                    'yellow',
                    'green',
                    'blue',
                    'purple',
                    None
                ]
            )
    )
    return ' '.join(map(format_wordle_letter, guess))


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, word_dictionary, guess_dictionary):
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.wordle = wordle.Game(word_dictionary, guess_dictionary)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel, self.wordle.hint())

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]

        try:
            correct, hint = self.wordle.guess(msg.strip())
        except wordle.GuessError:
            pass
        else:
            self.react(e, correct, hint)

        if irc.strings.lower(msg).startswith('w '):
            self.do_command(e, msg[2:].strip())
            return

        a = msg.split(":", 1)
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
            self.react(e, correct, hint)

    def react(self, e, correct, hint):
        c = self.connection

        if correct:
            nick = e.source.nick
            self.wordle.restart()
            c.privmsg(
                self.channel,
                f'{format_wordle_reply(hint)}, congrats, {nick}, next word: {self.wordle.hint()}'
            )
        else:
            c.privmsg(self.channel, format_wordle_reply(hint))


def main():
    import sys

    if len(sys.argv) != 6:
        print("Usage: testbot <server[:port]> <channel> <nickname> <word_dictionary> <guess_dictionary>")
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
    word_dictionary = sys.argv[4]
    guess_dictionary = sys.argv[5]

    irc.client.ServerConnection.buffer_class.errors = "replace"

    bot = TestBot(channel, nickname, server, port, word_dictionary, guess_dictionary)
    bot.start()


if __name__ == "__main__":
    main()
