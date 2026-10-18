"""
Game info collector.

Collects publicly known information about the card distribution.

NOTE: testing is done in game.py to avoid problems due to circular imports.
"""
from random import choice
from copy import deepcopy

from slalom_jass.cards import Suit, Rank, Card, RANK_ORDER, SUIT_ORDER
from slalom_jass.game import NOF_PLAYERS


# list of symbols exported if a script calls 'from game_info import *'
__all__ = [
    'GameInfo',
]

# 'Jass' is played with 36 cards 
JASS_RANKS = [Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK,
              Rank.QUEEN, Rank.KING, Rank.ACE]


class GameInfo:
    """
    Information publicly known about card distribution.

    Keeps track of cards not played yet and which players may hold them.
    For each card in the game we have a list of possible players holding it.
    If a card is played, this list is emptied. If a player cannot follow suit,
    we remove this player from all cards of this suit, which are still in the
    game.
    At any point of the game, we can use this plublicly known information to
    create randomly generated card distributions for game simulations (e.g. for
    Information Set Monte Carlo Tree Search).

    Attributes:
        c2p_map (dict):     maps each card to a list of players maybe holding
                            this card.
        p2c_map (list):     maps each opponent player to a list of unobserved
                            cards which could be in this player's hand.
        pool (list))        pool of unobserved cards (not in our hand).


    """
    def __init__(self):
        # create a dictionary mapping each card to a list of players maybe
        # holding this card.
        # NOTE: we do this without an observer in mind, i.e. every player with
        #       perfect memory could have this information.
        self.c2p_map = {}
        # at the start of the game each card could be in any player's hand.
        # e.g. self.c2p[Suit.HEARTS][Rank.QUEEN] = [0, 1, 2, 3]
        #       => each of the 4 players could have the Q♡ in hand.
        for suit in Suit:
            self.c2p_map[suit.value] = {}
            for rank in JASS_RANKS:
                self.c2p_map[suit.value][rank.value] = list(range(NOF_PLAYERS))

        # list of info records per other (than observer) player.
        self.p2c_map = []

        # pool of unobserved cards (= cards in the hands of other players)
        self.pool = []

    def serialize(self):
        """
        Convert GameInfo object to dictionary.

        Used for serialization into JSON-string.

        Returns:
            dict:   game info.
        """
        return {'c2p_map': self.c2p_map}

    def deserialize(self, state):
        """
        Load GameInfo object from serialized GameInfo.

        Args:
            state (dict):   serialized GameInfo object.
        """
        self.c2p_map = {}
        for suit in  state['c2p_map']:
            self.c2p_map[int(suit)] = {}
            for rank in state['c2p_map'][suit]:
                self.c2p_map[int(suit)][int(rank)]\
                      = state['c2p_map'][suit][rank]

    def show_c2p_map(self):
        """
        Print c2p_map.
        """
        for suit in SUIT_ORDER:
            for rank in JASS_RANKS:
                candidates = self.c2p_map[suit.value][rank.value]
                if len(candidates) > 0:
                    print(f"{str(Card(suit, rank)):>3} : {candidates}")

    def remove_from_suit(self, next_player, suit, verbose=False):
        """
        Remove player from all lists of this suit in c2p_map.

        Args:
            next_player (int):  index of next player in state.players.
            suit (Suit):        suit next player has to be removed from.
        """
        for rank in JASS_RANKS:
            try:
                self.c2p_map[suit.value][rank.value].remove(next_player)
            except ValueError:
                # player already removed before => ignore
                continue

        if verbose:
            print(f"### remove P{next_player + 1} from {suit}")
            self.show_c2p_map()

    def update(self, next_player, table, card, verbose=False):
        """
        Update c2p_map after next player played a card.

        Args:
            next_player (int):      index of next player in player's list.
            table (list):           list of cards already played this turn.
            card (Card):            card played by next player.
            verbose (bool):         True => print debug info.
        """
        if len(table) > 0:
            # next player plays 2nd, 3rd, or 4th
            if card.suit != table[0].suit:
                # player doesn't follow leading suit
                # => player is out of leading suit
                self.remove_from_suit(next_player, table[0].suit, verbose)

        # in each case the played card is out of the game now
        # => empty this cards player list
        self.c2p_map[card.suit.value][card.rank.value] = []

        # also reset the pool of unknown cards
        # => determinisation() method has to create a new pool as 1st step.
        self.pool = []

    def map_pool_cards(self, players, observer):
        """
        Map unobserved cards to possible players.

        We throw all cards not held by the observer (= agent using this game
        info) into a pool of unobserved cards, while remembering for each of
        these players the number of cards he had originally in his hand.
        Next we use the c2p_map to build for each of these (no-observer)
        players a list of indices referencing the cards in the pool, which
        represents the cards available to this player during determinisation
        (= re-distribution of unobserved cards to opponent players).

        NOTE: this is done from the point of view of an observer (player agent),
              which knows his own cards, but does not know the hands of the
              other players.

        players (list):     players (Player) in a game of 'Jass'.
        observer (int):     index of observer in list of players.
        """
        # create p2c_map for other (than the observer) players, while adding
        # their cards to the pool of unobserved cards.
        for p in range(NOF_PLAYERS):
            if p == observer:
                continue    # skip the observer
            # create p2c_map record
            # => [player, size_of_hand, available cards, selected cards]
            self.p2c_map.append([p, len(players[p].hand), [], []])
            # add player's hand to pool
            self.pool = self.pool + players[p].hand

        # sort cards in pool
        self.pool = sorted(self.pool, key=lambda x: (SUIT_ORDER.index(x.suit),
                                                     RANK_ORDER.index(x.rank)))

        # make a deep copy of the cards->players map, because we change it
        # while building the player records.
        c2p_map = deepcopy(self.c2p_map)

        # for each of the other (than observer) players, create a list of
        # indices referencing the pool cards which could be in their hands.
        for i, c in enumerate(self.pool):
            # loop through cards in pool.
            for rec in self.p2c_map:
                # loop through (other) players records.
                if observer in c2p_map[c.suit.value][c.rank.value]:
                    # the observer already has all his cards => remove him
                    c2p_map[c.suit.value][c.rank.value].remove(observer)
                if rec[0] in c2p_map[c.suit.value][c.rank.value]:
                    # player could hold this card => add index to his list of
                    # available cards.
                    if len(c2p_map[c.suit.value][c.rank.value]) == 1:
                        # only player who can hold this card
                        # => add it directly to his selected cards == 2
                        rec[3].append(i)
                    else:
                        # other players could hold this card
                        # => add it to available cards
                        rec[2].append(i)

    def show_unobserved_cards(self, players, observer):
        """
        Print unobserved cards per player.
        
        Args:
            players (list):     list of players.
            observer (int):     index of observer.
        """
        if not self.pool:
            # make sure the pool of unobserved cards exists.
            self.map_pool_cards(players, observer)

        # print available cards per player
        for rec in self.p2c_map:
            print(f"Player{rec[0]+1}: {rec[1]} -"
                  f" {'  '.join([str(self.pool[c]) for c in rec[2]])}")

    def determinize(self, players, observer, verbose=False):
        """
        Redistribute unobserved cards for DETERMINISATION phase.

        Jass is not a deterministic game, i.e. a player only knows his own
        hand cards and what is publicly known about the cards of the other
        players (e.g. suits they couldn't follow).
        To use Monte Carlo Tree Search (MCTS) in a non-deterministc game, we
        use determinisation to convert it into a deterministic game.
        I.e. before each rollout we assume a fixed distribution of unobserved
        cards (= cards not in the hand of the observer) using the publicly
        known information (suits not followed etc.)
        In a 1st step we have to collect all unobserved cards and map them to
        players who could possibly hold them. This has to be done only once per
        tree search using the map_pool_cards() method.
        In the 2nd step we redistribute the unobserved cards to possible
        holders, which has to be done before each rollout.
        Since we change the map of unobserved cards during redistribution, we
        make a deep copy in each rollout. Then we let each of the players other
        than the observer in turn select a cards from their lists of available
        cards, until they have filled up their hands to the original sizes. But
        we have to avoid distribution deadlocks, e.g. if we have the following
        unobserved cards map for a state where Player1 is the observer
        (NOTE: example was made for a card game using all 52 cards):

        pool: 6♢ 7♢ 9♢ 5♡ 6♡ 8♡ 9♡ 10♡ J♡ Q♡ 3♠ 5♠
        Player2 size:4  available:[3, 4, 5, 6, 7, 8, 9] selected: []
        Player3 size:4  available:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] selected: []
        Player4 size:4  available:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] selected: []

        we let the opponents of the observer randomly select cards until we get
        to the following situation:

        pool: 6♢ 7♢ 9♢ 5♡ 6♡ 8♡ 9♡ 10♡ J♡ Q♡ 3♠ 5♠
        Player2 size:4  available:[3] selected: [7, 4, 8]
        Player3 size:4  available:[1, 2, 3, 10] selected: [9, 0, 6]
        Player4 size:4  available:[1, 2, 3, 10] selected: [5, 11]

        Player2 has only 1 possibility left to fill his hand (3 => 5♡) but it
        is Player4's turn to select a card. If Player4 selects 3, Player2 can
        no longer fill his hand to 4 cards, i.e. we have a deadlock. Therefore,
        we use the following recipe to avoid deadlocks:
            - Player (in turn) randomly selects a card from its available
              cards list.
            - Check if another player with this card in its available card list
              is at his minimum of available cards (i.e. he needs all cards in
              his available cards list to fill up his hand). If this is the
              case, skip the selecting player (don't let him take this card) and
              continue with the next player.
            - No deadlock => add the selected card to this players selected
              cards list and remove it from the available cards list of all
              players.

        NOTE: before we start distributing the pool cards, we also have to move
              cards which are only available for one player from his available to
              his selected list. Otherwise, selecting cards which also can be
              selected by other players before selecting cards exclusive to
              him, could also cause a deadlock.

        After all pool card indices have been distributed to the players other
        than the observer, we add the actual cards at these indices to the
        hands of these players.

        Args:
            players (list):     list of players.
            observer (int):     index of observer.
            verbose (bool):     True => show details of distribution process.
        """
        def is_deadlock():
            """
            Check if taking a card causes a distribution deadlock.

            Returns:
                bool:   True => pidx selecting cidx causes a deadlock.

            """
            for r in p2c:
                if r[0] == p2c[pidx][0]:
                    continue    # skip selecting player
                if r[1] - len(r[3]) == len(r[2]) and cidx in r[2]:
                    # player has exactly so many available cards (including the
                    # card selected by another player) as he needs to fill up
                    # his hand to the original size, if the selected card is
                    # removed from his available cards, we will have a deadlock.
#                    print(f"### P{p2c[pidx][0] + 1} taking {cidx} causes a"
#                          f" deadlock for P{r[0]}")
                    return True
            return False

        if not self.pool:
            # once per tree search create the pool of unobserved cards.
            self.map_pool_cards(players, observer)

        # make a deep copy of the pool card map (because cards will be removed
        # from the list of available cards during redistribution).
        p2c = deepcopy(self.p2c_map)

        # calculate then number of already distributed cards (cards mapped to
        # only one player).
        distributed = 0     # number of distributed cards
        for rec in p2c:
            distributed += len(rec[3])

        pidx = 0            # index of next record in p2c
        while distributed < len(self.pool):
            # get pool card map record for current player
            # rec[0] => players index.
            # rec[1] => original size of hand.
            # rec[2] => list of cards (pool-indices) available to this player.
            # rec[3] => list of already selected cards (pool-indices).
            rec = p2c[pidx]
            if verbose:
                print(f"\nPlayer{rec[0]+1}: size:{rec[1]} available:{rec[2]} selected:{rec[3]}")

            if rec[1] - len(rec[3]) == 0:
                # skip player if he already has all needed cards.
                pidx = (pidx + 1) % len(p2c)
                continue

            # let this player randomly select one of the available cards
            cidx = choice(rec[2])
            if verbose:
                print(f"Player{rec[0]+1} selects {cidx}")
            if is_deadlock():
                if verbose:
                    print("#### deadlock ###")
                # taking card causes a deadlock
                # => don't take it, skip this player, let others chose first
                # if this is the only choice left, raise an exception
                if len(rec[2]) == 1:
                    raise ValueError(f"P{pidx + 1}: Not enough cards available!")

                # skip to next player
                pidx = (pidx + 1) % len(p2c)
                continue

            # no deadlock add it to the selected cards
            rec[3].append(cidx)
            distributed += 1

            # remove selected card from all available lists
            for rc in p2c:
                if cidx in rc[2]:
                    rc[2].remove(cidx)

            # increment index to next player
            pidx = (pidx + 1) % len(p2c)

        # add cards at selected indices to player hands
        for rec in p2c:
            players[rec[0]].hand = []   # start with empty hand
            for cidx in rec[3]:
                players[rec[0]].hand.append(self.pool[cidx])
            players[rec[0]].sort_hand()

    def get_lowest_and_highest(self, suit):
        """
        Get highest and lowest card of a suit which is still in the game.

        Args:
            suit (Suit):    card suit.

        Returns:
            tuple:      lowest card, highest card of specified suit,
                        or None, None if no card left in suit.   
        """
        # get ranks of cards with specified suit which are still in the game
        ranks = [r for r, p in self.c2p_map[suit.value].items() if len(p) > 0]
        if len(ranks) > 0:
            return Card(suit, Rank(ranks[0])), Card(suit, Rank(ranks[-1]))
        else:
            # no cards left in this suit
            return None, None

    def get_2nd_lowest_and_2nd_highest(self, suit):
        """
        Get 2nd highest and 2nd lowest card still in the game for a suit.

        Args:
            suit (Suit):    card suit.

        Returns:
            tuple:      2nd lowest card, 2nd highest card of specified suit.
        """
        # get list of cards with the specified suit which are still in the game
        ranks = [r for r, p in self.c2p_map[suit.value].items() if len(p) > 0]
        if len(ranks) > 1:
            return Card(suit, Rank(ranks[1])), Card(suit, Rank(ranks[-2]))
        else:
            # 1 or less cards left in this suit
            return None, None

    def get_lower_or_higher(self, card, higher):
        """
        Get cards lower or higher than the specified card.

        Get all non-played cards with same suit as the specified card, which
        are either higher or lower than this card.

        Args:
            card (Card):    reference card.
            higher (boo):   True => higher cards, False => lower cards.

        Returns:
            list:   list of higher or lower cards.
        """
        # get suit of specified card
        suit = card.suit
        # get ranks of cards with specified suit which are still in the game
        ranks = [r for r, p in self.c2p_map[suit.value].items()
                 if len(p) > 0]
        if higher:  # cards higher than the specified card
            return [Card(suit, Rank(r)) for r in ranks
                    if r > card.rank.value]
        else:       # cards lower than the specified card
            return [Card(suit, Rank(r)) for r in ranks
                    if r < card.rank.value]
