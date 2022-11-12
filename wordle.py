from collections import Counter
from enum import Enum, auto
import random
import re
from typing import Iterator, List, NamedTuple, Tuple


class Status(Enum):
    MISS = auto()
    RIGHT_PLACE = auto()
    RIGHT_LETTER = auto()


class Letter(NamedTuple):
    letter: str
    status: Status


class Game:
    def __init__(self, word_dictionary: str, guess_dictionary) -> None:
        self.words = set(load_good_words(word_dictionary))
        self.guesses = set(load_good_words(guess_dictionary))
        self.word = random.choice(list(self.words))

    def restart(self):
        self.word = random.choice(list(self.words))

    def hint(self) -> str:
        return f'{len(self.word)} letters'

    def guess(self, guess: str) -> Tuple[bool, List[Letter]]:
        guess = guess.lower()

        if len(guess) != len(self.word):
            raise GuessError(f'wrong length ({len(self.word)} letters)')

        if guess not in self.guesses:
            raise GuessError('not in the word list')

        word_counts = Counter(self.word)
        right_place = set()
        for i, (word_letter, guess_letter) in enumerate(zip(self.word, guess)):
            if word_letter == guess_letter:
                right_place.add(i)
                word_counts[guess_letter] -= 1

        right_letter = set()
        for i, letter in enumerate(guess):
            if i not in right_place and word_counts[letter] > 0:
                right_letter.add(i)
                word_counts[letter] -= 1

        return guess == self.word, [
            Letter(
                letter,
                (
                    Status.RIGHT_PLACE if i in right_place
                    else Status.RIGHT_LETTER if i in right_letter
                    else Status.MISS
                )
            )
            for i, letter in enumerate(guess)
        ]


class GuessError(Exception):
    pass


def load_good_words(dictionary: str) -> Iterator[str]:
    with open(dictionary) as f:
        for word in f:
            word = word.strip().lower()
            if re.fullmatch('[a-z]+', word) and 4 <= len(word) <= 8:
                yield word
