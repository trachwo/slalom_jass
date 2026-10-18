"""
Swiss Slalom-Jass Card Game.

'Jass' is the national card game of Switzerland. It's usually played with a
German deck of 36 cards, i.e. the suits 'Rose', 'Schilte', 'Eichle', 'Schelle',
and the ranks '6', '7', '8', '9', '10, 'Under', 'Ober', 'König', 'Ass'. But it
can also be played with a French deck. We use the French deck in this program,
since 'Hearts', 'Spades', 'Diamonds', and 'Clubs' can be easily displayed using
unicodes.

We have the following mapping from the German to the French deck:
    'Schelle'   => ♡    '6'     => '6'
    'Eichle'    => ♠    '7'     => '7'
    'Schilte'   => ♢    '8'     => '8'
    'Rosen'     => ♣    '9'     => '9'
                        '10'    => '10'
                        'Under' => 'J'
                        'Ober'  => 'Q'
                        'König' => 'K'
                        'Ass'   => 'A'

One of many Jass-variants is called Coiffeur-Jass (from French 'quoi faire'),
which is a trick-taking game for 4 players, where players sitting opposite of
each other are building a team.
The game is played over several rounds, where each round is played with a
different trump variant:
    - Eichle
    - Rosen
    - Schilten
    - Schellen
    - Obenabe (no trump, 'Ass' is the highest, '6' is the lowest card)
    - Undeufe (no trump, '6' is the highest, 'Ass' is the lowest card)
    - ...

Starting with the player to the right of the dealer (swiss card games are
played counterclockwise) players select one of the variants not played yet or
pass. If all 4 players pass the player to the right of the dealer is forced to
make a selection. As soon as a player selects a variant, this player plays the
1st card to the 1st trick. The player who wins the trick plays the 1st card to
the next trick, and so on.

'Slalom' is a variant, which is played without trump, but the rank order
alternates between 'Obenabe' (top down) and 'Undeufe' (bottom up). The player
selecting 'Slalom' has also to declare, if the 1st trick is played 'Obenabe' or
'Undeufe'. This also determines the card values for the whole round:

            +-----------------------+
            |        Points         |
            +-----------+-----------+
            | 'Obenabe' | 'Undeufe' |
            |   first   |   first   |
  +---------+-----------+-----------+
  | '6'     |     0     |    11     |
  | '7'     |     0     |     0     |
  | '8'     |     8     |     8     |
  | '9'     |     0     |     0     |
  | '10'    |    10     |    10     |
  | 'Under' |     2     |     2     |
  | 'Ober'  |     3     |     3     |
  | 'König' |     4     |     4     |
  | 'Ass'   |    11     |     0     |
  +---------+-----------+-----------+

The game itself is played as usual for trick taking games without trump, i.e.
players must follow the suit led, if possible. If a player has no cards of the
led suit, he may play any card.
Remember that card order alternates between tricks:

+----------+---+---+---+---+---+---+---+---+---+
| Trick    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
+----------+---+---+---+---+---+---+---+---+---+
| Obenabe  | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ |  
+----------+---+---+---+---+---+---+---+---+---+
| Undeufe  | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ |
+----------+---+---+---+---+---+---+---+---+---+

After the whole round has been played, the teams sum up the points for the
cards in their tricks (see table above). The team which has won the last trick
gets an addtitional 5 points.

"""

from collections import Counter
from copy import deepcopy
import json

from slalom_jass.cards import Suit, Rank, Card, Deck, SUIT_ORDER
from slalom_jass.game.player import Player, NOF_PLAYERS
from slalom_jass.game.info import GameInfo

# list of symbols exported if a script calls 'from game import *'
__all__ = [
    'GameState',
    'OBENABE_POINTS_ORDER',
    'UNDEUFE_POINTS_ORDER',
    'simulate_game',
    'finish_game',
]

NOF_TRICKS = 9          # Number of tricks per round

RANK_POINTS = {'Obenabe': {Rank.SIX: 0, Rank.SEVEN: 0, Rank.EIGHT: 8,
                           Rank.NINE: 0, Rank.TEN: 10, Rank.JACK: 2,
                           Rank.QUEEN: 3, Rank.KING: 4, Rank.ACE: 11},
               'Undeufe': {Rank.SIX: 11, Rank.SEVEN: 0, Rank.EIGHT: 8,
                           Rank.NINE: 0, Rank.TEN: 10, Rank.JACK: 2,
                           Rank.QUEEN: 3, Rank.KING: 4, Rank.ACE: 0}}

OBENABE_POINTS_ORDER = [Rank.SIX, Rank.SEVEN, Rank.NINE, Rank.JACK, Rank.QUEEN,
                        Rank.KING, Rank.EIGHT, Rank.TEN, Rank.ACE]
UNDEUFE_POINTS_ORDER = [Rank.ACE, Rank.SEVEN, Rank.NINE, Rank.JACK, Rank.QUEEN,
                        Rank.KING, Rank.EIGHT, Rank.TEN, Rank.SIX]

class GameState:
    """
    Game state for a single round of 'Slalom'.

    An implementation of 'Slalom' passes this game state to the corresponding
    agents (human or AI) to select a legal play (card played from hand). By
    applying this card play to the current state we get to the next state.
    This is repeated until the round is finished.

    State machine:
    --------------

    initialize: table = [],
                tricks = 0
                turns = 0
                next = dealer

     tricks |     turns   | action by next player
    --------+-------------+-----------------------------------------------------
      -1    |       0     | deals 9 cards to each player.
            |             | turns += 1
            |             | next = (next + 1) % 4
    --------+-------------+-----------------------------------------------------
      -1    |    1 - 4    |  selects:
            |             |     'Obenabe' or 'Undeufe':
            |             |             => obenabe = True or obenabe = False
            |             |             => tricks = 1
            |             |             => turns = 0
            |             |
            |             |      or 'Schiebe':
            |             |             => turns += 1
            |             |             => next = (next + 1) % 4
    --------+-------------+-----------------------------------------------------
      -1    |       5     | selects:
            |             |     'Obenabe' or 'Undeufe':
            |             |             => obenabe = True or obenabe = False
            |             |             => tricks = 1
            |             |             => turns = 0
    --------+-------------+-----------------------------------------------------
     0 - 8  |       0     | play any card from hand as leading card,
            |             | next = (next + 1) % 4
            |             | 
     0 - 8  |       1     | follow or play any card, next = (next + 1) % 4 
            |             |
     0 - 8  |       2     | follow or play any card, next = (next + 1) % 4
            |             |
     0 - 8  |       3     | follow or play any card, next = (next + 1) % 4
            |             |
     0 - 8  |       4     | determine winner of trick => next
            |             | table = [], tricks += 1, turns = 0
    --------+-------------+-----------------------------------------------------
       9    |       0     | game is over.
            |             | calculate score per player.
            |             | add +5 for next (winner of last trick)
            |             | calculate score per team.
    --------+-------------+-----------------------------------------------------

    Attributes:
        players (list):         list of players.
        tricks (int):           number of tricks played this round.
        turns (int):            player turn: trick -1   => 0-5.
                                             trick 0-9  => number of table cards. 
        table (list):           list of table cards in play order.
        next_player (int):      index of player playing next.
        obenabe (bool):         True => 'Obenabe', False = 'Undeufe'.
        info (GameInfo):        publicly known game info.
    """
    def __init__(self, players, tricks, turns, table, next_player, obenabe,
                 info):
        """
        Initializer.

        Args:
            players (list):         list of players.
            tricks (int):           number of tricks played this round.
            turns (int):            player turn: trick -1   => 0-5.
                                                 trick 0-9  => number of table cards. 
            table (list):           list of table cards in play order.
            next_player (int):      index of player playing next.
            obenabe (bool):         True => 'Obenabe', False = 'Undeufe'.
            info (GameInfo):        publicly known game info.
        """
        self.players = players              # list of players.
        self.tricks = tricks                # counting tricks this round.
        self.turns = turns                  # counting player turns per trick.
        self.table = table                  # cards played during current turn.
        self.next_player = next_player      # next player to play a card.
        self.obenabe = obenabe              # True => odd turns are played 'Obenabe'.
                                            #         and 'Obenabe' score. 
        self.info = info                    # card distribution info.

    def deal_cards(self):
        """
        Deal deck of cards to players.

        Each player gets 9 cards.
        """
        # create and shuffle deck of 36 cards ('2', '3', '4', and '5' removed)
        deck = Deck(remove=[Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE])
        deck.shuffle_cards()
        # dealer is next player (tricks = -1, turns = 0)
        # dealing starts with player to the right of the dealer
        p = (self.next_player + 1) % NOF_PLAYERS
        while len(deck.cards) > 0:
            # deal one card after another to players.
            card = deck.deal_card()
            self.players[p].get_card(card)
            # next player with wrap-around
            p = (p + 1) % NOF_PLAYERS
        # sort player hands
        for player in self.players:
            player.sort_hand()


    @classmethod
    def new_round(cls, dealer):
        """
        Create a new round of the game.

        Args:
            dealer (int):   players index of dealer. 

        Returns:
            GameState:      state of new round.
        """
        players = [Player(f"Player{i+1}") for i in range(NOF_PLAYERS)]
        tricks = -1
        turns = 0
        table = []
        next_player = dealer
        obenabe = False
        info = GameInfo()
        return GameState(players, tricks, turns, table, next_player, obenabe,
                         info)

    def start_round(self):
        """
        Deal cards and move to declaration phase.

        """
        # game must be in initial state: tricks = -1, turns = 0
        if self.tricks != -1:
            raise ValueError(f"Cannot start round in turn {self.turns}!")
        if self.turns != 0:
            raise ValueError(f"Cannot start round in turn {self.turns}")

        # dealer (next player) shuffles deck of 36 cards and deals 9 cards to
        # each player.
        self.deal_cards()
        self.next_player = (self.next_player + 1) % NOF_PLAYERS
        self.turns = 1      # next game state: tricks = -1, turns = 1

    def get_legal_declarations(self):
        """
        Get legal plays during declaration phase.
        
        While tricks = -1, turns = 1 - 4 legal plays are:
            - 'Obenabe'
            - 'Undeufe'
            - 'Schiebe'

        While tricks = -1, turns = 5 legal plays are:
            - 'Obenabe'
            - 'Undeufe'

        Returns:
            list:   list of legal plays during declaration phase.
        """
        if self.tricks >= 0 or self.turns == 0:
            raise ValueError(f"Cannot get declaration in state"
                             f" - tricks{self.tricks} turns:{self.turns}")
        if self.turns == 5:
            # all players passed => player following dealer has to select.
            return ['Obenabe', 'Undeufe']

        # during turns 1 - 4, each player may pass
        return ['Schiebe', 'Obenabe', 'Undeufe']

    def is_legal_card_play(self, card, suit_cnt):
        """
        Check if a card can be legally played in this state.

        turns = 0 (leading player) legal plays are:
            - any card in hand of player.

        turns 1 - 3 (following players) legal plays are:
            - any card in hand of player with same suit as 1st card played this
              trick.
            - any card in hand of player if he can't follow suit.

        Args:
            card (Card):        card to be played.
            suit_count (dict):  cards per suit in player's hand.

        Returns:
            bool:   True => card is legal play.  
        """
        if self.tricks == -1:
            # cannot play a card during declaration phase.
            return False

        if self.turns == 0:
            # 1st player => may play any card from his hand.
            return True

        if card.suit == self.table[0].suit:
            # following suit of leading card is allowed
            return True

        # if you can't follow suit => you can play any card
        return suit_cnt[self.table[0].suit] == 0

    def get_legal_card_plays(self):
        """
        Get cards, the next player can legally play.

        Returns:
            list:   cards that can be played.
        """
        hand = self.players[self.next_player].hand

        # count hand cards per suit
        suit_cnt = Counter([card.suit for card in hand])

        legal_plays = []
        for card in hand:
            if self.is_legal_card_play(card, suit_cnt):
                legal_plays.append(card)

        return legal_plays

    def get_legal_plays(self):
        """
        Get legal plays for current game state.

        If the game is in the declaration phase (tricks < 0), legal plays are
        declarations 'Schiebe', 'Obenabe', 'Undeufe', while in the trick phase
        (tricks >= 0) legal plays are cards which can be played by the next
        player.

        Returns:
            list:   declarations or cards.
        """
        if self.tricks < 0:
            # declaration phase => 'Schiebe', 'Obenabe', or 'Undeufe'.
            return self.get_legal_declarations()

        # trick phase => playable cards.
        return self.get_legal_card_plays()

    def show_table_cards(self):
        """
        Create string of cards played to the table.

        Returns:
            str:    string of cards played to the table.
        """
        table_str = [str(c) for c in self.table]
        return '  '.join(table_str)

    def higher_card_wins(self):
        """
        Find rank order depending on declaration and played trick.
        
        To win a trick a player must follow suit (play a card with the same
        suit as the 1st card in the trick) and with the corresponding rank.
        The rank order alternates between tricks. In 'Obenabe' rounds the 1st
        trick is won by the highest ranked card of the leading suit, while in
        'Undeufe' rounds it's won by the lowest ranked card. 

            Trick | Obenabe | Undeufe |
            ------+---------+---------+
               1  |  higher |  lower  |
               2  |  lower  |  higher |
               3  |  higher |  lower  |
               4  |  lower  |  higher |
               5  |  higher |  lower  |
               6  |  lower  |  higher |
               7  |  higher |  lower  |
               8  |  lower  |  higher |
               9  |  higher |  lower  |


        Returns:
            bool:   True => higher card wins, False => lower card wins.
        """
        # NOTE: this trick hasn't been counted yet => tricks + 1
        odd = (self.tricks + 1) % 2 == 1    # True  => 1, 3, 5, 7, 9
                                            # False => 2, 4, 6, 8

        if self.obenabe:
            # 'Obenabe' => higher card wins odd tricks
            # 'Obenabe' => lower card wins even tricks
            return odd
        else:
            # 'Undeufe' => lower card wins odd tricks
            # 'Undeufe' => higher card wins even tricks
            return not odd

    @classmethod
    def find_trick_winner(cls, table, obenabe):
        """
        Find card which currently wins the trick.

        To win a trick a player must follow suit (play a card with the same
        suit as the 1st card in the trick) and with the corresponding rank:
            'Obenabe', trick 1, 3, 5, 7, 9: higher rank
            'Obenabe', trick   2, 4, 6, 8:  lower rank
            'Undeufe', trick 1, 3, 5, 7, 9: lower rank
            'Undeufe', trick   2, 4, 6, 8:  higher rank

        NOTE: we need 'table' as argument, because the current state has still
              the table before the played card was applied.

        Args:
            table (list):   cards played during current turn.

        Returns:
            int:    table index of card currently winning the trick.
                    None => table is empty.
        """
        winner = None   # empty table => no winner
        if len(table) > 0:
            winner = 0      # 1st card wins by default
            # check other played cards
            for i in range(1, len(table)):
                if table[i].suit == table[0].suit:      # followed suit
                    if obenabe:     # Obenabe trick
                        if table[i] > table[winner]:    # higher card wins
                            winner = i
                    else:           # Undeufe trick
                        if table[i] < table[winner]:    # lower card wins
                            winner = i

        return winner

    def get_bock_cards(self):
        """
        Get a list of cards which are currently bock.

        Get from each suit the highest (obenabe bock) and lowest (undeufe bock)
        unplayed card.

        NOTE: this does not include the cards already on the table. I.e. the
              bock of the led suit must be compared to the card currently
              winning the trick.

        Returns:
            tuple:  list of lowest card per suit, list of highest card per suit.
        """
        lowest = []
        highest = []
        for suit in SUIT_ORDER:
            lo, hi = self.info.get_lowest_and_highest(suit)
            if lo is not None:  # None => no card left in this suit
                lowest.append(lo)
                highest.append(hi)

        return lowest, highest

    def apply_declaration(self, declaration):
        """
        Apply selected declaration.

        Args:
            declaration (str):  'Obenabe', 'Undeufe', or 'Schiebe'.

        Returns:
            GameState:          game state after selected declaration.
        """
        # make real copy of game state attributes
        tricks = self.tricks
        turns = self.turns
        players = deepcopy(self.players)
        next_player = self.next_player
        table = self.table[:]
        obenabe = self.obenabe
        info = deepcopy(self.info)

        if declaration == 'Schiebe':
            # ask next player for declaration
            turns += 1
            if turns > 5:
                # after all 4 players passed, the player to the right of the
                # dealer has to make a declaration.
                raise ValueError("Illegal 'Schiebe' action!")
            next_player = (next_player + 1) % NOF_PLAYERS
        elif declaration == 'Obenabe' or declaration == 'Undeufe':
            # player made a declaration => stays next player
            obenabe = True if declaration == 'Obenabe' else False
            # reset tricks and turns counters
            tricks = 0
            turns = 0
        else:
            raise ValueError(f"Illegal declaration {declaration}!")

        # return new game state
        return GameState(players, tricks, turns, table, next_player, obenabe,
                         info)

    def apply_card_play(self, card, verbose=False):
        """
        Add selected card to table.

        TODO: add new attribut winner => current winner of trick.
              add new attribut bock => winning card is bock.
              => helps SimpleBot making decisions.

        Args:
            card (Card):        card selected by agent from player's hand.
            verbose (bool):     True => print debug info.

        Returns:
            GameState:          game state after playing selected card.
        """
        # make real copy of game state attributes
        tricks = self.tricks
        turns = self.turns
        players = deepcopy(self.players)
        next_player = self.next_player
        table = self.table[:]
        obenabe = self.obenabe
        info = deepcopy(self.info)

        # update game info
        info.update(next_player, table, card, verbose)

        # move card from player to table
        c = players[next_player].play_card(card)
        table.append(c)

        # increment turns counter
        turns += 1

        # Every player had his turn:
        if turns == 4:
            # check if trick is complete
            if len(table) != NOF_PLAYERS:
                raise ValueError(f"Only {len(table)} cards in trick!")
            # get table index of card winning this trick
            winner = GameState.find_trick_winner(table,
                                                 self.higher_card_wins())
            # player of winning card is 1st player for next trick.
            # NOTE: current next_player has played table[3]
            next_player = (self.next_player + 1 + winner) % NOF_PLAYERS

            # add trick to winner's trick-list
            players[next_player].collect_trick(table)
            # => table is empty
            table = []
            tricks += 1
            turns = 0
        else:
            # next player, who has to play a card in this trick
            next_player = (next_player + 1) % NOF_PLAYERS

        # return new game state
        return GameState(players, tricks, turns, table, next_player, obenabe,
                         info)

    def apply_play(self, play):
        """
        Applies specified play to game state.

        If game state is in the declaration phase, we expect play to be
        'Schiebe', 'Obenabe', or 'Undeufe', while in the trick phase play
        should be a card in the hand of the next player.

        Args:
            play (str or Card):     play to be applied in this game state.

        Returns:
            GameState:      game state after play has been applied. 
        """
        if self.tricks < 0:
            # declaration phase
            if play not in ['Schiebe', 'Obenabe', 'Undeufe']:
                raise ValueError(f"{play} is not a legal declaration!")
            return self.apply_declaration(play)

        # trick phase
        if not isinstance(play, Card):
            raise ValueError(f"{play} is not a card!")
        return self.apply_card_play(play)

    def is_over(self):
        """
        Check if game is over.

        Returns:
            bool:   True => game is over.
        """
        if self.tricks == NOF_TRICKS:
            return True
        return False

    def count_points(self):
        """
        Count points per player.

        Each player gets points for the cards in his tricks:
            '6':  0 (Obenabe) or 11 (Undeufe),
            '7':  0,
            '8':  8,
            '9':  0,
            10': 10,
            'J':  2,
            'Q':  3,
            'K':  4,
            'A': 11 (Obenabe) or 0 (Undeufe).
        
        The player who won the last trick, gets an additional 5 points.

        Returns:
            list:   score = penalty points per player.
        """
        score = []
        mode = 'Obenabe' if  self.obenabe else 'Undeufe' 
        for p, player in enumerate(self.players):
            points = 0
            # flatten list of tricks to list of cards
            flat_tricks = [card for trick in player.tricks for card in trick]
            # sum up point cards
            for card in flat_tricks:
                points += RANK_POINTS[mode][card.rank]

            if p == self.next_player:
                # this player has won the last trick
                points += 5

            score.append(points)

        return score

    def print_state(self):
        """
        Show game state.
        """
        for i, player in enumerate(self.players):
            if i == self.next_player:
                prefix = '* '
            else:
                prefix = '  '
            print(f"{prefix} {player.name}: {player.show_hand()}")


    def clone(self):
        """
        Make a clone of the current game state.

        Makes a real copy of the current game state, i.e. we can apply actions
        to this clone without changing the original game state. The clone is
        used in MTCS to follow a game state from node to node in the SELECTION
        phase and finally to the terminal state in the SIMULATION phase.

        Returns:
            GameState:      clone of current game state.
        """
        # make a real (deep) copy of the players list
        players = deepcopy(self.players)
        # make a real (deep) copy of the game info
        info = deepcopy(self.info)
        tricks = self.tricks                    # tricks played
        turns = self.turns                      # turns played in trick
        next_player = self.next_player          # next player to play
        table = self.table[:]                   # cards on table
        obenabe = self.obenabe                  # 'Obenabe' flag

        # create clone of this game state
        return GameState(players, tricks, turns, table, next_player, obenabe,
                         info)

    def clone_and_randomize(self):
        """
        Make a clone of the current game state with randomized opponent cards.

        Makes a real copy of the current game state, i.e. we can apply actions
        to this clone without changing the original game state. The clone is
        used in ISMTCS to follow a game state from node to node in the SELECTION
        phase and finally to the terminal state in the SIMULATION phase.
        Jass is a game with imperfect information, i.e. the agent who uses
        this state clone with SO-ISMCTS to find his best play, does only know
        his own cards, but not the cards in the hands of the other players.
        Therefore, SO-ISMCTS uses a different random distribution of other
        player's cards (DETERMINISATION) for each rollout. Information gathered
        in previous turns of the game (GameInfo), can be used for this
        redistribution (e.g. if a player previously could not follow a leading
        suit, he will not get cards of this suit during redistribution).

        Returns:
            GameState:      clone of current game state.
        """
        # make a real (deep) copy of the players list
        players = deepcopy(self.players)
        # make a real (deep) copy of the game info
        info = deepcopy(self.info)
        tricks = self.tricks                    # tricks played
        turns = self.turns                      # turns played in trick
        next_player = self.next_player          # next player to play
        table = self.table[:]                   # cards on table
        obenabe = self.obenabe                  # 'Obenabe' flag

        # we make this clone to use SO-ISMCTS for play selection for the next
        # player, i.e. we know the next player's cards, but have to
        # redistribute the cards of the other players.
        info.determinize(players, next_player, False)
        # create clone of this game state
        return GameState(players, tricks, turns, table, next_player, obenabe,
                         info)

    def serialize(self):
        """
        Convert GameState object to dictionary.

        Used for serialization into JSON-string.

        Returns:
            dict:   game state.
        """
        state = {}
        state['players'] = [player.serialize() for player in self.players]
        state['tricks'] = self.tricks
        state['turns'] = self.turns
        state['table'] = [card.serialize() for card in self.table]
        state['next_player'] = self.next_player
        state['obenabe'] = self.obenabe
        state['info'] = self.info.serialize()
        return state

    def save(self, filename):
        """
        Save game state to file.

        Args:
            filename (str):     filename.
        """
        # convert GameState object into a dictionary
        data = self.serialize()

        # write data to json-file.
        if not filename.endswith('.json'):
            raise ValueError (
                "Filename must have extension '.json' => json-file!")

        json_str = json.dumps(data, indent=4)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)

    def deserialize(self, state):
        """
        Load GameState object from serialized GameState.

        Args:
            state (dict):   serialized GameState object.
        """
        # get players
        self.players = []
        for p in state['players']:
            player = Player(p['name'])
            player.deserialize(p)
            self.players.append(player)

        self.tricks = state['tricks']
        self.turns = state['turns']
        self.table = [Card(Suit(c['suit']), Rank(c['rank']))
                      for c in state['table']]

        self.next_player = state['next_player']
        self.obenabe = state['obenabe']
        self.info = GameInfo()
        self.info.deserialize(state['info'])

    def load_string(self, json_string):
        """
        Load GameState from JSON-string.

        Args:
            json_string (str):      json-string with serialized GameState.
        """
        # get serialized GameState from JSON-string.
        data = json.loads(json_string)

        # convert serialized GameState back to GameState object.
        self.deserialize(data)

    def load_file(self, filename):
        """
        Load game state from file.

        Args:
            filename (str):     filename.
        """
        # check filename.
        if not filename.endswith('.json'):
            raise ValueError (
                "Filename must have extension '.json' => json-file!")

        # load serialized GameState from json-file.
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # convert serialized GameState back to GameState object.
        self.deserialize(data)


def simulate_game(agent1, agent2, agent3, agent4, dealer=3, verbose=False):
    """
    Let 4 agents play a single round of Slalom-Jass against each other.

    Args:
        agent1 (Agent):     bot playing Player1.
        agent2 (Agent):     bot playing Player2.
        agent3 (Agent):     bot playing Player3.
        agent4 (Agent):     bot playing Player4.
        dealer (int):       this round's dealer.
        verbose (bool):     True => show details.

    Returns:
        tuple:     points per agent.
    """
    # map player index to agent
    agent_map = {0: agent1, 1: agent2, 2: agent3, 3: agent4}

    # create gamestate for new round
    # with Player4 as dealer Player1 has to declare first.
    game = GameState.new_round(dealer)
    # deal cards and determine starting player
    game.start_round()
    if verbose:
        # print cards per player
        game.print_state()
        print()

    # play 9 tricks of one round.
    while not game.is_over():
        # ask next player's agent to select play (declaration or card)
        legal_plays = game.get_legal_plays()
        legal_plays_str = '  '.join([str(p) for p in legal_plays])
        play = agent_map[game.next_player].select_play(game)
        if verbose:
            if game.tricks < 0:
                # declaration phase
                if game.turns == 1:
                    print("   --------")    # 1st player to declare
                print(f"   Player{game.next_player + 1}: {legal_plays_str:<48}"
                      f" => Declaration: ", end='')
            else:
                if game.turns == 0:
                    print("   --------")    # 1st player to play card
                print(f"   Player{game.next_player + 1}: {legal_plays_str:<48}"
                      f" => Trick: ", end='')
            if len(game.table) == 0:
                # 1st card
                print(f"{str(play)}")
            else:
                # add to table cards
                print(f"{game.show_table_cards()}  {str(play)}")
        # apply selected card to game state
        game = game.apply_play(play)

        # save status for game info test.
#        if game.tricks == 5:
#            game.save('data/info_test.json')

    # calculate points per player
    points = game.count_points()

    if verbose:
        # print detailed results
        print("--------------------------------------------------------------"
              "--------------------------------------")
        print(f"   {'Obenabe' if game.obenabe else 'Undeufe'}:")
        print("   --------")
        for p, player in enumerate(game.players):
            print(f"   {player.name}: {points[p]:>3} -"
                  f" {player.show_tricks()}", end='')
            if p == game.next_player:
                print("  + 5")   # for last trick
            else:
                print()
    return points

def finish_game(game, agent1, agent2, agent3, agent4, verbose=False):
    """
    Let 4 agents finish a round of Slalom-Jass from a specified state.

    Args:
        game (GameState):   current state of the game.
        agent1 (Agent):     bot playing Player1.
        agent2 (Agent):     bot playing Player2.
        agent3 (Agent):     bot playing Player3.
        agent4 (Agent):     bot playing Player4.
        verbose (bool):     True => show details.

    Returns:
        tuple:     points per agent.
    """
    # map player index to agent
    agent_map = {0: agent1, 1: agent2, 2: agent3, 3: agent4}

    # finish the game from this game state
    while not game.is_over():
        # ask next player's agent to select play (declaration or card)
        legal_plays = game.get_legal_plays()
        legal_plays_str = '  '.join([str(p) for p in legal_plays])
        play = agent_map[game.next_player].select_play(game)
        if verbose:
            if game.tricks < 0:
                # declaration phase
                if game.turns == 1:
                    print("   --------")    # 1st player to declare
                print(f"   Player{game.next_player + 1}: {legal_plays_str:<48}"
                      f" => Declaration: ", end='')
            else:
                if game.turns == 0:
                    print("   --------")    # 1st player to play card
                print(f"   Player{game.next_player + 1}: {legal_plays_str:<48}"
                      f" => Trick: ", end='')
            if len(game.table) == 0:
                # 1st card
                print(f"{str(play)}")
            else:
                # add to table cards
                print(f"{game.show_table_cards()}  {str(play)}")
        # apply selected card to game state
        game = game.apply_play(play)

    # calculate points per player
    points = game.count_points()

    if verbose:
        # print detailed results
        print("--------------------------------------------------------------"
              "--------------------------------------")
        print(f"   {'Obenabe' if game.obenabe else 'Undeufe'}:")
        print("   --------")
        for p, player in enumerate(game.players):
            print(f"   {player.name}: {points[p]:>3} -"
                  f" {player.show_tricks()}", end='')
            if p == game.next_player:
                print("  + 5")   # for last trick
            else:
                print()
    return points


def main():
    """
    GameState tests.
    """
    # new round with Player1 as dealer.
    game = GameState.new_round(0)

    # deal cards to players
    game.start_round()
    game.save("saved_game_state.json")
    game.load_file("saved_game_state.json")
    print("-------------------")
    print(f"Tricks:      {game.tricks}")
    print(f"Turns:       {game.turns}")
    print(f"next_player: {game.next_player}")
    print(f"obenabe:     {game.obenabe}")
    print("c2p_map:")
    print("--------")
    game.info.show_c2p_map()

    print("\n-------------------------------------------------")
    print("GameState:")
    print("----------")
    game.print_state()
    print("-------------------------------------------------")

    # ask players for declaration.
    while game.tricks < 0:
        player = game.players[game.next_player]
        declarations = game.get_legal_declarations()
        dec_str = [f"{i}:{declarations[i]}" for i in range(len(declarations))]
        dec_str = '  '.join(dec_str)
        while True:
            sel = input(f"{player.name} select: {dec_str} ? ")
            try:
                if int(sel) >= 0 and int(sel) < len(declarations):
                    break
            except ValueError:
                continue    # wait for player to make valid choice.
        # apply selected declaration to game state.
        game = game.apply_declaration(declarations[int(sel)])

    print("-------------------")
    print(f"Tricks:      {game.tricks}")
    print(f"Turns:       {game.turns}")
    print(f"next_player: {game.next_player}")
    print(f"obenabe:     {game.obenabe}")
    print("-------------------")

    # play all turns with human input.
    while not game.is_over():
        # print game state => player hands, table
        mode = 'Obenabe' if game.higher_card_wins() else 'Undeufe'
        print(f"\nTricks:{game.tricks} Turns:{game.turns} {mode}")
        print("-------------------------------------------------")
        game.print_state()
        print()
        # print table before play
        print(f"Table: {game.show_table_cards()}")
        # ask next player to play a card
        player = game.players[game.next_player]
        plays = game.get_legal_card_plays()
        plays_str = [f"{i}:{plays[i]}" for i in range(len(plays))]
        plays_str = '  '.join(plays_str)
        # ask human agent for input
        while True:
            sel = input(f"{player.name} select card: {plays_str} ? ")
            try:
                if int(sel) >= 0 and int(sel) < len(plays):
                    break
            except ValueError:
                continue
        # print table after play
        print(f"Table: {game.show_table_cards()}  {str(plays[int(sel)])}")
        # apply selected card to game state
        game = game.apply_card_play(plays[int(sel)])


def info_test():
    """
    Test game info module.
    """
    print("\n### GameInfo test ###\n")
    # load game from file
    game = GameState.new_round(3)
    game.load_file('data/info_test.json')

    # print loaded state
    game.print_state()
    print()

    # show 'cards to players' map.
    game.info.show_c2p_map()
    print()

    # find lowest and highest card of Diamonds
    lowest, highest = game.info.get_lowest_and_highest(Suit.DIAMONDS)
    print(f"lowest: {str(lowest)}   highest: {str(highest)}")
    print()

    # find bock cards (obenabe or undeufe)
    lowest, highest = game.get_bock_cards()
    print(f"undeufe bock-cards:  {'  '.join([str(c) for c in lowest])}") 
    print(f"obenabe bock-cards:  {'  '.join([str(c) for c in highest])}") 
    print()

    # find cards still in the game which are lower than 9♣
    lower = game.info.get_lower_or_higher(Card(Suit.CLUBS, Rank.NINE), False)
    print(f"lower than 9♣ :  {'  '.join([str(c) for c in lower])}") 
    # find cards still in the game which are higher than 9♣
    higher = game.info.get_lower_or_higher(Card(Suit.CLUBS, Rank.NINE), True)
    print(f"higher than 9♣ :  {'  '.join([str(c) for c in higher])}") 
    print()

    # redistribute cards
    new_game = game.clone_and_randomize()
    new_game.print_state()


if __name__ == '__main__':
    # !!!NOTE!!!
    # To avoid ModuleNotFoundError start it from '~/Projects/slalom_jass/src' with
    # python3 -m slalom_jass.game.game
    info_test()
    main()
