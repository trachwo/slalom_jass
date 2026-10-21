"""
Slalom-Jass Scenario Reader.

Allows to read preset hands per player from a scenario-file.
If the scenario does not specify all of the players' hands, the remmaining
cards are randomly distributed to the unspecified hands.
"""
import csv
from pathlib import Path

from slalom_jass.cards import Suit, Rank, Card, Deck, SUIT_ORDER, RANK_ORDER

# list of symbols exported if a script calls 'from scenario import *'
__all__ = [
    'Scenario',
]

# absolute path to  Projects/slalom_jass/src
BASE_PATH = Path(__file__).parents[2]

# absolute path to scenario files
SCENARIO1 = str(BASE_PATH / 'data' / 'scenarios' / 'scenario_1.cs')
SCENARIO2 = str(BASE_PATH / 'data' / 'scenarios' / 'scenario_2.cs')

STR_TO_SUIT = {'C': Suit.CLUBS,
               'D': Suit.DIAMONDS,
               'H': Suit.HEARTS,
               'S': Suit.SPADES}

STR_TO_RANK = {'6': Rank.SIX,
               '7': Rank.SEVEN,
               '8': Rank.EIGHT,
               '9': Rank.NINE,
               '10': Rank.TEN,
               'J': Rank.JACK,
               'Q': Rank.QUEEN,
               'K': Rank.KING,
               'A': Rank.ACE}

class Scenario():
    """
    Slalom-Jass Scenario Reader.

    Attributes:
        scenario_path (str):    path to scenario file.
        hands (dict):           list of cards per player.
        deck (Deck):            deck of cards (6 - A).

    """
    def __init__(self, scenario_path):
        """
        Initializer.

        Args:
            scenario_path (str):        path to scenario file.
        """
        self.scenario_path = scenario_path
        self.hands = {'P1': [], 'P2': [], 'P3': [], 'P4': []}
        # create and shuffle deck of 36 cards ('2', '3', '4', and '5' removed)
        self.deck = Deck(remove=[Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE])
        self.deck.shuffle_cards()

    def add_card_to_hand(self, player, card):
        """
        Adds card specified in scenario-file to player's hand.

        Args:
            player (str):   'P1', 'P2', 'P3', or 'P4'.
            card (str):     name of card (e.g. '8-C', 'Q-H', etc.)
        """
        # create card
        rank = STR_TO_RANK[card[0]]
        suit = STR_TO_SUIT[card[1]]
        card = Card(suit, rank)
        try:
            # try to remove it from the deck
            self.deck.remove_card(card)
        # card has already been removed from the deck
        except:
            raise ValueError(f"{str(card)} was used multiple times in scenario!")

        # add it to the hand of the specified player.
        self.hands[player].append(card)

    def load(self):
        """
        Load scenario from CSV-file.
        """
        line_num = 0     # line number

        with open(self.scenario_path, 'r', encoding='utf-8') as fp:
            # create the CSV-Reader to read ','-separated values from this file
            scenario_reader = csv.reader(fp, delimiter=',')
            for row in scenario_reader:
                line_num = scenario_reader.line_num
                # remove leading/trailing whitespace from fields
                row = [x.strip() for x in row]

                # skip comments.
                if row[0][0] == '#':
                    continue

                # Error if ',' at end of line.
                if len(row[-1]) == 0:
                    raise ValueError(f"Detected ',' at end of row {line_num}!")

                # remove comment field at end of row.
                if row[-1][0] == '#':
                    row = row[:-1]

                # check number of fields.
                if len(row) != 10:
                    raise ValueError(f"Wrong number of fields {len(row)} in row"
                                     f" {line_num}!")

                # check if 1st field is 'P1', 'P2', 'P3', or 'P4'.
                if row[0] not in self.hands:
                    raise ValueError(f"Row {line_num}: {row[0]} is not a valid"
                                     f" player!")
                for field in row[1:]:
                    card = field.split('-')
                    if len(card) != 2:
                        raise ValueError(f"Row {line_num}: {field} has illegal"
                                         f" format!")
                    if card[0] not in STR_TO_RANK:
                        raise ValueError(f"Row: {line_num}: {card[0]} is not a"
                                         f" card-rank!")
                    if card[1] not in STR_TO_SUIT:
                        raise ValueError(f"Row: {line_num}: {card[1]} is not a"
                                         f" card-suit!")
                    self.add_card_to_hand(row[0], card)

    def distribute(self):
        """
        Fill unspecified hands with remaining deck cards.
        """
        for _, hand in self.hands.items():
            while len(hand) < 9:
                # get card from top of deck
                card = self.deck.deal_card()
                # add it to this player's hand
                hand.append(card)

    def sort_hands(self):
        """
        Sort hands by suits and ranks.
        """
        for p, hand in self.hands.items():
            self.hands[p] = sorted(hand,
                                   key=lambda x: (SUIT_ORDER.index(x.suit),
                                                  RANK_ORDER.index(x.rank)))

    def print(self):
        """
        Print cards in player hands.
        """
        for player, hand in self.hands.items():
            hand_str = '  '.join([str(c) for c in hand])
            print(f"{player}: {hand_str}")


if __name__ == '__main__':
    print(f"BASE_PATH: {BASE_PATH}")

    # scenario 1: all hands specified
    scenario = Scenario(SCENARIO1)
    scenario.load()
    print("\nscenario_1.cs: hands after load:")
    scenario.print()
    print("\nscenario_1.cs: hands after distribute:")
    scenario.distribute()
    scenario.print()

    scenario = Scenario(SCENARIO2)
    scenario.load()
    print("\nscenario_2.cs: hands after load:")
    scenario.print()
    print("\nscenario_2.cs: hands after distribute:")
    scenario.distribute()
    scenario.print()
    print("\nscenario_2.cs: hands after sorting:")
    scenario.sort_hands()
    scenario.print()
