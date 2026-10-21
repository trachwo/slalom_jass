"""
Playing cards.

Implementation of playing cards (french deck of 52 cards without jokers).

We use the unicodes for 'CLUBS', 'DIAMONDS', 'HEARTS', and 'SPADES' for string
representation.

NOTE: You may have to configure a font able to display these unicodes in your
      terminal.
"""

from enum import Enum
from random import shuffle

# list of symbols exported if a script calls 'from cards import *'
__all__ = [
    'Suit',
    'Rank',
    'RANK_ORDER',
    'SUIT_ORDER',
    'Card',
    'Deck'
]

class Suit(Enum):
    """
    Card Suits.
    """
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4


class Rank(Enum):
    """
    Card Ranks.
    """
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

# rank order (2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A)
RANK_ORDER = [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
              Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN,
              Rank.KING, Rank.ACE]
# suit order (Clubs, Diamonds, Hearts, Spades)
SUIT_ORDER = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]


class Card:
    """
    Playing card.

    Attributes:
        suit (Suit):    Suit of card.
        rank (Rank):    Rank of card.
    """
    def __init__(self, suit, rank):
        """
        Initializer.

        Args:
            suit (Suit):    Suit of card.
            rank (Rank):    Rank of card.
        """
        self.suit = suit
        self.rank = rank

    def __str__(self):
        """
        Get string representing card.

        Returns:
            str:    string representation of card.
        """
        suits = {Suit.CLUBS: '\u2663',
                 Suit.DIAMONDS: '\u2662',
                 Suit.HEARTS: '\u2661',
                 Suit.SPADES: '\u2660'}
        ranks = {Rank.ACE: 'A',
                 Rank.TWO: '2',
                 Rank.THREE: '3',
                 Rank.FOUR: '4',
                 Rank.FIVE: '5',
                 Rank.SIX: '6',
                 Rank.SEVEN: '7',
                 Rank.EIGHT: '8',
                 Rank.NINE: '9',
                 Rank.TEN: '10',
                 Rank.JACK: 'J',
                 Rank.QUEEN: 'Q',
                 Rank.KING: 'K'}
        return f"{ranks[self.rank]}{suits[self.suit]}"

    def __repr__(self):
        """
        Get debugger representation of card.

        Returns:
            str:    rank and suit of card.
        """
        return f"<Card {self.rank} of {self.suit}>"

    def __lt__(self, other):
        """
        Check if this card is less than other card.

        Args:
            other (Card):   other card.

        Returns:
            bool:   True => this card is less than other card.
        """
        if RANK_ORDER.index(self.rank) < RANK_ORDER.index(other.rank):
            return True
        if RANK_ORDER.index(self.rank) == RANK_ORDER.index(other.rank):
            return SUIT_ORDER.index(self.suit) < SUIT_ORDER.index(other.suit)
        return False

    def __eq__(self, other):
        """
        Check if this card is equal to other card.

        Args:
            other (Card):   other card.

        Returns:
            bool:   True => this card is equal to other card.
        """
        return self.suit == other.suit and self.rank == other.rank

    def __gt__(self, other):
        """
        Check if this card is greater than other card.

        Args:
            other (Card):   other card.

        Returns:
            bool:   True => this card is greater than other card.
        """
        if RANK_ORDER.index(self.rank) > RANK_ORDER.index(other.rank):
            return True
        if RANK_ORDER.index(self.rank) == RANK_ORDER.index(other.rank):
            return SUIT_ORDER.index(self.suit) > SUIT_ORDER.index(other.suit)
        return False

    def serialize(self):
        """
        Convert Card object to card state dictionary.

        Used for serialization into JSON-string.

        Returns:
            dict:   card state.
        """
        return {'suit': self.suit.value,
                'rank': self.rank.value}


class Deck:
    """
    Deck of playing cards.
    """
    def __init__(self, remove=None):
        """
        Initializer.

        Some card game don't use a deck of 52 cards (e.g. Swiss Jass is played
        with 36 cards, German Skat with 32 cards, and Italian Scopa with 40
        cards). Usually these decks are created by removing lower cards, e.g.
        for Swiss Jass you remove 2, 3, 4, and 5 (but keep the Ace).

        Args:
            remove (list):  list of removed ranks.
        """
        # create deck of cards (without Jokers)
        if remove is not None:
            # create reduced deck
            self.cards = [Card(s, r) for s in Suit for r in Rank if r not in remove]
        else:
            # create complete deck (=> 52 cards)
            self.cards = [Card(s, r) for s in Suit for r in Rank]

    def __str__(self):
        """
        Get string representation of deck.

        Returns:
            str:    string with all cards in deck.
        """
        return ' '.join([str(c) for c in self.cards])

    def __repr__(self):
        """
        Get debugger representation of deck.
        """
        return ''.join([f"<Card {c.rank} of {c.suit}>\n" for c in self.cards])

    def shuffle_cards(self):
        """
        Shuffle deck of cards.

        Randomly changes the sequence of cards in the cards list.
        """
        shuffle(self.cards)

    def deal_card(self):
        """
        Deal card from top of deck.

        Returns:
            Card:   Top card of deck.
        """
        return self.cards.pop(-1)

    def remove_card(self, card):
        """
        Remove specified card from the deck. 

        Args:
            card (Card):    card to be removed from deck.
        """
        self.cards.remove(card)

    def serialize(self):
        """
        Convert Deck object to list of serialized cards.

        Used for serialization into JSON-string.

        Returns:
            list:   serialized cards.
        """
        return [card.serialize() for card in self.cards]

    def deserialize(self, state):
        """
        Load Deck from serialized Deck.

        Args:
            state (list):    serialized Deck object.
        """
        self.cards = [Card(Suit(c['suit']), Rank(c['rank'])) for c in state]


if __name__ == '__main__':
    # !!!NOTE!!!
    # To avoid ModuleNotFoundError start it from '~/Projects/slalom_jass/src' with
    # python3 -m slalom_jass.cards

    print(Card(Suit.SPADES, Rank.ACE))
    print(Card(Suit.HEARTS, Rank.QUEEN))
    print(Card(Suit.DIAMONDS, Rank.TEN))
    print(Card(Suit.CLUBS, Rank.TWO))

    deck = Deck()
    print(deck)
    deck.shuffle_cards()
    print(deck)
    serialized_deck = (deck.serialize())
    print(serialized_deck)
    deck.deserialize(serialized_deck)
    print(deck)

    # create a Swiss Jass deck
    deck = Deck(remove=[Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE])
    print(f"\nSwiss-Jass deck: {deck}")
