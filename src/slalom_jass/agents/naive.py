"""
Implementation of random bot for 'Slalom-Jass' card game.
"""

import json
import random

from slalom_jass.agents.base import Agent
from slalom_jass.cards import RANK_ORDER
from slalom_jass.game import OBENABE_POINTS_ORDER, UNDEUFE_POINTS_ORDER,\
     NOF_PLAYERS, GameState, simulate_game, finish_game

# list of symbols exported if a script calls 'from naive import *'
__all__ = [
    'RandomBot',
    'SimpleBot',
]

def get_least_valuable_card(legal_plays, next_bock_cards, obenabe):
    """
    Get least valuable non-bock playable card.

    Args:
        legal_plays (list):     next player's playable cards.
        next_bock_cards (list): cards which could be bock in future tricks.
        obenabe (bool):     True => obenabe round, False => undeufe round.
                            NOTE: points depend on mode of whole round!!!

    Returns:
        Card:   least valuable card, if possible not a potential bock.
    """
    if obenabe:
        cards = sorted(legal_plays,
                       key=lambda x: OBENABE_POINTS_ORDER.index(x.rank))
    else:
        cards = sorted(legal_plays,
                       key=lambda x: UNDEUFE_POINTS_ORDER.index(x.rank))

    for card in cards:  # start with cheapest card
        if card not in next_bock_cards:
            # play least valuable card which is not bock in future tricks.
            return card
    # play least valuable card although it could be bock in future tricks.
    return cards[0]


def get_most_valuable_card(legal_plays, next_bock_cards, obenabe):
    """
    Get least valuable non-bock playable card.

    Args:
        legal_plays (list):     next player's playable cards.
        next_bock_cards (list): cards which could be bock in future tricks.
        obenabe (bool):     True => obenabe round, False => undeufe round.
                            NOTE: points depend on mode of whole round!!!

    Returns:
        Card:   most valuable card, if possible not a potential bock.
    """
    if obenabe:
        cards = sorted(legal_plays,
                       key=lambda x: OBENABE_POINTS_ORDER.index(x.rank))
    else:
        cards = sorted(legal_plays,
                       key=lambda x: UNDEUFE_POINTS_ORDER.index(x.rank))

    for card in reversed(cards):    # start with most valuable card
        if card not in next_bock_cards:
            # play most valuable card which is not bock in future tricks.
            return card
    # play most valuable card although it could be bock in future tricks.
    return cards[-1]


class RandomBot(Agent):
    """
    Implementation of Slalom-Jass-Agent selecting playable cards at random.
    """
    def __init__(self):
        """
        Initializer.
        """
        Agent.__init__(self)        # base class initializer.

    def save(self, filename):
        """
        Save agent type.

        Args:
            filename (str):     filename.
        """
        data = {
            "type": "random"
        }
        # write data to json-file.
        if not filename.endswith('.json'):
            raise ValueError (
                "Filename must have extension '.json' => json-file!")
        json_str = json.dumps(data, indent=4)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)

    def select_play(self, game_state):
        """
        Select declaration or playable card at random.

        Args:
            game_state (GameState):     current game state.

        Returns:
            str or Card:    Selected declaration or selected card.
        """
        # get list of declarations or of playable cards
        plays = game_state.get_legal_plays()
        if len(plays) == 0:
            raise ValueError("No plays to choose from!")
        # return randomly selected card
        return random.choice(plays)


class SimpleBot(Agent):
    """
    Implementation of Slalom-Jass-Agent using lightweight heuristics.

    SimpleBot plays a little bit smarter than RandomBot using the following
    heuristic policy:

        - Agent plays 1st:
            1. Play a 'Bock'-card (= highest remaining card of a suit during
               'Obenabe', or lowest remaining card of a suit during 'Undeufe').
            2. Play card with minimum point value, but try to keep cards, which
               are 'Bock' in a later trick.

        - Agent plays 2nd:
            1. Follow suit with a 'Bock'-card.
            2. Play card with minimum point value, but try to keep cards, which
               are 'Bock' in a future trick.

        - Agent plays 3rd:
            1. If first player (= partner) surely wins this trick, play card
               with maximum point value, but try to keep cards, which are
               'Bock' in a future trick.
            2. Follow suit with a 'Bock'-card.
            3. We may lose this trick (opponent plays last), therefore play
               card with minimum point value, but try to keep cards, which are
               'Bock' in future tricks.

        - Agent plays 4th:
            1. If 2nd player (= partner) has already won this trick, play card
               with maximum point value, but try to keep cards, which are
               'Bock' in a future trick.
            2. Win the trick with the best card necessary.
            3. Opponents will win this trick, therefore play card with minimum
               point value, but try to keep cards, which are 'Bock' in a future
               trick.

    SimpleBot can be used instead of RandomBot for MCTS smart rollouts
    (=> slower but more realistic).
    """
    def __init__(self):
        """
        Initializer.
        """
        Agent.__init__(self)        # base class initializer.

    def save(self, filename):
        """
        Save agent type.

        Args:
            filename (str):     filename.
        """
        data = {
            "type": "simple"
        }
        # write data to json-file.
        if not filename.endswith('.json'):
            raise ValueError (
                "Filename must have extension '.json' => json-file!")
        json_str = json.dumps(data, indent=4)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)

    def select_turn_1_card(self, game_state):
        """
        Select card as 1st player.

        Selection:
            - 1st player has bock cards:
              => play one of the bock cards.

            - 1st player has no bock cards.
              => play cheapest (points) card which is not a bock in future
                 tricks.

        Args:
            game_state (GameState):     current game state.

        Returns:
            card (Card):                card 1st player wants to play.
        """
        # get playable cards
        cards = game_state.get_legal_plays()

        if len(cards) == 1:
            # only 1 playable card
            return cards[0]

        # check if higher or lower card wins 
        obenabe = game_state.higher_card_wins()

        # get lowest and highest cards still in the game pers suit
        lowest, highest = game_state.get_bock_cards()

        # check if we have bock-cards
        if obenabe:     # OBENABE trick
            # playable cards which are bock this trick
            bock_cards = [c for c in cards if c in highest]
            next_bock_cards = lowest
        else:           # UNDEUFE trick
            bock_cards = [c for c in cards if c in lowest]
            next_bock_cards = highest

        if bock_cards:
            # play random bock card.
            return random.choice(bock_cards)

        # no bock
        # => play cheapest card (if possible) not bock in next trick.
        return get_least_valuable_card(cards, next_bock_cards, obenabe)

    def select_turn_2_card(self, game_state):
        """
        Select card as 2nd player.

        Selection:
            - 2nd player can follow suit:
                -- 2nd player has bock card:
                   => play bock card.
                -- 2nd player does not have bock card.
                   => play cheapest (points) card which is not a bock in future
                      tricks.
            - 2nd player cannot follow suit:
              => play cheapest (points) card which is not a bock in future
                 tricks.

        Args:
            game_state (GameState):     current game state.

        Returns:
            card (Card):                card 2nd player wants to play.
        """
        # get playable cards
        cards = game_state.get_legal_plays()

        if len(cards) == 1:
            # only 1 playable card
            return cards[0]

        # check if higher or lower card wins 
        obenabe = game_state.higher_card_wins()

        # get lowest and highest cards still in the game pers suit
        lowest, highest = game_state.get_bock_cards()

        # check if we are following suit.
        if cards[0].suit == game_state.table[0].suit:
            # check if we have the bock-card
            if obenabe:     # OBENABE trick
                # playable card which is bock this trick
                bock_cards = [c for c in cards if c in highest]
            else:           # UNDEUFE trick
                # playable card which is bock this trick
                bock_cards = [c for c in cards if c in lowest]
            if bock_cards:
                # play bock card (can only be 1 in the led suit)
                return bock_cards[0]

            # no bock
            # => play cheapest card not bock in a future trick (if possible).
            return get_least_valuable_card(cards, lowest + highest, obenabe)

        # not following suit
        # => play cheapest card not bock in a future trick (if possible).
        return get_least_valuable_card(cards, lowest + highest, obenabe)

    def select_turn_3_card(self, game_state):
        """
        Select card as 3rd player.

        Selection:
            - 3rd player can follow suit:
                -- 1st player (partner) has won the trick so far:
                   --- 1st player has played bock card:
                       => play most valuable non-bock.
                   --- 1st player has not played bock card:
                       ---- 3rd player has all cards better than 1st's card:
                            => play most valuable non-bock.
                       ---- 4th player could beat 1st player's card:
                            ----- 3rd player has bock card:
                                  => play bock card.
                            ----- 3rd player does not have bock card:
                                  => play cheapest non-bock card.
                -- 2nd player (opponent) has won the trick so far:
                   --- 3rd player has bock-card:
                       => play bock card.
                   --- 3rd player does not have bock card:
                       => play cheapest non-bock card.

            - 3rd player cannot follow suit:
                -- 1st player (partner) has won the trick so far:
                   --- 1st player has played bock card:
                       => play most valuable non-bock.
                   --- 1st player has not played bock card:
                       => play cheapest non-bock card.
                -- 2nd player has won the trick so far:
                   => play cheapest non-bock card.

        Args:
            game_state (GameState):     current game state.

        Returns:
            Card:       card played by 3rd player.
        """
        # get playable cards
        cards = game_state.get_legal_plays()

        if len(cards) == 1:
            # only 1 playable card
            return cards[0]

        # get cards on table
        table = game_state.table

        # check if higher or lower card wins 
        obenabe = game_state.higher_card_wins()

        # check who has won the trick so far.
        winner = GameState.find_trick_winner(table, obenabe)

        # get lowest and highest cards still in the game pers suit
        lowest, highest = game_state.get_bock_cards()
        bock_cards = highest if obenabe else lowest

        # get list of cards which could beat partners card
        better_cards = game_state.info.get_lower_or_higher(table[0], obenabe)

        # check if we are following suit.
        if cards[0].suit == table[0].suit:
            if winner == 0:
                # our partner has won the trick so far
                if not better_cards: 
                    # partner has played bock
                    # => play most valuable card which is not a future bock
                    return get_most_valuable_card(cards, lowest + highest,
                                                  obenabe)
                # our partner didn't play bock
                if (len([c for c in cards if c in better_cards])
                    == len(better_cards)):
                    # all better cards are in our hand
                    # => play most valuable card which is not a future bock
                    return get_most_valuable_card(cards, lowest + highest,
                                                  obenabe)
                # the 4th player (opponent) could have one of the better cards
                my_bock = [c for c in cards if c in bock_cards]
                if my_bock:
                    # we have the bock in the led suit 
                    return my_bock[0]
                # the 4th player could have the bock in the led suit
                # => play the cheapest card which is not a future bock
                return get_least_valuable_card(cards, lowest + highest,
                                               obenabe)
            # the 2nd player (opponent) has won the trick so far
            my_bock = [c for c in cards if c in bock_cards]
            # if we have the bock card, we play it
            if my_bock and obenabe and my_bock[0] > table[1]:
                return my_bock[0]
            if my_bock and not obenabe and my_bock[0] < table[1]:
                return my_bock[0]

            # we don't have the bock card
            # => play the cheapest card which is not a future bock
            return get_least_valuable_card(cards, lowest + highest, obenabe)

        # we cannot follow suit
        if winner == 0:
            # our partner has won the trick so far
            if not better_cards: 
                # partner has played bock
                # => play most valuable card which is not a future bock
                return get_most_valuable_card(cards, lowest + highest, obenabe)

        # the 2nd player has already won the trick or the 4th player could have
        # the bock card
        # => play the cheapest card which is not a future bock
        return get_least_valuable_card(cards, lowest + highest, obenabe)

    def select_turn_4_card(self, game_state):
        """
        Select card as 4th player.

        Selection:
            - 2nd player (partner) has won trick (so far):
              => play most valuable non-bock.

            - 2nd player has lost trick:
                -- 4th player can follow suit:
                    --- 4th player can win this trick:
                        => play best card necessary.
                    --- 4th player cannot win this trick:
                        => play cheapest non-bock.

        TODO there seems to be a problem.

        Args:
            game_state (GameState):     current game state.

        Returns:
            Card:       card played by 4th player.
        """
        # get playable cards sorted by rank lowest to highest
        cards = sorted(game_state.get_legal_plays(),
                       key=lambda x: RANK_ORDER.index(x.rank))

        if len(cards) == 1:
            # only 1 playable card
            return cards[0]

        # get cards on table
        table = game_state.table

        # check if higher or lower card wins 
        obenabe = game_state.higher_card_wins()

        # check who has won the trick so far.
        winner = GameState.find_trick_winner(table, obenabe)

        # get lowest and highest cards still in the game pers suit
        lowest, highest = game_state.get_bock_cards()

        if winner == 2:
            # our partner has already won this trick
            # => play most valuable card which is not a future bock
            return get_most_valuable_card(cards, lowest + highest, obenabe)

        # opponents have one this trick so far.
        if cards[0].suit == table[0].suit:
            # we are following suit
            if obenabe:     # obenabe trick
                # find lowest card wich can win the trick
                my_best = [c for c in cards if c > table[winner]]
                if my_best:
                    return my_best[0]
            else:           # undeufe trick
                # find highest card wich can win the trick
                my_best = [c for c in cards if c < table[winner]]
                if my_best:
                    return my_best[-1]

        # cannot win the trick or cannot follow suit
        # => play cheapest card which is not a future bock
        return get_least_valuable_card(cards, lowest + highest, obenabe)

    def select_declaration(self, game_state):
        """
        Select declaration.

        We let the next player play multiple games with declaration 'Obenabe'
        and 'Undeufe' calculating the average score for both types of game.
        We 

        Args:
            game_state (GameState):     current game state.

        Returns:
            str:    'Schiebe', 'Obenabe', or 'Undeufe'.
        """
        # make sure we're in the declaration phase
        if game_state.tricks >= 0:
            raise ValueError("Not in declaration phase!")
        # get legal declarations
        declarations = game_state.get_legal_plays()

        # get next player
        player = game_state.next_player
        # get partner of next player
        partner = (player + 2) % NOF_PLAYERS
        nof_eval_games = 100
        obenabe_points = 0   # total team points for obenabe games
        undeufe_points = 0   # total team points for undeufe games
        for _ in range(nof_eval_games):
            # play a number of obenabe games
            game = game_state.clone_and_randomize()
            game = game.apply_play('Obenabe')
            points = finish_game(game, SimpleBot(), SimpleBot(), SimpleBot(),
                                 SimpleBot(), False)
            obenabe_points += points[player]
            obenabe_points += points[partner]

            # play a number of undeufe games
            game = game_state.clone_and_randomize()
            game = game.apply_play('Undeufe')
            points = finish_game(game, SimpleBot(), SimpleBot(), SimpleBot(),
                                 SimpleBot(), False)
            undeufe_points += points[player]
            undeufe_points += points[partner]
#        print(f"Average Obenabe points: {obenabe_points / nof_eval_games:.1f}")
#        print(f"Average Undeufe points: {undeufe_points / nof_eval_games:.1f}")

        if obenabe_points >= undeufe_points and obenabe_points / nof_eval_games > 100:
            return 'Obenabe'
        if undeufe_points >= obenabe_points and undeufe_points / nof_eval_games > 100:
            return 'Undeufe'
        if 'Schiebe' in declarations:
            return 'Schiebe'
        if obenabe_points >= undeufe_points:
            return 'Obenabe'
        return 'Undeufe'  

    def select_play(self, game_state):
        """
        Select declaration or playable card using lightweight heuristics.

        Args:
            game_state (GameState):     current game state.

        Returns:
            str or Card:    Selected declaration or card.
        """
        if game_state.tricks < 0:
            # declaration phase
            # => get list of legal declarations
            return self.select_declaration(game_state)

        # trick phase (tricks >= 0)
        if game_state.turns == 0:
            # let 1st player select card.
            return self.select_turn_1_card(game_state)
        if game_state.turns == 1:
            # let 2nd player select card.
            return self.select_turn_2_card(game_state)
        if game_state.turns == 2:
            # let 3rd player select card.
            return self.select_turn_3_card(game_state)
        if game_state.turns == 3:
            # let 4th player select card.
            return self.select_turn_4_card(game_state)


if __name__ == '__main__':
#    simulate_game(RandomBot(), RandomBot(), RandomBot(), RandomBot(), 3, True)
    simulate_game(SimpleBot(), SimpleBot(), SimpleBot(), SimpleBot(), 3, True)
