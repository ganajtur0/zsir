from math import ceil
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

class EndResult(Enum):
    LOST = 0
    DRAW = 1
    WON = 2

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
        self.score = 0
        self.hand = []
        self.collected = []
        self.is_ai = is_ai
        self.stash = []

class Zsir:
    def __init__(self, players, human, first_player):
        # DEBUG
        # self.game_over = True
        self.game_over = False
        self.players = players
        self.human = human
        self.current_player = first_player
        self.first_player = first_player
        self.num_players = len(players)
        self.deck = deck.copy()
        self.house = []
        self.last_round_winner = -1
        self.round = 0
        self.let_it_go_decision = False
        shuffle(self.deck)

    def deal(self):
        if (len(self.deck) == 0 and 
            sum([len(p.hand) for p in self.players]) == 0):
            print("Vége")
            self.game_over = True
            return
        decklen_half = ceil(len(self.deck)/2)
        for i in range(self.num_players):
            for _ in range(min(4 - len(self.players[i].hand),
                               decklen_half)):
                self.players[i].hand.append(self.deck.pop())

    def make_move(self, card):
        self.house.append(card)
        self.players[self.current_player].hand.remove(card)
        
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players
        if self.current_player == self.first_player:
            return True
        return False

    def print_house(self):
        for card in reversed(self.house):
            print(card)

    def ai_move(self, can_let_go):
        if len(self.house) > 0:
            for card in self.players[self.current_player].hand:
                if (card.figure == self.house[0].figure or
                    card.figure == Figures.VII):
                    return card
            if can_let_go:
                return None
        return choice(self.players[self.current_player].hand)
    
    def can_do_it(self, player):
        for card in self.players[player].hand:
            if (card.figure == self.house[0].figure
                or card.figure == Figures.VII):
                return True
        return False
    
    # calculates scores, returns state of game
    def evaluate_game(self):
        for player in self.players:
            for card in player.stash:
                if (card.figure == Figures.X or
                    card.figure == Figures.ASZ):
                    player.score += 10
        score = self.players[0].score
        draw = True
        for player in self.players[1:]:
            if player.score != score:
                draw = False
                break
        if draw:
            self.players[self.current_player].score += 1
        player_score = self.players[self.human].score
        for i, player in enumerate(self.players):
            if i != self.human:
                if player.score > player_score:
                    return EndResult.LOST
        return EndResult.WON
    
    def restart(self):
        self.game_over = False
        self.deck = deck.copy()
        self.first_player = self.human
        self.current_player = self.first_player
        self.house = []
        self.last_round_winner = -1
        self.round = 0
        self.let_it_go_decision = False
        shuffle(self.deck)
        self.deal()
        for player in self.players:
            player.stash = []
            player.score = 0

    def evaluate_round(self):
        takes_trick = self.first_player
        for i in range(0, len(self.house)):
            if (
                self.house[i].figure == self.house[0].figure or
                self.house[i].figure == Figures.VII
                ):
                takes_trick = (self.first_player + i%self.num_players) % self.num_players
        #if (len(self.house) == self.num_players
        if (True
            and takes_trick != self.first_player
            and not self.let_it_go_decision
            and self.can_do_it(self.current_player)):
            return True
        self.let_it_go_decision = False
        self.print_house()
        print(f"A kört {self.players[takes_trick].name} játékos viszi")
        self.players[takes_trick].stash += self.house
        self.house = []
        self.first_player = takes_trick
        self.current_player = self.first_player
        self.last_round_winner = takes_trick   
        self.deal() 
        return False