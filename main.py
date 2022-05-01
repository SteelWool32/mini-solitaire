from time import perf_counter, time_ns
import random
import pyxel

from game.card import Card
from game.pile import Pile
from game.move import Move
from game.consts import CARD_HEIGHT, CARD_SPACING, CARD_WIDTH


Buttons = {
    'retry': pyxel.KEY_R,
    'new': pyxel.KEY_N,
    'help': pyxel.KEY_H,
    'mode_switch': pyxel.KEY_TAB,
    'select': pyxel.MOUSE_BUTTON_LEFT,
    'cancel': pyxel.MOUSE_BUTTON_RIGHT,
}


class App:
    def __init__(self) -> None:
        width = 128 # 160
        height = 128 # 144
        pyxel.init(width, height, title="Solitaire", fps= 60)
        pyxel.load("assets/assets.pyxres")

        pyxel.mouse(True)

        self.config = {
            "drag_and_drop": True
        }

        self.rng_seed = None
        self.offset_x = 0
        self.offset_y = 0
        self.move_count = 0
        self.game_status = "new"
        self.move_log = []
        self.last_click_time = 0

        self.next_move = Move()
        self.perform_next_move = True
        self.log_next_move = True

        self.show_help = False

        self.cards = [Card(i // 13, i % 13) for i in range(52)]

        self.piles = {
            "tableau0": Pile(2, 32),
            "tableau1": Pile(20, 32),
            "tableau2": Pile(18*2 + 2, 32),
            "tableau3": Pile(18*3 + 2, 32),
            "tableau4": Pile(18*4 + 2, 32),
            "tableau5": Pile(18*5 + 2, 32),
            "tableau6": Pile(18*6 + 2, 32),
            "stock": Pile(2, 2, render_all= False, render_slot= False),
            "waste": Pile(20, 2, render_all= False),
            "foundation0": Pile(18*3 + 2, 2, render_all= False),
            "foundation1": Pile(18*4 + 2, 2, render_all= False),
            "foundation2": Pile(18*5 + 2, 2, render_all= False),
            "foundation3": Pile(18*6 + 2, 2, render_all= False)
        }

        for key in self.piles.keys():
            self.piles[key].id = key

        self.new_game()
        pyxel.run(self.update, self.render)

    def get_cursor_pos(self):
        return (pyxel.mouse_x, pyxel.mouse_y)
    
    def get_offset_cursor(self):
        return (pyxel.mouse_x - self.offset_x, pyxel.mouse_y - self.offset_y)

    def set_cursor_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def new_game(self, seed = None):
        """Resets game state and starts a new game."""
        
        # Set all cards face down, clears assigned pile
        for card in self.cards:
            card.set_face_down()
            card.pile = None

        # Clear all piles
        for pile in self.piles.values():
            pile.clear()

        # Resets state
        self.rng_seed = time_ns() if seed == None else seed
            
        random.seed(self.rng_seed)
        self.game_status = "new"
        self.move_log.clear()
        self.reset_move()

        self.move_count = 0

        # Assign cards to stock pile and shuffle
        stock = self.piles["stock"]
        stock.add(self.cards)
        stock.shuffle()
        stock.position_cards(now = True)

    def win_game(self, force = False):
        """Wins game and sets appropiate game state."""

        if force:
            for pile in self.piles.values():
                pile.clear()
            for card in self.cards:
                card.set_face_up()

            for i in range(4):
                cards = self.cards[i*13: i*13 + 12]
                self.piles[f"foundation{i}"].add(cards)
                self.piles[f"foundation{i}"].position_cards(now = True)

            self.piles["tableau0"].add([c for c in self.cards if c.rank == 12])
            return

        self.game_status = "win"
        
    def get_pile_at(self, x, y) -> Pile:
        """Returns pile at the indicated (x, y) coordinates."""
        for pile in self.piles.values():
            if x > pile.x and y > pile.y and x < pile.x + pile.width and y < pile.y + pile.height:
                return pile
        
        return None

    def get_card_at(self, x, y) -> Card:
        """Returns the card at the indicated (x,y) coordinates."""
        pile = self.get_pile_at(x, y)

        if pile and len(pile) > 0:
            if pile.render_all:
                for i in range( len(pile.cards)-1 , -1, -1):
                    card = pile.cards[i]
                    if x > card.x and y > card.y and x < card.x + card.width and y < card.y + card.height:
                        return card
            else:
                return pile.top_card

        return None

    def get_card_amount(self, card:Card):
        """Returns the amount of cards to move."""
        pile = card.pile
        if 'tableau' in pile.id:
            if card and card.is_face_up:
                index = pile.cards.index(card)
                diff = len(pile) - index
                lower_card = None if index == 0 else pile.cards[index-1]
                self.config_move(flip_source_top= not lower_card.is_face_up if lower_card else False)

                return diff
        else:
            return 1

    def get_cards_moving(self):
        """Returns a list of cards currently moving."""
        cards = [c for c in self.cards if c.is_moving() == True]
        return cards

    def get_cards_down(self):
        """Returns a list of cards currently face-down."""
        cards = [c for c in self.cards if not c.is_face_up]
        return cards

    def config_move(
        self,
        source:Pile = None,
        target:Pile = None,
        amount:int = None,
        flip_source_top:bool = None,
        flip_source_pile:bool = None,
        flip_target_top:bool = None,
        flip_target_pile:bool = None,
        log_move: bool = None
    ):
        """Configure next move."""
        if source != None:
            self.next_move.source = source

        if target != None:
            self.next_move.target = target

        if amount != None:
            self.next_move.amount = amount

        if flip_source_top != None:
            self.next_move.flip_source_top = flip_source_top

        if flip_source_pile != None:
            self.next_move.flip_source_pile = flip_source_pile

        if flip_target_top != None:
            self.next_move.flip_target_top = flip_target_top

        if flip_target_pile != None:
            self.next_move.flip_target_pile = flip_target_pile

        if log_move != None:
            self.log_next_move = log_move

    def validate_move(self, source:Pile, target:Pile, amount:int) -> bool:
        """Validate moves performed by dragging cards. Not used when undoing moves or clicking the Stock pile.
        Returns a boolean value indicating the attempted move is valid."""

        # Amount is non-positive, invalid
        if amount <= 0:
            return False

        # Source is the same as Target, invalid 
        if source == target:
            return False
        
        # Source is empty, invalid
        if source.is_empty:
            return False

        # Target is Stock or Waste piles, invalid
        if 'stock' in target.id or 'waste' in target.id:
            return False

        # Source is Waste or Foundation, amount is greater than 1, invalid
        if 'waste' in source.id or 'foundation' in source.id:
            if amount > 1:
                return False

        # Target is Foundation and amount is greater than 1, invalid
        if 'foundation' in target.id and amount > 1:
            return False

        # Source is Waste, Foundation or Tableau
        elif 'waste' in source.id or 'foundation' in source.id or 'tableau' in source.id:

            # Target is Foundation
            if 'foundation' in target.id:
                # Only Aces are allowed in empty Foundations
                if target.is_empty and source.top_card.rank == 0:
                    return True

                # Not-empty Foundations may only take cards of the same suit if it's one rank higher than it's top card.
                elif not target.is_empty:
                    source_top = source.top_card
                    target_top = target.top_card
                    if source_top.suit == target_top.suit and source_top.rank == target_top.rank + 1:
                        return True

            # Target is Tableau
            elif 'tableau' in target.id:

                # Compare the lowest card of the source with the top card of the target
                source_card = source.cards[-amount]

                # "Only kings may occupy empty thrones"
                # Fuck it, any card or pile can go in empty spaces.
                if target.is_empty:
                    return True

                # Non-empty Tableaus may only take cards of alternating colors if it's one rank lower than it's top card.
                elif target.top_card.color != source_card.color and source_card.rank + 1 == target.top_card.rank:
                    return True
        
        # Any other move, invalid
        return False

    def perform_move(
        self,
        source:Pile,
        target:Pile,
        amount = None,
        flip_source_top = False,
        flip_source_pile = False,
        flip_target_top = False,
        flip_target_pile = False,
        log_move = True
    ):
        """Executes movevement of cards between piles."""
        
        # If no amount is defined, move whole source
        if amount == None:
            amount = len(source)
        elif amount == 0:
            return
        
        # Move cards from source to target
        target.add(source.draw(amount))
        
        # Play sound
        pyxel.play(0, 0)

        if not source.is_empty:
            # Flip source's top card if requested
            if flip_source_top:
                source.top_card.flip()

            # Flip source pile if requested
            if flip_source_pile:
                source.flip()

        # Flip target's top card if requested
        if flip_target_top:
            target.top_card.flip()

        # Flip target pile if requested
        if flip_target_pile:
            target.flip()

        if log_move:
            self.log_move(
                source,
                target,
                amount,
                flip_source_top,
                flip_source_pile,
                flip_target_top,
                flip_target_pile
            )

    def log_move(
        self,
        source:Pile,
        target:Pile,
        amount = None,
        flip_source_top = False,
        flip_source_pile = False,
        flip_target_top = False,
        flip_target_pile = False,
    ):
        """Records move to facilitate undoing. Also increases move counter."""

        self.move_log.append(
            Move(
                source,
                target,
                amount,
                flip_source_top,
                flip_source_pile,
                flip_target_top,
                flip_target_pile
            )
        )

        self.move_count += 1
        
    def undo_move(self, move:Move):
        """Returns board to state before last move."""
        if move:
            if not move.target.is_empty:
                # Flip source's top card previous to move, if requested
                if move.flip_target_top:
                    move.target.top_card.flip()

                # Flip source pile previous to move, if requested
                if move.flip_target_pile:
                    move.target.flip()

            if not move.source.is_empty:
                # Flip target's top card previous to move, if requested
                if move.flip_source_top:
                    move.source.top_card.flip()

                # Flip target pile previous to move, if requested
                if move.flip_source_pile:
                    move.source.flip()

            # Move cards from source to target
            move.source.add(move.target.draw(move.amount))

    def reset_move(self):
        """Resets move state back to defaults."""
        self.next_move.source = None
        self.next_move.target = None
        self.next_move.amount = 0
        self.next_move.flip_source_pile = False
        self.next_move.flip_source_top = False
        self.next_move.flip_target_pile = False
        self.next_move.flip_target_top = False

    def try_quick_move(self, pile, card:Card):
        """Attempts to perform a quick move and returns True if the move can be performed."""
        if not card or not card.is_face_up:
            return False

        f_piles = [f for f in self.piles.values() if 'foundation' in f.id]

        if card.rank == 0:
            f_piles = list(filter(lambda f: f.is_empty, f_piles))
        else:
            f_piles = list(filter(lambda f: not f.is_empty and f.top_card.suit == card.suit and f.top_card.rank == card.rank - 1, f_piles))

        if len(f_piles) > 0:
            amount = self.get_card_amount(card)
            if amount > 0:
                self.config_move(pile, f_piles[0], amount, log_move= True)
                return True
        
        return False

    def on_click(self, x, y, quick_move = False):
        pile = self.get_pile_at(x, y)
        card = self.get_card_at(x, y)

        # No pile clicked, win excluded
        if pile == None:
            return

        if 'stock' in pile.id and self.next_move.source == None:
            waste = self.piles["waste"]
            if pile.is_empty and not waste.is_empty:
                self.perform_move(waste, pile, len(waste), flip_target_pile=True)
            elif not pile.is_empty:
                self.perform_move(pile, waste, 1, flip_target_top= True)
            return
        elif pile.is_empty and self.next_move.amount == 0:
            return

        # Move type
        if quick_move:
            self.try_quick_move(pile, card)

        elif self.next_move.source == None:
            self.set_cursor_offset(x - card.x, y - card.y)
            amount = self.get_card_amount(card) if 'tableau' in pile.id else 1
            self.config_move(source= pile, amount= amount)

        elif self.next_move.target == None:
            self.config_move(target= pile)

    def try_autoplay(self):
        piles = [p for p in self.piles.values() if 'tableau' in p.id or 'waste' in p.id]

        for p in piles:
            if p.top_card:
                if self.try_quick_move(p, p.top_card):
                    return

    def handle_input(self):
        # New game
        if pyxel.btnp(Buttons['new']):
            self.new_game()

        # Retry
        elif pyxel.btnp(Buttons['retry']):
            self.new_game(self.rng_seed)

        elif pyxel.btnp(Buttons['help']):
            self.show_help = not self.show_help

        # Mode switch
        elif pyxel.btnp(Buttons['mode_switch']):
            self.config['drag_and_drop'] = not self.config['drag_and_drop']

        #elif pyxel.btnp(pyxel.KEY_W):
            #self.win_game(True)

    def drop_text(self, x, y, s, fg=pyxel.COLOR_WHITE, bg=pyxel.COLOR_BLACK):
        pyxel.text(x, y+1, s, bg)
        pyxel.text(x, y, s, fg)


    def update(self):
        self.handle_input()

        if self.game_status == "new":

            f_piles = [p for p in self.piles.values() if 'tableau' in p.id]
            lowest_height = len(self.piles['tableau6'])

            moving = self.get_cards_moving()

            if len(moving) == 0:
                if lowest_height < 7:
                    for i in range(lowest_height, 7):
                        self.perform_move(self.piles["stock"], f_piles[i], 1, log_move= False)                  

                if lowest_height >= 7:
                    for f in f_piles:
                        f.position_cards(now = True)
                        if not f.top_card.is_face_up:
                            f.top_card.flip()
                            return

                    self.game_status = "play"

        elif self.game_status == "play":
            moving = self.get_cards_moving()

            # Left Mouse draws and places, right mouse cancels and undoes
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                click_time = perf_counter()
                self.on_click(*self.get_cursor_pos(), pyxel.btn(pyxel.KEY_SHIFT) or click_time - self.last_click_time < 0.5)
                self.last_click_time = click_time

            elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                # If no move configured, undo last move 
                if not self.next_move.source:
                    last_move = None if len(self.move_log) == 0 else self.move_log.pop()
                    if last_move != None:
                        self.undo_move(last_move)

                # Otherwise, reset move
                else:
                    self.reset_move()

            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                map(lambda p: p.position_cards(), self.piles.values())

            # Release
            if self.config["drag_and_drop"]:
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.next_move.source != None:
                    
                    source_card = self.next_move.source.cards[-self.next_move.amount]
                    self.next_move.target = self.get_pile_at(*source_card.center)

                    if self.next_move.source == None:
                        self.next_move.target = self.get_pile_at(*self.get_cursor_pos())

                    if self.next_move.source != None:
                        if self.next_move.target != None:
                            if self.next_move.source == self.next_move.target:
                                self.reset_move()
                        else:
                            self.reset_move()

            if len(self.get_cards_moving()) == 0:
                
                #win condition
                f_piles = [p for p in self.piles.values() if 'foundation' in p.id and len(p) == 13]
                if len(f_piles) == 4:
                    self.win_game()

                # Autoplay
                elif len(self.get_cards_down()) == 0:
                    self.try_autoplay()

            # Process move if any
            if self.next_move.source != None and self.next_move.target != None:                
                
                m = self.next_move

                # Perform move if valid
                is_valid = self.validate_move(m.source, m.target, m.amount)
                if is_valid:
                    self.perform_move(m.source, m.target, m.amount, m.flip_source_top, m.flip_source_pile, m.flip_target_top, m.flip_target_pile)

                self.reset_move()

            # Cards in hand
            if self.next_move.source and self.next_move.amount > 0:
                self.next_move.source.position_cards(*self.get_offset_cursor(), self.next_move.amount, now = True)

        elif self.game_status == "win":
            pass

        # Update cards and piles
        for card in self.cards:
            card.update()

        for pile in self.piles.values():
            pile.position_cards()
            
    def render(self):
        stock = self.piles["stock"]

        pyxel.cls(3)

        # render stock pile's unique slot
        if len(stock) == 0:
            pyxel.blt(stock.x, stock.y, 0, 32, 0, CARD_WIDTH, CARD_HEIGHT, 14)

        # render pile slots
        for pile in self.piles.values():
            if pile.render_slot:
                pyxel.blt(pile.x, pile.y, 0, 16, 0, CARD_WIDTH, CARD_HEIGHT, 14)

        # render piles and cards
        for pile in self.piles.values():
            if pile != self.next_move.source:
                pile.render()

        # Render currently selected pile
        if self.next_move.source != None:
            self.next_move.source.render()

        # render moving cards on top of the rest
        moving = self.get_cards_moving()

        for card in moving:
            card.render()

        if self.game_status == "win":
            pyxel.rect(42, 67, 50, 20, pyxel.COLOR_NAVY)
            self.drop_text(52, 69, "YOU WIN!", 7)
            self.drop_text(48, 79, "Moves: %3i" % self.move_count, 7)
        else:
            if not self.next_move.source:
                pile = self.get_pile_at(*self.get_cursor_pos())
                card = self.get_card_at(*self.get_cursor_pos())

                if card and pile and card.is_face_up and pile.card_spacing < CARD_SPACING:
                    card.render()
            else:
                self.next_move.source.render()

        s = "Moves: %3i     [H] Help" % self.move_count
        self.drop_text(2, pyxel.height - 7, s, 7)

        if self.show_help:
            pyxel.rect(4, 4, 120, 120, pyxel.COLOR_NAVY)

            s = """Game Rules:
-Goal: move all cards to the 
4 Foundations (upper-right)
as ordered cards of the same
suit, in ascending rank
(A, 2-10, J, Q, K).
-Place cards in the seven
Tableau Columns (bottom) in 
descending rank (K, Q, J, 
10-2, A), alternating color.
-Get more cards from the
Stock and Waste (upper-left).

Controls:
-Left-click: move cards.
-Right-click: undo move.
-N: new game.
-R: retry current game.
-Tab: Toggle drag-n-drop.
"""
            self.drop_text(8, 8, s)

def main():
    App()

if __name__ == '__main__':
    main()