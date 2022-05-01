from enum import IntEnum, auto

class Suit(IntEnum):
    Hearts = 0
    Diamonds = 1
    Spades = 2
    Clubs = 3
    Win = 4

class Color(IntEnum):
    Red = auto()
    Black = auto()