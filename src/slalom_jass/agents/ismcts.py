"""
Information Set Monte Carlo Tree Search (ISMCTS) agent for 'Slalom-Jass'.

MCTS let's us find an optimum move without complex position evaluation as
necessary for depth pruning. We just select one of the legal moves and apply
it to the current state. From this new game state we let primitive agents
play out the game choosing legal moves at random (or using lightweight
heuristics) and note the winner. The result of 1 such simulation is purely
random, but if the move applied to the current (root) state has advantages for
one or the other player, it will show in the win statistics over several
simulations. With MCTS we don't do this just for the legal moves of the current
state, but expand it to a tree of game states running simulations from the
lowest branches and backpropagate the results through the tree up to the root.
To avoid that the tree is just expanded by paths determinded by accidently
found initially good results, we use the 'Upper Confidence Bound for Trees'
(UCT) method to strike a balance between exploitation (following the path
with the best results) and exploration (following a path with rarely simulated
moves).

Most MCTS examples found online are about 2 player games with perfect
information like 'Connect 4' or 'Go'. But 'Slalom-Jass' is a 4-player game with
imperfect information, i.e. players only know their own cards (=> available
actions). For multiplayer games with imperfect information we have to switch to
Single Observer Information Set Monte Carlo Tree Search (SO-ISMCTS), i.e. we
make the following changes to the multiplayer MCTS algorithm we used for the
MCTSCheater agent (= multiplayer MCTS with perfect information):

    1. DETERMINISATION PHASE
       This is a new phase, in which we randomly redistribute the (unknown)
       opponent cards before each rollout, while keeping our own (known) cards.
       We can use information gathered in previous turns of the game for the
       redistribution (e.g. if a player couldn't follow a suit in a previous
       turn, he's out of that suit and doesn't get any cards of that suit
       during redistribution).

    2. SELECTION PHASE
       Due to the random redistribution of opponent cards, it is now possible,
       that a node (where one of the opponents selects the play) which was
       fully expanded in a previous rollout, has now new unexpanded plays
       available in the current rollout. I.e. we can no longer rely on a fixed
       'untried plays' or 'children' list, but have to get a list of legal
       plays from the current game state and compare it to the list of expanded
       plays in each traversed node. Only if all legal plays in the current
       game state (with redistributed opponent cards) have been expanded into
       child nodes, can we use the Upper Confidence boundery for Trees (UCT),
       to move down the tree to one of the children.
       NOTE, that the calculation of the Upper Confidance Boundary (UCB1) has
       also changed. If we would still use the number of times the parent was
       visited to calculate the exploration bonus, plays which appear seldomly
       in the list of legal plays for a node, will be overexplored. In the
       changed UCB1 calculation we have to replace the number of times the
       parent node was visited with the number of times the parent node was
       visited AND THE CHILD NODE WAS AVAILABLE. This also means that we
       increment the 'visits' count in the SELECTION phase as long as the
       corresponding state and therefore its legal plays are available
       (otherwise we would have to store a clone of the state or at least the
       legal plays in the node).

    3. EXPANSION PHASE
       As soon as we get to a node, where not every available legal play for
       the corresponding game state (with redistributed opponent cards) is
       already matched by a child node, we have to expand one of the unmatched
       legal plays into a new child node and run a simulation from there.

    4. SIMULATION PHASE
       The simulation phase is identical with vanilla MCTS, we use random
       selection or simple heuristics to bring the game to a terminal state and
       give the corresponding rewards (0.0 ... 1.0) to the winners and losers.

    5. BACKPROPAGATION PHASE
       Backpropagate the rewards dictionary up the tree, adding the
       corresponding reward (the one for the active player in the parent node,
       who made the decision to make this play, i.e. move to this node).
       NOTE: we no longer update the 'visits' count, because that was already
             done during SELECTION on the way down the tree (since we needed
             the legal plays per state to increment the 'visits_per_play'
             counters).
"""

import math
import time
import random
from collections import defaultdict
import json

from slalom_jass.agents.base import Agent
from slalom_jass.agents.naive import RandomBot, SimpleBot
from slalom_jass.game import GameState, NOF_PLAYERS

# list of symbols exported if a script calls 'from mcts import *'
__all__ = [
    'ISMCTSAgent',
]


def points_to_score(points):
    """
    Convert points to score.

    As final step of the MTCS-algorithm, we have to update the statistic
    counters in each node we passed through from the root to the new node
    (state), from where the random simulation was started. Each of these nodes
    gets its 'visited' counter incremented and in a 2-player game each node,
    where the winning player selected the action in the parent node, the win
    counter is incremented. Both counters are necessary to calculate the UCT
    score of a node. In Slalom-Jass the simulation gives us the points
    (0 to 157) for each of the 4 players. We sum up these points per team
    (Player1 + Player3 and Player2 + Player4) and convert the results into
    values from 0.0 (0 points) to 1.0 (157 points), adding them to the win
    counters in the corresponding visited nodes.

    Args:
        points (list):      points (0 ... 157) per player.

    Returns:
        rewards (list):     rewards (0.0 ... 1.0) per player.
    """
    # get team points
    team13 = (points[0] + points[2]) / 157
    team24 = (points[1] + points[3]) / 157

    return [team13, team24, team13, team24]


def show_tree(node, indent='', level=0, max_depth=3):
    """
    Print the MCTS tree.

    Args:
        node (MCTSNode):    starting node.
        indent (str):       indention for printing this level.
        level (int):        level.
        max_depth (int):    maximum depth to print.
    """
    if max_depth < 0:
        return
    if node is None:
        return
    if node.parent is None:
        print(f"\n{indent}root")
    else:
        player = node.parent.active_player + 1
        play = node.play
        print(f"{indent} {level} {indent} P{player} {str(play)} {node.visits} "
              f"{node.wins / node.visits:.3f}")

    # loop through children sorted from highest to lowest number of rollouts
    for child in sorted(node.children, key=lambda n: n.visits,
                        reverse=True):
        show_tree(child, indent + '--', level + 1, max_depth - 1)


class ISMCTSNode():
    """
    Node in the Information Set Monte Carlo Tree Search tree.

    Tracks the performance of play selections with random playouts.
    Each node corresponds to a certain state reached over 1 or more plays from
    the root state (node), which is the state for which we want to find the
    best play for the active player. In our case it's not necessary to store
    a clone of the corresponding state in the node. We just need the link to
    the parent node (previous state) and the list of children (expanded plays).
    In each rollout we search a way through the tree to a node with untried
    legal plays. One of these plays is then expanded into a new child node and
    a simulation using random plays is started from the corresponding state to
    find winners and losers. The rewards for winners and losers are
    backpropagated up the tree => update 'visits' and 'wins' counters in nodes
    passed on the way up to the root node. 'visits' and 'wins' counters are
    used by the active player in the parent (!) node to decide which play
    (child node) to select next on the way to a node with untried moves. The
    UCT method calculating UCB1 from wins and visits counters is used to make
    these decisions.
    Changes made from MCTSNode to ISMCTSNode:

        - we no longer have a fixed 'untried plays' list, instead we have to
          compare the list of child nodes to the list of available legal plays
          in the corresponding game state, since new untried plays may become
          available (in nodes where an opponent is the active player),
          depending on the DETERMINISATION phase (redistributing opponent
          cards) at the beginning of each rollout.

        - each node has to count visits per available child for correct UCB1
          calculation (subset-armed bandit). I.e. when we backpropagate the
          simulation result up the tree, we not only increment the 'visits'
          counter, but also increment a seperate counter for each child which
          was available during this rollout (=> correct calculation of
          exploration bonus for each child).

    NOTE: for each rollout we make a clone of the state (for which we try to
          find the best move) and change it in parallel with the movement
          through the search tree to a node with untried moves (SELECTION phase)
          and to a terminal state (SIMULATION phase). Therefore, it's not
          necessary to store a clone of the current state in each node. 

    Attributes:
        parent (MCTSNode):      parent node that led to this node.
        play (str or Card):     last play that directly led to this node.
        wins (int):             win counter for active player in parent node.
        visits (int):           total number of times this node was visited.
        visits_per_play (list): vitsits per available legal play. 
        children (list):        children nodes which have this node as parent.
        expanded_plays (list):  plays expanded from this node.
        active_player (int):    next player to play in this node's game state.
    """
    def __init__(self, state, parent=None, play=None):
        """
        Initializer.

        Args:
            state (GameState):  game state at this node.
            parent (MCTSNode):  parent node that led to this node.
            play (str or Card): declaration or card played, that directly led
                                to this node.
        """
        self.parent = parent    # parent of this node
        self.play = play        # play that led directly to this node.
        self.children = []      # children nodes with this node as parent.
        self.wins = 0           # wins of active player in parent node.
        self.visits = 0         # number of times this node was visited.

        # remember who is selecting plays in the state belonging to this node
        # => update the wins counter in the children with the rewards for this
        #    player.
        self.active_player = state.next_player

        # NOTE: REMOVED
        # (because it changes with each rollout depending on DETERMINISATION)
        # legal moves possible from this node, but not evaluated yet.
        # self.untried_plays = state.get_legal_plays()

        # NOTE: NEW
        # plays which already have been expanded from this node.
        self.expanded_plays = []

        # NOTE: NEW
        # counts visits of this node per legal play available in a rollout.
        # will be used in the UCB1 calculation for each child instead of just
        # using the 'visits' counter (subset-armed bandit).
        self.visits_per_play = defaultdict(int)

    def select_child_uct(self, legal_plays, temperature):
        """
        Select child using Upper Confidence Bound for Trees (UCT).
        
        Max-N selection: Choose the child node that is in the legal plays list
                         and maximizes the UCT score for the player
                         WHO IS CURRENTLY MAKING THE CHOICE.

        Calculates the UCB1 for each child in its children list which also
        corresponds to a play in the legal plays list and returns the child
        node with the highest UCB1.

        Args:
            legal_plays (list):     legal plays available in this state.
            temperature (float):    temperature in UCB1 calculation.

        Returns:
            MCTSNode:               child node with highest UCB1.
        """

        def uct_score(child):
            """
            Calculate the Upper Confidence Bound (UCB1) for one child.

            Then searching a path through the tree, we have to decide at each
            node, which of its child nodes (legal plays) to select next.  We
            select the child node with the highest 'Upper Confidence Bound for
            Trees' (UCT) score which is the sum of an exploitation- and
            exploration-part.
            The exploitation part is the win-rate calculated as 'wins / visits'
            from the statistics counters in each of the considered child nodes,
            i.e. the more wins we have seen following this move, the higher the
            chance to follow the path through this node again.
            To avoid that we just follow a narrow path through the tree, which
            was preset by an early lucky success, the exploration part is
            calculated as squrt(log(N)/n), where N is the total number of
            'visits' counted in the parent node and n the number of 'visits'
            counted in this child node. I.e. the exploration part grows bigger
            the less a node (play) has been used in rollouts. The exploration
            part is further adapted by a weight factor called the temperature.
            A high temperature means more exploration and a broader tree, while
            a low temperature means more exploitation, i.e a more focused
            search along fewer paths.

            NOTE: in ISMCTS the opponents have different sets of legal plays
                  available with each rollout, due to the redistribution of the
                  unknown opponent cards at the beginning of each rollout
                  (DETERMINISATION). I.e. cards which appear for some reason
                  less frequent in the hand of an opponent, will get
                  overexplored, if we use the usual UCB1 formula. Therefore,
                  each node has to increment a counter per legal play available
                  in this rollout, whenever its 'visits' counter is incremented
                  during BACKPROPAGATION and we use the 'visits_per_play' count
                  for the corresponding child to calculate the exploration bonus.

            Args:
                child (ISMCTSNode):    child node.

            Returns:
                float:  Upper Confidence Bound 1 (UCB1).
                
            """
            # Win rate calculated for the decision maker
            # (= active player in parent node)
            win_rate = child.wins / child.visits
            bonus = (temperature
                    * math.sqrt(math.log(self.visits_per_play[str(child.play)])
                                / child.visits))
            return win_rate + bonus

        # only consider children corresponding to legal plays during this
        # rollout
        legal_children = [child for child in self.children
                          if child.play in legal_plays]
        # return child node with maximum UCB1.
        return max(legal_children, key=uct_score)

    def add_child(self, play, next_state):
        """
        Creates a child node.

        Args:
            play (str or Card):     play applied to current state, to get to
                                    the next state.
            next_state (GameState):     corresponding state in child node.

        Returns:
            ISMCTSNode:     new child node.
        """
        # create child node of current node reached by applied play.
        # corresponds to next state reach if play is applied to current state.
        child = ISMCTSNode(next_state, self, play)
        # append the new node to the list of this node's children
        self.children.append(child)
        # append the play to the list of expanded plays.
        self.expanded_plays.append(play)
        return child

    def update_wins(self, score):
        """
        Update the win counter.

        If this node was on the path between the root node (for which we try to
        find the best possible play) and the new child node created for this
        rollout, we have to update it's win counter with the result of the
        rollout (simulation using randomly selected legal plays).
        NOTE: we don't have to increment the 'visits' and 'visits_per_play'
              counts, because that was already done during SELECTION.
        As result of the simulation we get the card points for each player,
        which we've converted to a score of 0.0 to 1.0 per player (e.g. a team
        has gotten all 157 card points, both players get a score of 1.0).
        If this node is not the root node (i.e. if this node has a parent),
        add the reward received by the active player in the parent node (i.e.
        the player who selected the play which led to this node) in the
        simulation to the 'wins'-counter in this node.

        Args:
            score (list):       points converted to rewards (0.0 ... 1.0) per
                                player from rollout simulation.
        """
        # add the reward for the active player in the parent node to the
        # 'wins' counter.
        if self.parent is not None:
            # we cannot do this for the root node (no parent)
            for p in  range(NOF_PLAYERS):
                if p == self.parent.active_player:
                    self.wins += score[p]

    def show_select(self, legal_plays, temperature, play):
        """
        Show details for SELECT phase in this node.

        Args:
            legal_plays (list):     list of legal plays available in current
                                    state.
            temperature (float):    temperature in UCB1 calculation.
            play (Card):            selected play.
        """
        uct_scores = []
        # get a list of children reached via legal plays from this state
        legal_children = [child for child in self.children
                          if child.play in legal_plays]
#        print("### visits_per_play: ",end='')
#        for child in legal_children:
#            print(f"{str(child.play)} :{self.visits_per_play[str(child.play)]} ",
#                   end='')
#        print()
        for child in legal_children:
            # calculate UCB1
            win_rate = child.wins / child.visits
            bonus = (temperature
                    * math.sqrt(math.log(
                        self.visits_per_play[str(child.play)])
                        / child.visits))
            ucb1 = win_rate + bonus
            uct_scores.append(f"{str(child.play)} :{ucb1:.2f}")

        print(f"P{self.active_player + 1}:"
              f" {' '.join(uct_scores)}")
        print(f"SELECT: {str(play)}")

    def show_expand(self, unexpanded, play):
        """
        Show details for EXPAND phase in this node.

        Args:
            play (str or Card): play selected from legal unexpanded plays.
        """
        print(f"P{self.active_player + 1}:"
              f" {'  '.join([str(p) for p in unexpanded])} ")
        print(f"EXPAND: {str(play)}")

    def is_not_expandable(self, legal_plays):
        """
        Check if node is not expandable.

        Args:
            legal_plays (list):     legal plays available in this state.

        Returns:
            bool:   True => has no expandable plays. 
        """
        return all([p in self.expanded_plays for p in legal_plays])

class ISMCTSAgent(Agent):
    """
    Implementation of Slalom-Jass-Agent using SO-ISMCTS.

    We use Single-Observer Information Set Monte Carlo Tree Search (SO-ISMCTS)
    to implement an agent playing the game of Slalom-Jass as imperfect
    information game, i.e. an agent who doesn't know the other players' cards.
    
    Attributes:
        num_rounds (int):       number of rollouts.
        simple (bool):          True => use lightweight heuristics.
        temperature (float):    weight factor for exploration value.
        log_tree(bool):         True => show tree.
        max_depth (int):        show tree max depth
        log_nlwt (bool):        True => nodes, levels, wins, time.
        show_tricks(int):       show rollout details for this trick.
        show_player (int):      show details for this player.
    """
    def __init__(self, num_rounds, simple=False, temperature=1.6,
                 log_tree=False, max_depth=3, log_nlwt=False, show_trick=-2,
                 show_player=-1):
        """
        Initializer.

        Args:
            num_rounds (int):       number of rollouts.
            temperature (float):    weight factor for exploration value.
            simple (bool):          True => use lightweight heuristics.
            log_tree(bool):         True => show tree.
            max_depth (int):        show tree max depth
            log_nlwt (bool)         True => nodes, levels, wins, time.
            show_trick (int):       show rollout details for this trick.
            show_player (int):      show details for this player.
        """
        Agent.__init__(self)        # base class initializer.
        self.num_rounds = num_rounds
        self.temperature = temperature
        self.simple = simple
        self.log_tree = log_tree
        self.max_depth = max_depth
        self.log_nlwt = log_nlwt
        self.show_trick = show_trick
        self.show_player = show_player

    def set_temperature(self, temperature):
        """
        Set temperature.

        Args:
            temperature (float):    exploration/exploitation rate.
        """
        self.temperature = temperature

    def save(self, filename):
        """
        Save agent type and parameters to json-file.

        Args:
            filename (str):     filename.
        """
        data = {
            "type": "ismcts",
            "num_rounds": self.num_rounds,
            "temperature": self.temperature,
            "simple": self.simple,
            "log_tree": self.log_tree,
            "max_depth": self.max_depth,
            "log_nlwt": self.log_nlwt,
            "show_trick": self.show_trick,
            "show_player": self.show_player
        }
        # write data to json-file.
        if not filename.endswith('.json'):
            raise ValueError (
                "Filename must have extension '.json' => json-file!")
        json_str = json.dumps(data, indent=4)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)

    @staticmethod
    def simulate_random_game(game, simple=False):
        """
        Simulate game with random or simple bots selecting legal plays.

        Args:
            game (GameState):   game state from which the simulation starts.
            simple (bool):      False => Randombot, True => SimpleBot.

        Returns:
            list:     penalty points per player.
        """
        if simple:
            # agents selecting legal moves using lightweight heuristics.
            bots = [SimpleBot(nof_eval_games=0) for _ in range(NOF_PLAYERS)]
        else:
            # agents selecting legal moves at random.
            bots = [RandomBot() for _ in range(NOF_PLAYERS)]

        while not game.is_over():
            bot_play = bots[game.next_player].select_play(game)
            game = game.apply_play(bot_play)
        # return card points per player
        return game.count_points()

    def select_play(self, game_state):
        """
        Select legal play with Single-Observer Information Set MCTS.

        ISMCTS-agent only knows its own cards, but not the cards in the hands
        of the other players (=> imperfect information game).
        Therefore, it uses the additional DETERMINISATION phase at the start of
        each rollout to select a new random card distribution for the opponent
        cards. It uses the game_info module to randomize the opponent cards
        according to the information gathered in previous turns (e.g. opponent
        couldn't follow suit).
        During the SELECTION phase, it compares the plays leading to child
        nodes (= expanded plays) to the legal plays in the current game state.
        Only if all available legal plays are matched by a child node, UCT is
        used to select a child node. Note, that calculation of UCB1 has changed
        (subset-armed bandit), therefore a 'visits_per_play' counter has to be
        incremented for each available legal play in the selecting node after
        selection (but before moving to the selected node).
        If a node has been found, where not all available legal plays are
        matched by a child node, a new child for one of the unmatched legal
        plays will be added and a SIMULATION will be run from this new node.
        The result of the simulation will be bubbled up the tree during
        BACKPROPAGATION (=> each node passed during SELECTION plus the newly
        added node), i.e. add the reward for the active player in their parent
        node to their 'wins' counter. NOTE, that we already updated the 'visits'
        counters on the way down.

        Args:
            game_state (GameState):     game state for which we want to find
                                        the best next move.

        Returns:
            str or Card:    Best legal play possible from this game state.
        """
        # get the legal plays available to this agent (=Single-Observer)
        # NOTE: the observer always knows all his cards => legal plays.
        legal_plays = game_state.get_legal_plays()
        if len(legal_plays) == 1:
            # only 1 legal play => no need to build a tree
            return legal_plays[0]

        # create the root node for the search tree
        root_node = ISMCTSNode(game_state)

        nof_nodes = 0       # count number of nodes in tree
        max_levels = 0      # max number of tree levels

        start_time = time.time()    # get start time

        # loop through the specified number of rollouts.
        for i in range(self.num_rounds):
            # print more debug info for specified trick and player
            if (game_state.tricks == self.show_trick
                and game_state.next_player == self.show_player):
                print(f"\nROLLOUT {i + 1}")

            # start each search at the root node
            node = root_node

            # 1. DETERMINISATION: Make a clone of the root state, with cards
            #    randomly redistributed according to the publicly known game
            #    info, i.e. the next player (= this agent) keeps his own
            #    (known) cards while the unknown cards in the hands of the
            #    other players are redistributed.
            #    This state will be changed during this rollout (until a
            #    terminal state is reached), while the original root state
            #    stays unchanged.
            state = game_state.clone_and_randomize()

            if (game_state.tricks == self.show_trick
                and game_state.next_player == self.show_player):
                # print more debug info for specified trick and player.
                print("\nDETERMINISATION:")
                state.print_state()
                print()

            # get list of available legal plays in root state
            legal_plays = state.get_legal_plays()

            # 1. SELECT: Move down the tree using UCT until we hit a node with
            #    unexpanded legal plays or a terminal node (no legal plays).
            while legal_plays and all([p in node.expanded_plays
                                      for p in legal_plays]):
                # all legal plays have already been expanded into child nodes.
                # => use UCT to select child node with highest UCB1
                selected_node = node.select_child_uct(legal_plays,
                                                      self.temperature)

                # show debug info for specified trick and player
                if (game_state.tricks == self.show_trick
                    and game_state.next_player == self.show_player):
                    node.show_select(legal_plays, self.temperature,
                                     selected_node.play)

                # increment the 'visits' and 'visits_per_play' counts in the
                # current node.
                node.visits += 1
                for play in legal_plays:
                    # only for play's which were available in this SELECTION
                    node.visits_per_play[str(play)] += 1

                # move to the selected node
                node = selected_node

                # apply play which leads to child to the current state
                # => clone of original game enters corresponding (child) state.
                state = state.apply_play(node.play)

                # and get the legal plays available in the new state
                legal_plays = state.get_legal_plays()

            # 2. EXPAND: if we get here, we found a node, where not all
            #    available legal plays have been expanded into child nodes, or
            #    we have found a terminal node, i.e. there are no more legal
            #    plays => expand one random legal play which is not in the
            #    expanded_play set of this node.
            if legal_plays:
                # not a terminal node => get a list of unexpanded legal plays
                unexpanded = [p for p in legal_plays
                              if p not in node.expanded_plays]

                # randomly select one of the unexpanded legal plays
                play = random.choice(unexpanded)

                # show debug info for specified trick and player
                if (game_state.tricks == self.show_trick
                    and game_state.next_player == self.show_player):
                    node.show_expand(unexpanded, play)

                # apply this play to the state of the cloned game
                state = state.apply_play(play)
                # create a new child node corresponding to the new state of
                # the cloned game.
                new_node = node.add_child(play, state)
                nof_nodes += 1

                # NOTE: we no longer update the 'visits' and 'visits_per_play'
                # counts during BACKPROPAGATION but in SELECTION or EXPANSION
                # (because we need 'legal_plays' for the current state).
                # => update 'visits' and 'visits_per_play' in the parent node.
                node.visits += 1
                for p in legal_plays:
                    node.visits_per_play[str(p)] += 1

                # move to the new child node
                node = new_node
                # update the 'visits' count in the new child node
                node.visits += 1

            # 3. SIMULATE (Rollout): Fast simulation to a terminal game state.
            # simulate a game with agents selecting plays at random or using
            # simple heuristics, from this node's game state.
            points = self.simulate_random_game(state, self.simple)

            if (game_state.tricks == self.show_trick
                and game_state.next_player == self.show_player):
                # show debug info for specified trick and player
                results = [f"P{p + 1}:{points[p]}" for p in range(4)]
                print(f"SIMULATE: {' '.join(results)}")

            # convert card points into score from 0.0 to 1.0 per team.
            score = points_to_score(points)

            # 4. BACKPROPAGATE: bubble the score up the tree through all
            #    parents to the root.
            levels = 0
            while node is not None:     # stop at the root (has no parent)
                # add reward for active player in parent node to 'wins' count
                # in current node.
                # NOTE: the 'visits' and 'visits_per_play' count was already
                # incremented during SELECTION or EXPANSION.
                node.update_wins(score)
                node = node.parent      # go up the tree to the parent
                levels += 1             # count levels back to the root.
            # keep max number levels
            max_levels = max(max_levels, levels)

        # print whole tree for specified player
        if self.log_tree and game_state.next_player == self.show_player:
            show_tree(root_node, max_depth=self.max_depth)

        # after all rollouts have been done, check the win counters in root's
        # children to find the best move.
        best_play = None
        best_win_ratio = -1.0   # best 'wins / visits' ratio.
        for child in root_node.children:
            # get the win/visits ratio for the next player (root's game state)
            child_win_ratio = child.wins / child.visits
            if child_win_ratio > best_win_ratio:
                best_win_ratio = child_win_ratio
                best_play = child.play  # play leading from root to this child.

        duration = time.time() - start_time

        # print number of nodes, number of levels,
        # and win percentage of selected move for specified player.
        if self.log_nlwt and game_state.next_player == self.show_player:
            print(f"\n   nodes:{nof_nodes} levels:{max_levels - 1} "
                  f"wins:{100 * best_win_ratio:2.1f}% "
                  f"time:{1000 * duration / self.num_rounds:.2f} ms/rollout\n")
        return best_play


def ismcts_vs_simple():
    """
    Let ISMCTSAgent play against SimpleBot.

    NOTE: When looking at rollout details,

                !!! DO NOT FORGET TO LOOK AT THE WHOLE PATH !!!

          i.e. if P1 has selected Q♣ as 1st card and we expand 3♣ from P2, it's
          correct, that if in the next rollout P1 selects 6♣, P2 still could
          have 3♣ as unexpanded play, because this is another node reached over
          6♣ instead of Q♣.
    """
    # create gamestate for new round
    game = GameState.new_round(3)
    # deal cards and determine starting player
    game.start_round()
    print("------------------------------------------------------------------------------")

    # create 2 ISMCTSAgent using 100 rollouts and temperatur=0.7.
    agent1 = ISMCTSAgent(100, temperature=0.7, simple=True, log_tree=False,
                         max_depth=3, log_nlwt=False, show_trick=-2,
                         show_player=-1)
    agent3 = ISMCTSAgent(100, temperature=0.7, simple=True, log_tree=False,
                         max_depth=3, log_nlwt=False, show_trick=-2,
                         show_player=-1)

    # create 2 bots using simple heuristic to select moves.
    agent2 = SimpleBot()
    agent4 = SimpleBot()
    agents = [agent1, agent2, agent3, agent4]
    game.print_state()
    print()

    while not game.is_over():
        # play until all cards have been played
        play = agents[game.next_player].select_play(game)
        if game.tricks < 0:
            # Declaration phase
            print(f"   {game.players[game.next_player].name}: {play}")
        else:
            game.print_state()
            # obenabe/undeufe indicator
            ob = '\u2193' if game.higher_card_wins() else '\u2191'
            if len(game.table) == 0:
                print(f"{ob}  Trick:   {str(play)}")
            else:
                print(f"{ob}  Trick:   {game.show_table_cards()}  {str(play)}")

        # apply selected play to game state
        game = game.apply_play(play)
        print("------------------------------------------------------------------------------")

    # calculate score
    if game.obenabe:
        print("OBENABE:")
    else:
        print("UNDEUFE:")
    print("-------")
    score = game.count_points()
    for p in range(NOF_PLAYERS):
        player = game.players[p]
        print(f"{player.name}: {score[p]:>3}")
    print()
    print(f"Team13:  {score[0] + score[2]:>3}")
    print(f"Team24:  {score[1] + score[3]:>3}")


if __name__ == '__main__':
    # !!!NOTE!!!
    # To avoid ModuleNotFoundError start it from '~/Projects/slalom_jass/src'
    # with:
    # python3 -m slalom_jass.agents.ismcts

    # run game with 1 ismcts-agent and 3 simple agents.
    ismcts_vs_simple()
