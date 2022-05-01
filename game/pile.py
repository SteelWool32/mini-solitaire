from typing import List
from game.card import Card
from game.consts import CARD_HEIGHT, CARD_WIDTH, CARD_SPACING
import pyxel
import random


class Pile:
    def __init__(self, x, y, render_all= True, render_slot = True) -> None:
        self.x = x
        self.y = y
        self.render_all = render_all
        self.render_slot = render_slot
        self.card_spacing = CARD_SPACING

        self.cards:List[Card] = []
        
    def render(self):
        if len(self.cards) == 0:
            return
        
        if self.render_all:
            for card in self.cards:    
                card.render()
        else:
            if len(self.cards) > 1:
                self.cards[-2].render()

            self.cards[-1].render()
    
    def __len__(self) -> int:
        return len(self.cards)

    @property
    def width(self):
        return CARD_WIDTH

    @property
    def height(self):
        if 'tableau' in self.id:
            return max(CARD_HEIGHT, CARD_HEIGHT + (self.card_spacing * (len(self.cards) - 1)))
        else:
            return CARD_HEIGHT

    @property
    def is_empty(self):
        return len(self.cards) == 0

    @property
    def top_card(self) -> Card:
        """The top card is the last list element."""
        return self.cards[-1] if len(self.cards) > 0 else None

    @property
    def second_card(self) -> Card:
        """The second card underneath the top card would be the second-to-last list element."""
        return self.cards[-2] if len(self.cards) > 1 else None

    @property
    def bottom_card(self) -> Card:
        """The bottom card is the first list element."""
        return self.cards[0] if len(self.cards) > 0 else None

    def position_cards(self, offset_x = None, offset_y = None, hand_size = 0, now = False):
        pile_cards = []
        hand_cards = []

        if hand_size > 0:
            pile_cards = self.cards[:-hand_size]
            hand_cards = self.cards[-hand_size:]
        else:
            pile_cards = self.cards[:]

        self.card_spacing = CARD_SPACING

        while self.y + self.height >= pyxel.height - 8:
            self.card_spacing -= 1
            
        for i in range(len(pile_cards)):
            card = pile_cards[i]
            if not card:
                break

            # Set card coordinates
            x = self.x
            y = self.y + (i * self.card_spacing) if self.render_all else self.y
            card.move_to(x, y, now)

        for i in range(len(hand_cards)):
            card = hand_cards[i]
            if not card:
                break

            # Set card coordinates
            x = offset_x 
            y = offset_y + (i * self.card_spacing) if self.render_all else offset_y
            card.move_to(x, y, now)

    def add(self, cards:List[Card]):
        """Add cards from list to the pile."""
        if isinstance(cards, list):
            self.cards = self.cards + cards
            for card in cards:
                card.pile = self

            self.position_cards()
            
    def draw(self, amount:int = 1) -> List[Card]:
        """Return a list of cards drawn from the top of the pile (the last elements of the list)."""
        amount = max(1, min(amount, len(self.cards)))
        
        staying_cards = self.cards[:-amount]
        moving_cards = self.cards[-amount:]

        self.cards = staying_cards

        return moving_cards

    def clear(self):
        self.cards.clear()
        
    def reverse(self):
        """Reverse order of cards list."""
        self.cards.reverse()

    def shuffle(self):
        """Shuffle pile."""
        random.shuffle(self.cards)

    def flip(self):
        """Reverse pile and flip all cards."""
        self.reverse()
        for i in range(len(self.cards)):
            self.cards[i].flip()