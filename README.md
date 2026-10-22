# Introduction #

This is a **Python** implementation of the trump-variant **Slalom** from the
Swiss card game **Coiffeur-Jass**. This is a terminal-only implementation, i.e.
there's no GUI. The main target was, to implement a **Single-Observer
Information Set Monte Carlo Tree Search (SO-ISMCTS)** agent. The performance of
different agents can be tested, by either letting them against each other or a
human player.

# Slalom-Jass Rules #
'Jass' is the national card game of Switzerland. It's usually played with a
Swiss-German deck of 36 cards, i.e. the suits 'Rose', 'Schilte', 'Eichle', 'Schelle',
and the ranks '6', '7', '8', '9', '10, 'Under', 'Ober', 'König', 'Ass'. But it
can also be played with a French deck. We use the French deck in this implementation,
since 'Hearts', 'Spades', 'Diamonds', and 'Clubs' can be easily displayed using
unicodes.


| Swiss   |  French  |   |
|---------|----------|---|
| Schelle | Hearts   | ♡ |
| Eichle  | Spades   | ♠ |
| Schilte | Diamonds | ♢ |
| Rosen   | Clubs    | ♣ |
| 6       | 6        |   |
| 7       | 7        |   |
| 8       | 8        |   |
| 9       | 9        |   |
| 10      | 10       |   |
| Under   | J        |   |
| Ober    | Q        |   |
| König   | K        |   |
| Ass     | A        |   |


One of many Jass-variants is called Coiffeur-Jass. The name means hairdresser
in French but actually comes from the similar sounding 'quoi faire' (what to do?).
It is a trick-taking game for 4 players, where players sitting opposite of each
other are building a team. The game is played over several rounds, where each
round one of the players has to select a diffent different trump variant:
- Eichle
- Rosen
- Schilten
- Schellen
- Obenabe (no trump, 'Ass' is the highest, '6' is the lowest card)
- Undeufe (no trump, '6' is the highest, 'Ass' is the lowest card)
- ...

Starting with the player to the right of the dealer (swiss card games are
played counterclockwise) players select one of the variants not played yet or
pass ('Schiebe'). If all 4 players pass, the player to the right of the dealer
is forced to make a selection. As soon as a player selects a variant, this
player plays the 1st card to the 1st trick. The player who wins the trick plays
the 1st card to the next trick, and so on.

'Slalom' is a variant, which is played without trump, but the rank order
alternates between 'Obenabe' (top down) and 'Undeufe' (bottom up). The player
selecting 'Slalom' has also to declare, if the 1st trick is played 'Obenabe' or
'Undeufe'. This also determines the card values for the whole round:


  | Card    |  Obenabe  |  Undeufe  |
  |:--------|:---------:|:---------:|
  | 6       |     0     |    11     |
  | 7       |     0     |     0     |
  | 8       |     8     |     8     |
  | 9       |     0     |     0     |
  | 10      |    10     |    10     |
  | Under   |     2     |     2     |
  | Ober    |     3     |     3     |
  | König   |     4     |     4     |
  | Ass     |    11     |     0     |


The game itself is played like any other trick taking game without trump, i.e.
if possible players must follow the suit led (suit of the 1st card played to
this trick), If a player has no cards of the led suit, he may play any card
(and lose this trick).

Remember that card order alternates between tricks:

| Trick    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|----------|---|---|---|---|---|---|---|---|---|
| Obenabe  | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ |  
| Undeufe  | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ | ↓ | ↑ |

After the whole round has been played, the teams sum up the points for the
cards in their tricks (see table above). The team which has won the last trick
gets an addtitional 5 points.

# Installation #

## Python ##
Install Python3:  
-> <https://realpython.com/installing-python/>

## Slalom-Jass

Clone the 'slalom_jass' repository from **github**  
-> git@github.com:trachwo/slalom_jass.git

or download the zip-file **(green '<> Code' button)**

To verify the installation, go to the 'slalom_jass/src' directory and run a
short test:

    $ cd my_path/slalom_jass/src
    $ python3 bot_vs_bots --bot13 simple --bot24 random -n 5

You should immediatly see something similar to the output below:
```
          |     |     |     |     |    Average    |  
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time  
----------+-----+-----+-----+-----+-------+-------+-------  
      1/5 | 157 |   0 |   0 |   0 |  157  |    0  | 0.0s  
      2/5 |  64 |   0 |  93 |   0 |  157  |    0  | 0.0s  
      3/5 |   0 |   0 | 157 |   0 |  157  |    0  | 0.0s  
      4/5 |  30 |  62 |  51 |  14 |  138  |   19  | 0.0s  
      5/5 |  59 |   0 |  77 |  21 |  137  |   19  | 0.0s  
-------------------------------------------------------------------------------
Player1:                  310  62  
Player2:                   62  12  
Player3:                  378  75  
Player4:                   35   7  
  
>Player1 + Player3:        688 137  
>Player2 + Player4:         97  19  
===============================================================================
```



# Files

After installation, you should see the following file structure:

>      slalom_jass/
>           |
>           +--- README.md
>           |
>           +--- LICENSE
>           |
>           +--- src/
>                 |
>                 +--- bot_vs_bots.py
>                 |
>                 +--- human_vs_bots.py
>                 |
>                 +--- slalom_jass/
>                 |          |
>                 |          +--- __init__.py
>                 |          |
>                 |          +--- cards.py
>                 |          |
>                 |          +--- game/
>                 |          |      |
>                 |          |      +--- __init__.py
>                 |          |      |
>                 |          |      +--- player.py
>                 |          |      |
>                 |          |      +--- info.py
>                 |          |      |
>                 |          |      +--- scenario.py
>                 |          |      |
>                 |          |      +--- game.py
>                 |          |
>                 |          +--- agents/
>                 |                 |
>                 |                 +--- __init__.py
>                 |                 |
>                 |                 +--- base.py
>                 |                 |
>                 |                 +--- human.py
>                 |                 |
>                 |                 +--- naive.py
>                 |                 |
>                 |                 +--- mcts_cheater.py
>                 |                 |
>                 |                 +--- ismcts.py
>                 +--- data
>                        |
>                        +--- agents
>                        |       |
>                        |       +--- human.json
>                        |       |     
>                        |       +--- random.json
>                        |       |     
>                        |       +--- simple.json
>                        |       |     
>                        |       +--- cheater.json
>                        |       |     
>                        |       +--- ismcts.json
>                        |
>                        +--- scenarios
>                                 |
>                                 +--- scenario_1.cs
>                                 |
>                                 +--- scenario_2.cs

**README.md**: This file.

**LICENSE**: MIT License.

**src/**: Python source code:
- **bot_vs_bots.py**: Let bots play against themselves.
- **human_vs_bots.py**: Let human player play against bots.

**src/slalom_jass**: slalom_jass sub-modules:
- **__init__.py**: Makes *slalom_jass* a Python package.
- **cards.py**: Implementation of playing cards.

**src/slalom_jass/game/**: Game logic sub-module:
- **__init__.py**: Makes *game* a Python package.
- **player.py**: Player class keeping track of player hands.
- **info.py**: GameInfo class keeping track of played cards and suits not
               followed.
- **scenario**: Scenario class used to load player hands from CSV-file.
- **game**: GameState class containing the Slalom-Jass state machine.

**src/slalom_jass/agents/**: Game agents sub-module.
- **__init__.py**: Makes *agents* a Python package.
- **base.py**: Agent class => base class for all game agents.
- **human.py**: Agent representing a human player => user interface.
- **naive.py**: RandomBot class (random play selection) and SimpleBot class
                (using simple heuristic for play selection).
- **mcts_cheater.py**: MCTSCheater class => MCTS agent with perfect information
                       (i.e he is looking at other players' cards!)
- **ismcts.py**: ISMCTSAgent class => Single-Observer Informatin Set MCTS agent.

**src/data/agents**: Agent configuration files.
- **human.json**: Human player configuraion.
- **random.json**: RandomBot configuration.
- **simple.json**: SimpleBot configuration.
- **cheater.json**: MCTSCheater configuration.
- **ismcts.json**: ISMCTSAgent configuration.

**src/data/scenarios**: Scenarios with preset player hands.
- **scenario_1.cs**: Example for scenario, where all hands are specidfied.
- **scenario_2.cs**: Example for scenario, where only one hand is specified.

# Agents #

## human ##

Implements a primitive user interface for **human_vs_bots.py**. Whenever it is the human player's turn, he can select from a list of plays by entering a number.
```
------------------------------------------------------------------------------
Trick 1: Obenabe
------------------------------------------------------------------------------
*  Player1: 9♣  J♣  7♢  7♡  K♡  8♠  10♠  Q♠  K♠
   Player2: A♣  8♢  J♢  K♢  6♡  10♡  J♡  Q♡  A♡
   Player3: 7♣  8♣  K♣  10♢  8♡  6♠  7♠  9♠  A♠
   Player4: 6♣  10♣  Q♣  6♢  9♢  Q♢  A♢  9♡  J♠
   0:9♣  1:J♣  2:7♢  3:7♡  4:K♡  5:8♠  6:10♠  7:Q♠  8:K♠ ? 
```

## random ##

Selects all its plays randomly (declarations and card play).  
It is used for fast simulation in MCTS and as lower benchmark for other agents.

## simple ##

Selects its card plays using simple heuristics. Declarations (Schiebe, Obenabe, Undeufe) are made either after playing a specified number of evaluation games, or randomly. It is expected to play better than **random** and is still fast enough to be used for fast simulation in MCTS (set the number of evaluation games to 0).

### SimpleBot heuristics ###
**Playing 1st**:
1. play a bock.
2. play the least valuable card, avoiding future bock-cards and high-value
   cards ('8' and '10).

**Playing 2nd**:
1. can follow suit and has bock of this suit => play bock.
2. play the least valuable card, avoiding future bock-cards and high-value
   cards ('8' and '10).

**Playing 3rd**:
1. if 1st player (partner) has played the bock, play the most valuable card,
   avoiding future bock-cards.
2. if 1st player has currently won the trick, without playing bock:
    1. if 4th player cannot have better card, play the most valuable card,
       avoiding future bock-cards.
    2. if 4th player could have better card than 1st, but you have the bock,
       play it.
    3. play the least valuable card, avoiding future bock-cards and high-value
       cards ('8' and '10)
3. if 2nd player has won the trick, but you have the bock, play it.
4. play the least valuable card, avoiding future bock-cards and high-value 
   cards ('8' and '10).

**Playing 4th**:
1. if 2nd player (partner) has won the trick, play the most valuable card,
   avoiding future bock-cards.
2. if 2nd player has not won the trick:
    1. if you can follow suit, play the worst card which still wins the trick.
    2. if you cannot follow suit or win the trick, play the least valuable
       card, avoiding future bock-cards and high-value cards ('8' and '10).

## cheater ##

Selects all plays using **Monte Carlo Tree Search (MCTS)** for **perfect
information** games. It cheats by looking at the cards of the other players to
make its decision. Therefore, it's not really a Slalom-Jass-AI, but still can
be useful as upper benchmark, since it is expected to play better than all
other agents.

### Monte Carlo Tree Search ###

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

A very good introduction to MCTS can be found here:  
https://medium.com/@quasimik/monte-carlo-tree-search-applied-to-letterpress-34f41c86e238

Most MCTS examples found online are about 2 player games with perfect
information like 'Connect 4' or 'Go'. But 'Slalom-Jass' is a 4-player game with
imperfect information, i.e. players only know their own cards (=> available
actions). **cheater** adapts MTCS for 4 players, which knows not only its own,
but also the other players' cards, i.e. we treat 'Slalom-Jass' as a perfect
information game.

In MCTS we build a tree over multiple iterations (rollouts) starting at the
root node, which corresponds to the game state for which we want to find the
best next play. In the first few iterations we just randomly select one of the
legal plays (e.g. cards which can be played) in the root state and expand it
to a new child node of the root, i.e. we apply the selected play to a clone of
the root state (i.e. the original game is not changed) to get to the child
state. From this new child state we then run a fast simulation by randomly (or
using simple heuristics) selecting legal plays until the (simulated) game is
finished and we can update the reward statistics of the child node according to
the outcome of the simulation (e.g. won =>  +1  or  +120/157).  
If all children of the root node have been expanded, we have to select one of
them and continue building the tree from there (i.e. next we consider the best
move an opponent could select as answer to our play). From this point on each
rollout has the following 4 phases:

1. **Selection**:
   Starting at the root we walk down the tree to find a node with untried plays
   (= unexpanded children). To do this, we could just select at each completely
   expanded node, the child with the best rewards statistics. But maybe this
   was just a bad play with a lucky outcome (-> random simulation) and there
   are much better plays we will no longer find (multi-armed bandit dilemma).
   Therefore, we use the **Upper Confidence Bound for Trees (UCT)** to decide
   which node to go next. UCT calculates for each child a value (UCB1) which
   consists part on the reward statistics (**explointation**, i.e. a node is
   selected more often, if it showed good results in previous rollouts) and
   part on the number of times it was selected so far (**exploration**, i.e.
   a child is selected because it has not been selected as often as the other
   siblings).

2. **Expansion**:
   We have found a node with untried plays during **Selection**, now we
   randomly select one of the untried plays and apply it to the clone of the
   game state to create a new child node.

3. **Simulation**:
   From the game state of the new child node created during **Expansion**, we
   run a fast simulation by randomly (or using simple heuristics) selecting
   legal plays until we reach a terminal state (winners and losers found).

4. **Backpropagation**:
   The result of the simulation is bubbled up the tree to the root node,
   through every node passed down during **Selection**. In a 2 player game we
   just increment the win and rollout counters in these nodes. The rollout
   counter is incremented in every node passed, while the win counter is only
   incremented in children which have the winner as parent (e.g. if the player
   who selects a card in the root state wins a simulation, the win counter in
   the selected child is incremented, but the next child selected from there,
   corresponds to a play selected by the loser of the simulation and is
   therefore not incremented.  
   To adapt this for a 4-player game, we backpropagate a list of rewards
   (0.0 - 1.0) per player and each passed node adds the reward for the player
   selecting a play in the parent state (node) to its reward statistics.
   Rewards are calculated, by summing up the card points of players per team
   and dividing by the number of total points (157).

## ismcts ##

Selects all plays using **Single-Observer Information Set Monte Carlo Tree
Search (SO-ISMCTS)** for **imperfect information** games. It only nows its own
cards and public informatin like already played cards and suits not followed by
a player. It is expected to play better than **simple** but not as good as
**cheater**.

### Single-Observer Information Set MCTS ###

The IEEE paper about **Information Set Montecarlo Tree Search** can be found at:  
https://eprints.whiterose.ac.uk/id/eprint/75048/


We have to make the following changes to the multiplayer MCTS algorithm we used
for **cheater** (= multiplayer MCTS with perfect information) in order to use
MCTS for a 4-player game with imperfect information:

1. **Determinisation**:
   This is a new phase, in which we randomly redistribute the (unknown)
   cards of the other players before each rollout, while keeping our own
   (known) cards. We can use information gathered in previous turns of the game
   for the redistribution (e.g. if a player couldn't follow a suit in a previous
   turn, he's out of that suit and doesn't get any cards of that suit during
   redistribution).

2. **Selection**:
   Due to the random redistribution of opponent cards, it is now possible, that
   a node (where one of the opponents selects the play) which was fully
   expanded in a previous rollout, has now new unexpanded plays available in
   the current rollout. I.e. we can no longer rely on a fixed 'untried plays'
   or 'children' list, but have to get a list of legal plays from the current
   game state and compare it to the list of expanded plays in each traversed
   node. Only if all legal plays in the current game state (with redistributed
   opponent cards) have been expanded into child nodes, can we use the **Upper
   Confidence boundery for Trees (UCT)**, to move down the tree to one of the
   children.  
   **NOTE**, that the calculation of the Upper Confidance Boundary (UCB1) has
   also changed. If we would still use the number of times the parent was
   visited to calculate the exploration bonus, plays which appear seldomly in
   the list of legal plays for a node, will be overexplored. In the changed
   UCB1 calculation we have to replace the number of times the parent node was
   visited with the number of times the parent node was visited **and the child
   node was available**. This also means that we increment the 'visits' count
   in the **Selection** phase as long as the corresponding state and therefore
   its legal plays are available (otherwise we would have to store a clone of
   the state or at least the legal plays in the node).

3. ***Expansion**:
   As soon as we get to a node, where not every available legal play for the
   corresponding game state (with redistributed opponent cards) is already
   matched by a child node, we have to expand one of the unmatched legal plays
   into a new child node and run a simulation from there.

4. **Simulation**:
   The simulation phase is identical with vanilla MCTS, we use random selection
   or simple heuristics to bring the game to a terminal state and give the
   corresponding rewards (0.0 ... 1.0) to the winners and losers.

5. **Backpropagation**:
   Backpropagate the rewards dictionary up the tree, adding the corresponding
   reward (the one for the active player in the parent node, who made the
   decision to make this play, i.e. move to this node).
   **NOTE**: we no longer update the 'visits' count, because that was already
   done during **Selection** on the way down the tree (since we needed the
   legal plays per state to increment the 'visits_per_play' counters).


# Usage #