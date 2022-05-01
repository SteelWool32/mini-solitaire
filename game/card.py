from game.enums import Suit, Color
from game.consts import CARD_HEIGHT, CARD_WIDTH, CARD_DISTANCE_SPLIT
import pyxel


class Card:
    def __init__(self, suit, rank, is_face_up = False) -> None:
        self.suit = suit
        self.rank = rank
        self.is_face_up = is_face_up
        self.color = Color.Black

        if suit == Suit.Hearts or suit == Suit.Diamonds:
            self.color = Color.Red

        self.pile = None

        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.update_uv()

    @property
    def width(self):
        return CARD_WIDTH

    @property
    def height(self):
        return CARD_HEIGHT

    @property
    def center(self):
        return (self.x + (CARD_WIDTH//2), self.y + (CARD_HEIGHT//2))

    def update(self):
        if self.x != self.target_x:
            dx = (self.target_x - self.x) // CARD_DISTANCE_SPLIT
            self.x = self.x + dx if dx != 0 else self.target_x

        if self.y != self.target_y:
            dy = (self.target_y - self.y) // CARD_DISTANCE_SPLIT
            self.y = self.y + dy if dy != 0 else self.target_y

    def render(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, CARD_WIDTH, CARD_HEIGHT, 14)

    def set_face_up(self):
        self.is_face_up = True
        self.update_uv()

    def set_face_down(self):
        self.is_face_up = False
        self.update_uv()

    def flip(self):
        self.is_face_up = not self.is_face_up
        self.update_uv()

    def update_uv(self):
        self.u = (self.rank) * CARD_WIDTH if self.is_face_up else 0
        self.v = (self.suit * CARD_HEIGHT) + CARD_HEIGHT if self.is_face_up else 0  

    def move_to(self, x, y, instant = False):
        self.target_x = x
        self.target_y = y
        if instant:
            self.x = x
            self.y = y

    def is_moving(self) -> bool:
        return self.x != self.target_x and self.y != self.target_y