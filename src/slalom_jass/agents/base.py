"""
Baseclass of 'Jass' card game agents.
"""

# list of symbols exported if a script calls 'from base import *'
__all__ = [
    'Agent',
]

class Agent:
    """
    Baseclass for 'Jass' agents.

    Attributes:
        collector (ExperienceCollector):    Experience collector.
    """
    def __init__(self):
        self.collector = None
#        self.encoder = 'oneplane'

    def select_play(self, game_state):
        """
        Select a card to play.

        Select a legal card to play in this game state.
        !!! Must be implemented in the sub-class !!!

        Args:
            game_state (GameState):     current state of the game.
        """
        raise NotImplementedError()

    def set_collector(self, collector):
        """
        Set experience collector.

        The experience collector collects states, plays, and rewards in order
        to train other agents.

        Args:
            collector (ExperienceCollector): experience collector.
        """
        self.collector = collector
