"""
Hearts card game player.
"""

from slalom_jass.cards import Card, Deck, Suit, Rank, RANK_ORDER, SUIT_ORDER


# list of symbols exported if a script calls 'from player import *'
__all__ = [
    'Player',
    'NOF_PLAYERS'
]


NOF_PLAYERS = 4
BLACK_MARY = Card(Suit.SPADES, Rank.QUEEN)


class Player:
    """
    Player.

    Attributes:
        name (str):     name of player.
        hand (list):    cards in hand.
        tricks (list):  tricks collected.
    """

    def __init__(self, name):
        """
        Initializer.

        Args:
            name (str):     name of player.
        """
        self.name = name
        self.hand = []
        self.tricks = []

    def get_card(self, card):
        """
        Add card to hand during dealing.

        Args:
            card (Card):    card dealt to player.
        """
        self.hand.append(card)

    def sort_hand(self):
        """
        Sort hand by suits and ranks.
        """
        self.hand = sorted(self.hand, key=lambda x: (SUIT_ORDER.index(x.suit),
                                                     RANK_ORDER.index(x.rank)))

    def show_hand(self, hide=False):
        """
        Show hand cards.

        Args:
            hide (bool):    True => hide cards.

        Returns:
            str:    string of hand cards.
        """
        if hide:
            # display hand cards as 'XX XX ...'
            return len(self.hand) * 'XX  '

        hand_str = [f"{self.hand[i]}" for i in range(len(self.hand))]
        return '  '.join(hand_str)

    def show_tricks(self):
        """
        Show tricks player has collected.

        Returns:
            str:    string of collected tricks.
        """
        # convert cards in trick to strings
        tricks_str = [[str(c) for c in trick] for trick in self.tricks]
        # convert each trick into a string of card strings.
        tricks_str = [' '.join(trick) for trick in tricks_str]
        return '  '.join(tricks_str)

    def play_card(self, card):
        """
        Play a card from hand selected by index.

        Args:
            card (Card):    card to play.

        Returns:
            Card:   card to play.

        Throws:
            ValueError:     if card is not in hand.
        """
        # get index of card in player's hand
        idx = self.hand.index(card)
        # remove card at index from hand and return it.
        return self.hand.pop(idx)

    def collect_trick(self, trick):
        """
        Collect a trick.

        Args:
            trick (tuple):      tuple of 4 cards played during turn.
        """
        self.tricks.append(trick)

    def serialize(self):
        """
        Convert Player object to dictionary.

        Used for serialization into JSON-string.

        Returns:
            dict:   player state.
        """
        state = {}
        state['name'] = self.name
        state['hand'] = [card.serialize() for card in self.hand]
        state['tricks'] = [[card.serialize() for card in trick]
                           for trick in self.tricks]
        return state

    def deserialize(self, state):
        """
        Load Player object from serialized Player.

        Args:
            state (dict):   serialized Player object.
        """
        self.name = state['name']
        self.hand = [Card(Suit(c['suit']), Rank(c['rank']))
                     for c in state['hand']]
        self.tricks = [[Card(Suit(c['suit']), Rank(c['rank'])) for c in trick]
                       for trick in state['tricks']]


def main():
    """
    Test Player class.
    """
    # create card deck for Swiss Jass, i.e. remove '2', '3', '4', '5'.
    deck = Deck(remove=[Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE])

    # shuffle deck
    deck.shuffle_cards()

    # create player, deal him 9 cards.
    player = Player('Wolbert')
    for _ in range(9):
        card = deck.deal_card()
        player.get_card(card)

    # show player cards unsorted
    print(f"{player.name}: ",end='')
    print(player.show_hand())
    print()

    # show player cards sorted
    player.sort_hand()
    print(f"{player.name}: ",end='')
    print(player.show_hand())
    print()

    # ask player to select a card
    card_idx = input("Card to play: ")
    print(f"card_idx: {card_idx}")
    card = player.hand[int(card_idx)]
    card = player.play_card(card)
    print(card)
    print(player.show_hand())
    print()

    # sort hand by rank from lowest to highest
    ranked = sorted(player.hand, key=lambda x: RANK_ORDER.index(x.rank))
    print('  '.join([str(card) for card in ranked]))
    print()

    # serialize player
    serialized_player = player.serialize()
    print(serialized_player)
    print()

    # deserialize player
    player.deserialize(serialized_player)
    print(player.name)
    print(player.show_hand())

if __name__ == '__main__':
    # !!!NOTE!!!
    # To avoid ModuleNotFoundError start it from '~/Projects/slalom_jass/src' with
    # python3 -m slalom_jass.game.player

    main()
