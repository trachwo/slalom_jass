"""
Implementation of human interface for Hearts card game.
"""

import json

from slalom_jass.agents.base import Agent

# list of symbols exported if a script calls 'from mcts import *'
__all__ = [
    'HumanAgent',
]


class HumanAgent(Agent):
    """
    Implementation of Slalom-Jass-Agent as human interface.
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
            "type": "human"
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
        Let human player select a move.

        Args:
            game_state (GameState):     current game state.

        Returns:
            str or Card:       Selected declaratin or selected card.
        """
        # check if game state is in declaratin phase.
        if game_state.tricks < 0:
            player = game_state.players[game_state.next_player]
            declarations = game_state.get_legal_declarations()
            dec_str = [f"{i}:{declarations[i]}"
                       for i in range(len(declarations))]
            dec_str = '  '.join(dec_str)
            while True:
                sel = input(f"\n   {player.name} select: {dec_str} ? ")
                try:
                    if int(sel) >= 0 and int(sel) < len(declarations):
                        break
                except ValueError:
                    continue    # wait for player to make valid choice.
            print()
            return declarations[int(sel)]

        # get list of playable cards
        plays = game_state.get_legal_card_plays()
        # ask human agent to select one of these cards
        plays_str = [f"{i}:{plays[i]}" for i in range(len(plays))]
        plays_str = '  '.join(plays_str)
        while True:
            sel = input(f"   {plays_str} ? ")
            try:
                if int(sel) >= 0 and int(sel) < len(plays):
                    break
            except ValueError:
                continue
        # return selected card
        return plays[int(sel)]
