from enum import Enum
from random import shuffle, choice

class Colors(Enum):
    TOK   = 0
    MAKK  = 1
    ZOLD  = 2
    PIROS = 3

class Figures(Enum):
    VII    = 0
    VIII   = 1
    IX     = 2
    X      = 3
    ALSO   = 4
    FELSO  = 5
    KIRALY = 6
    ASZ    = 7

def card_filename(card):
    match card.color:
        case Colors.TOK:
            color_str = "tok"
        case Colors.MAKK:
            color_str = "makk"
        case Colors.ZOLD:
            color_str = "zold"
        case Colors.PIROS:
            color_str = "piros"
        case _:
            color_str = "unknown"
    match card.figure:
        case Figures.VII:
            figure_str = "het"
        case Figures.VIII:
            figure_str = "nyolc"
        case Figures.IX:
            figure_str = "kilenc"
        case Figures.X:
            figure_str = "tiz"
        case Figures.ALSO:
            figure_str = "also"
        case Figures.FELSO:
            figure_str= "felso"
        case Figures.KIRALY:
            figure_str = "kiraly"
        case Figures.ASZ:
            figure_str = "asz"
        case _:
            figure_str = "unknown"
    return f"{color_str}_{figure_str}"

class Card:
    def __init__(self, color, figure):
        self.color = color
        self.figure = figure

    def __repr__(self):
        return f"{Colors(self.color).name} {Figures(self.figure).name}"
    
    def __eq__(self, other):
        return self.figure == other.figure and self.color == other.color

deck = [
    Card(Colors.TOK, Figures.VII),
    Card(Colors.TOK, Figures.VIII),
    Card(Colors.TOK, Figures.IX),
    Card(Colors.TOK, Figures.X),
    Card(Colors.TOK, Figures.ALSO),
    Card(Colors.TOK, Figures.FELSO),
    Card(Colors.TOK, Figures.KIRALY),
    Card(Colors.TOK, Figures.ASZ),

    Card(Colors.MAKK, Figures.VII),
    Card(Colors.MAKK, Figures.VIII),
    Card(Colors.MAKK, Figures.IX),
    Card(Colors.MAKK, Figures.X),
    Card(Colors.MAKK, Figures.ALSO),
    Card(Colors.MAKK, Figures.FELSO),
    Card(Colors.MAKK, Figures.KIRALY),
    Card(Colors.MAKK, Figures.ASZ),
    
    Card(Colors.ZOLD, Figures.VII),
    Card(Colors.ZOLD, Figures.VIII),
    Card(Colors.ZOLD, Figures.IX),
    Card(Colors.ZOLD, Figures.X),
    Card(Colors.ZOLD, Figures.ALSO),
    Card(Colors.ZOLD, Figures.FELSO),
    Card(Colors.ZOLD, Figures.KIRALY),
    Card(Colors.ZOLD, Figures.ASZ),

    Card(Colors.PIROS, Figures.VII),
    Card(Colors.PIROS, Figures.VIII),
    Card(Colors.PIROS, Figures.IX),
    Card(Colors.PIROS, Figures.X),
    Card(Colors.PIROS, Figures.ALSO),
    Card(Colors.PIROS, Figures.FELSO),
    Card(Colors.PIROS, Figures.KIRALY),
    Card(Colors.PIROS, Figures.ASZ)
]

class Player:
    def __init__(self, name, is_ai):
        self.name = name
        self.hand = []
        self.collected = []
        self.is_ai = is_ai

class Zsir:
    def __init__(self, players, human):
        self.players = players
        self.human = human
        self.current_player = 0
        self.num_players = len(players)
        self.deck = deck.copy()
        self.house = []
        shuffle(self.deck)
    
    def deal(self):
        for i in range(self.num_players):
            for j in range(4 - len(self.players[i].hand)):
                self.players[i].hand.append(self.deck.pop())

    def make_move(self, card):
        self.house.append(card)
        self.players[self.current_player].hand.remove(card)
        self.next_player()
        self.print_house()
        
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def print_house(self):
        for card in reversed(self.house):
            print(card)

    def ai_move(self):
        return choice(self.players[self.current_player].hand)
    
    def evaluate_game(self):
        pass