"""
Cheating 'Slalom-Jass' agent using Monte Carlo Tree Search (MCTS) algorithm.

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
actions). We 1st adapt MTCS for 4 players by implementing a cheating agent,
which knows not only its own, but also the other players' cards, i.e. we treat
'Slalom-Jass' as a perfect information game. In a 2nd step we then use Single-
Observer Information Set MCTS (SO-ISMCTS) to let an AI-agent select actions in
a real 4-player game of 'Slalom-Jass' (i.e. with imperfect information).
"""

import math
import time
import random
import json

from slalom_jass.agents.base import Agent
from slalom_jass.agents.naive import RandomBot, SimpleBot
from slalom_jass.game import GameState, NOF_PLAYERS

# list of symbols exported if a script calls 'from mcts import *'
__all__ = [
    'MCTSCheater',
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


class MCTSNode():
    """
    Node in the Monte Carlo Tree Search tree.

    Tracks the performance of play selections with random playouts.
    Each node corresponds to a certain state reached over 1 or more plays from
    the root state (node), which is the state for which we want to find the
    best play for the active player. In our case it's not necessary to store
    a clone of the corresponding state in the node. We just need the link to
    the parent node (previous state), the list of untried plays, and the list
    of children (expanded plays). In each rollout we search a way through the
    tree to a node with untried plays. One of these plays is then expanded into
    a new child node and a simulation using random plays is started from the
    corresponding state to find winners and losers. The rewards for winners and
    losers are backpropagated up the tree => update 'visits' and 'wins'
    counters in nodes passed on the way up to the root node.
    'visits' and 'wins' counters are used by the active player in the parent (!)
    node to decide which play (child node) to select next on the way to a node
    with untried moves. The UCT method calculating UCB1 from wins and visits
    counters is used to make these decisions.

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
        children (list):        children nodes which have this node as parent.
        active_player (int):    next player to play in this node's game state.
        untried_plays (list):   legal plays not tried from this node.
    """
    def __init__(self, state, parent=None, play=None):
        """
        Initializer.

        Args:
            state (GameState):  game state at this node.
            parent (MCTSNode):  parent node that led to this node.
            play (str or Card): declaration or card, that directly led to this
                                node.
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

        # legal moves possible from this node, but not evaluated yet.
        self.untried_plays = state.get_legal_plays()

    def select_child_uct(self, temperature):
        """
        Select child using Upper Confidence Bound for Trees (UCT).
        
        Max-N selection: Choose the child node that maximizes the UCT score for
                         the player WHO IS CURRENTLY MAKING THE CHOICE.

        Calculates the UCB1 for each child in its children list and returns the
        child node with the highest UCB1.

        Args:
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

            Args:
                child (MCTSNode):    child node.

            Returns:
                float:  Upper Confidence Bound 1 (UCB1).
                
            """
            # Win rate calculated for the decision maker
            # (= active player in parent node)
            win_rate = child.wins / child.visits
            bonus = (temperature
                    * math.sqrt(math.log(self.visits) / child.visits))
            return win_rate + bonus

        # return child node with maximum UCB1.
        return max(self.children, key=uct_score)

    def add_child(self, play, next_state):
        """
        Creates a child node and removes the play from untried list.

        Args:
            play (str or Card):     play applied to current state, to get to
                                    the next state.
            next_state (GameState):     corresponding state in child node.

        Returns:
            MCTSNode:    new child node.
        """
        # create child node of current node reached by applied play.
        # corresponds to next state reach if play is applied to current state.
        child = MCTSNode(next_state, self, play)
        # remove applied play from this node's list of untried plays.
        self.untried_plays.remove(play)
        # append the new node to the list of this node's children
        self.children.append(child)
        return child

    def update_counters(self, score):
        """
        Update the win counters.

        If this node was on the path between the root node (for which we try to
        find the best possible play) and the new child node created for this
        rollout, we have to update it's win counter with the result of the
        rollout (simulation using randomly selected legal plays) and we also
        have to increment its visits counter.
        As result of the simulation we get the card points for each player,
        which we've converted to a score of 0.0 to 1.0 per team (e.g. a team
        has gotten all 157 card points, both players get a score of 1.0).
        If this node is not the root node (i.e. if this node has a parent),
        add the reward received by the active player in the parent node (i.e.
        the player who selected the play which led to this node) in the
        simulation to the 'wins'-counter in this node.

        Args:
            score (list):       points converted to rewards (0.0 ... 1.0) per
                                player from rollout simulation.
        """
        # always increment the 'visits' counter.
        self.visits += 1
        # add the reward for the active player in the parent node to the
        # 'wins' counter.
        if self.parent is not None:
            # we cannot do this for the root node (no parent)
            for p in  range(NOF_PLAYERS):
                if p == self.parent.active_player:
                    self.wins += score[p]

    def show_select(self, temperature):
        """
        Show details for SELECT phase in this node.

        Args:
            temperature (float):    temperature in UCB1 calculation.
        """
        uct_scores = []
        for child in self.parent.children:
            # calculate UCB1
            win_rate = child.wins / child.visits
            bonus = (temperature
                    * math.sqrt(math.log(self.parent.visits) / child.visits))
            ucb1 = win_rate + bonus
            uct_scores.append(f"{str(child.play)} :{ucb1:.2f}")

        print(f"P{self.parent.active_player + 1}:"
              f" {' '.join(uct_scores)}")
        print(f"SELECT: {str(self.play)}")

    def show_expand(self, play):
        """
        Show details for EXPAND phase in this node.

        Args:
            play (str or Card): play selected from untried plays.
        """
        print(f"P{self.active_player + 1}:"
              f" {'  '.join([str(p) for p in self.untried_plays])} ")
        print(f"EXPAND: {str(play)}")


class MCTSCheater(Agent):
    """
    Implementation of cheating Slalom-Jass-Agent using MCTS.
    
    To avoid the problems caused by applying MCTS to games with imperfect
    information, we let our agent cheat (i.e. look at other players' cards).
    This is not an agent we should use as AI-bot to play against humans, but
    will be used as upper benchmark for other AI-agents to compare against.

    We still have to adapt the MCTS algorithm for use in a 4-player game, by
    changing the way the simulation results are backpropagated into the tree-
    nodes. In a 2-player game we just note the winner of the simulation and
    then increment the win-count in all nodes passed on the way to the node
    from which the simulation was started (if the winning player was the active
    player in the parent node, i.e. has selected the action leading to this
    node).
    In a 4-player game of Slalom-Jass the simulation returns a list of card
    points per player, which we will convert to scores between 0.0 and 1.0
    (per team) accumulated in the corresponding nodes. 

    Attributes:
        num_rounds (int):       number of rollouts.
        simple (bool):          True => use lightweight heuristics.
        temperature (float):    weight factor for exploration value.
        log_tree(bool):         True => show tree.
        max_depth (int):        show tree max depth
        log_nlwt (bool):        True => nodes, levels, wins, time.
        show_trick(int):        show rollout details for this trick.
        show_player(int):       show details for this player.
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
            "type": "mcts_cheater",
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
            bots = [SimpleBot() for _ in range(NOF_PLAYERS)]
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
        Select legal play with Monte Carlo Tree Search (MCTS).

        The Cheater-agent treats 'Slalom-Jass' as a deterministic game, i.e. it
        not only knows its own hand cards, but also (illegally) looks at the
        hands of the other players. Therefore, we can use the same algorithm as
        for perfect information games like 'Connect 4' or 'Go' but adapted for
        4 players.

        Args:
            game_state (GameState):     game state for which we want to find
                                        the best next move.

        Returns:
            str or Card:    Best legal play possible from this game state.
        """
        legal_plays = game_state.get_legal_plays()
        if len(legal_plays) == 1:
            # only 1 legal play => no need to build a tree
            return legal_plays[0]

        # create the root node for the search tree
        root_node = MCTSNode(game_state)

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

            # make a clone of the root state, this state will be changed during this
            # rollout (until a terminal state is reached), while the original root
            # state stays unchanged.
            state = game_state.clone()

            # 1. SELECT: Move down the tree using UCT until we hit a node with
            #            untried plays.
            while not node.untried_plays and node.children:
                # list of untried moves is empty and node has children
                # => use UCT to select child node with highest UCB1
                node = node.select_child_uct(self.temperature)

                # show debug info for specified trick and player
                if (game_state.tricks == self.show_trick
                    and game_state.next_player == self.show_player):
                    node.show_select(self.temperature)
                # apply play which leads to child to the current state
                # => clone of original game enters corresponding (child) state.
                state = state.apply_play(node.play)

            # if we get here, we found a node with unexpanded plays from which
            # we can expand the tree with a new node, or a terminal node.
            # 2. EXPAND: Pop one untried play to create a new tree branch
            if node.untried_plays:
                # randomly select 1 of the available plays
                play = random.choice(node.untried_plays)

                # show debug info for specified trick and player               
                if (game_state.tricks == self.show_trick
                    and game_state.next_player == self.show_player):
                    node.show_expand(play)
                # apply this play to the state of the cloned game
                state = state.apply_play(play)
                # create a new child node corresponding to the new state of the
                # cloned game and remove the applied play from the untried
                # plays list of the parent node.
                node = node.add_child(play, state)
                nof_nodes += 1

            # 3. SIMULATE (Rollout): Fast simulation to a terminal game state.
            # simulate a game with agents selecting plays at random or using
            # simple heuristics, from this node's game state.
            points = self.simulate_random_game(state, self.simple)
            if (game_state.tricks == self.show_trick
                and game_state.next_player == self.show_player):
                results = [f"P{p + 1}:{points[p]}" for p in range(4)]
                print(f"SIMULATE: {' '.join(results)}")

            # convert card points into score from 0.0 to 1.0 per team.
            score = points_to_score(points)

            # 4. BACKPROPAGATE: bubble the score up the tree through all
            #                   parents to the root.
            levels = 0
            while node is not None:     # stop at the root (has no parent)
                # update the visited and wins counters
                # (for active player in parent).
                node.update_counters(score)
                node = node.parent      # go up the tree to the parent
                levels += 1             # count levels back to the root.
            # keep max number levels
            max_levels = max(max_levels, levels)

        # print whole tree
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


def cheater_vs_simple():
    """
    Let MCTSCheater play against SimpleBot.

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

    # create MCTSCheater using 100 rollouts and temperatur=0.7.
    agent1 = MCTSCheater(100, temperature=0.7, simple=False, log_tree=False,
                         max_depth=3, log_nlwt=False, show_trick=-2,
                         show_player=-1)
    # create 3 bots using simple heuristic to select moves.
    agent2 = SimpleBot()
    agent3 = SimpleBot()
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
    # python3 -m slalom_jass.agents.mcts_cheater
    cheater_vs_simple()
