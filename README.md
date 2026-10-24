# Introduction #

This is a **Python** implementation of the trump-variant **Slalom** from the
Swiss card game **Coiffeur-Jass**. This is a terminal-only implementation, i.e.
there's no GUI. The main target was, to implement a **Single-Observer
Information Set Monte Carlo Tree Search (SO-ISMCTS)** agent. The performance of
different agents can be tested, by either letting them play against each other
or a human player.

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
| 6       | 6        | 6 |
| 7       | 7        | 7 |
| 8       | 8        | 8 |
| 9       | 9        | 9 |
| 10      | 10       |10 |
| Under   | Jack     | J |
| Ober    | Queen    | Q |
| König   | King     | K |
| Ass     | Ace      | A |


One of many Jass-variants is called Coiffeur-Jass. The name means hairdresser
in French but actually comes from the similar sounding 'quoi faire' (what to do?).
It is a trick-taking game for 4 players, where players sitting opposite of each
other are building a team. The game is played over several rounds, where in each
round one of the players has to select a different trump variant:
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

see <https://realpython.com/installing-python/>

## Slalom-Jass

Clone the 'slalom_jass' repository or downnload the zip-file from **github** at

<github.com/trachwo/slalom_jass>

with the green **'<> Code'** button.

To verify the installation, go to the 'slalom_jass/src' directory and run a
short test:

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots --bot13 simple --bot24 random -n 5

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
>                 +--- bots_vs_bots.py
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
- **bots_vs_bots.py**: Let bots play against themselves.
- **human_vs_bots.py**: Let human player play against bots.

**src/slalom_jass**: slalom_jass sub-modules:
- **__init__.py**: Makes *slalom_jass* a Python package.
- **cards.py**: Implementation of playing cards.

**src/slalom_jass/game/**: Game logic sub-module:
- **__init__.py**: Makes *game* a Python package.
- **player.py**: Player class keeping track of player hands.
- **info.py**: GameInfo class keeping track of played cards and suits not
               followed.
- **scenario.py**: Scenario class used to load player hands from CSV-file.
- **game.py**: GameState class containing the Slalom-Jass state machine.

**src/slalom_jass/agents/**: Game agents sub-module.
- **__init__.py**: Makes *agents* a Python package.
- **base.py**: Agent class => base class for all game agents.
- **human.py**: Agent representing a human player => user interface.
- **naive.py**: RandomBot class (random play selection) and SimpleBot class
                (using simple heuristic for play selection).
- **mcts_cheater.py**: MCTSCheater class => MCTS agent with perfect information
                       (i.e he is looking at other players' cards!)
- **ismcts.py**: ISMCTSAgent class => Single-Observer Information Set MCTS agent.

**src/data/agents**: Agent configuration files.
- **human.json**: Human player configuration.
- **random.json**: RandomBot configuration.
- **simple.json**: SimpleBot configuration.
- **cheater.json**: MCTSCheater configuration.
- **ismcts.json**: ISMCTSAgent configuration.

**src/data/scenarios**: Scenarios with preset player hands.
- **scenario_1.cs**: Example for scenario, where all hands are specified.
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

Selects its card plays using simple heuristics. Declarations (Schiebe, Obenabe, Undeufe) are made either after playing a specified number of evaluation games, or randomly. It is expected to play better than **random** and is still fast enough to be used for fast simulation in MCTS (set 'nof_eval_games' to 0).

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
<https://medium.com/@quasimik/monte-carlo-tree-search-applied-to-letterpress-34f41c86e238>

Most MCTS examples found online are about 2 player games with perfect
information like 'Connect 4' or 'Go'. But 'Slalom-Jass' is a 4-player game with
imperfect information, i.e. players only know their own cards (=> available
actions). **cheater** adapts MTCS for 4 players, but knows not only its own
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
   consists part on the reward statistics (**exploitation**, i.e. a node is
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
   therefore not incremented).  
   To adapt this for a **4-player game**, we backpropagate a list of rewards
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

The IEEE paper about **Information Set Montecarlo Tree Search** can be
downloaded from:  
<https://eprints.whiterose.ac.uk/id/eprint/75048/>


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
   a node (where one of the other players selects the play) which was fully
   expanded in a previous rollout, has now new unexpanded plays available in
   the current rollout. I.e. we can no longer rely on a fixed 'untried plays'
   or 'children' list, but have to get a list of legal plays from the current
   game state and compare it to the list of expanded plays in each traversed
   node. Only if all legal plays in the current game state (with redistributed
   opponent cards) have been expanded into child nodes, can we use the **Upper
   Confidence boundery for Trees (UCT)**, to move down the tree to one of the
   children.  
   **NOTE**, that the calculation of the Upper Confidence Boundary (UCB1) has
   also changed. If we would still use the number of times the parent was
   visited to calculate the exploration bonus, plays which appear seldomly in
   the list of legal plays for a node, will be overexplored. In the changed
   UCB1 calculation we have to replace the number of times the parent node was
   visited with the number of times the parent node was visited **and the child
   node was available**. For this we move updating of the 'visits' counters
   from the **Backpropagation** to the **Selection** phase, since this is where
   we have the list of legal plays directly available.

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

## human_vs_bots.py ##

If you want to play against one type of bot yourself.

    $ cd my_path/slalom_jass/src
    $ python3 human_vs_bots -h
```
    usage: human_vs_bots.py [-h] --bots BOTS [--first {1,2,3,4}] [--scenario SCENARIO]

    options:
      -h, --help            show this help message and exit
      --bots BOTS
      --first {1,2,3,4}, -f {1,2,3,4}
                            Set starting player (1-4).
      --scenario SCENARIO, -s SCENARIO
                            load scenario file.
```

E.g. play against **ismcts** and Player1 plays first (default):

    $ cd my_path/slalom_jass/src
    $ python3 human_vs_bots --bots ismcts

```
------------------------------------------------------------------------------
Declarations
------------------------------------------------------------------------------
*  Player1: K♣  7♢  10♢  7♡  10♡  A♡  6♠  8♠  10♠
   Player2: 8♣  Q♣  6♢  9♢  Q♢  A♢  6♡  J♡  K♡
   Player3: 7♣  10♣  8♢  J♢  K♢  8♡  9♡  7♠  J♠
   Player4: 6♣  9♣  J♣  A♣  Q♡  9♠  Q♠  K♠  A♠

   Player1 select: 0:Schiebe  1:Obenabe  2:Undeufe ? 0

   Player1: Schiebe
   Player2: Obenabe
------------------------------------------------------------------------------
Trick 1: Obenabe
------------------------------------------------------------------------------
   Player1: K♣  7♢  10♢  7♡  10♡  A♡  6♠  8♠  10♠
*  Player2: 8♣  Q♣  6♢  9♢  Q♢  A♢  6♡  J♡  K♡
   Player3: 7♣  10♣  8♢  J♢  K♢  8♡  9♡  7♠  J♠
   Player4: 6♣  9♣  J♣  A♣  Q♡  9♠  Q♠  K♠  A♠
   Trick:   J♡

   Player1: K♣  7♢  10♢  7♡  10♡  A♡  6♠  8♠  10♠
   Player2: 8♣  Q♣  6♢  9♢  Q♢  A♢  6♡  K♡
*  Player3: 7♣  10♣  8♢  J♢  K♢  8♡  9♡  7♠  J♠
   Player4: 6♣  9♣  J♣  A♣  Q♡  9♠  Q♠  K♠  A♠
   Trick:   J♡  9♡

   Player1: K♣  7♢  10♢  7♡  10♡  A♡  6♠  8♠  10♠
   Player2: 8♣  Q♣  6♢  9♢  Q♢  A♢  6♡  K♡
   Player3: 7♣  10♣  8♢  J♢  K♢  8♡  7♠  J♠
*  Player4: 6♣  9♣  J♣  A♣  Q♡  9♠  Q♠  K♠  A♠
   Trick:   J♡  9♡  Q♡

*  Player1: K♣  7♢  10♢  7♡  10♡  A♡  6♠  8♠  10♠
   Player2: 8♣  Q♣  6♢  9♢  Q♢  A♢  6♡  K♡
   Player3: 7♣  10♣  8♢  J♢  K♢  8♡  7♠  J♠
   Player4: 6♣  9♣  J♣  A♣  9♠  Q♠  K♠  A♠
   0:7♡  1:10♡  2:A♡ ? 
```

E.g. play against **cheater**, Player3 plays first, and the card distribution
is loaded from **scenario_2.cs**:

    $ cd my_path/slalom_jass/src
    $ python3 human_vs_bots.py --bot cheater --first 3 --scenario scenario_2

```
------------------------------------------------------------------------------
Declarations
------------------------------------------------------------------------------
   Player1: 7♣  9♣  8♢  J♢  7♡  10♡  8♠  J♠  K♠
   Player2: 9♢  9♠  6♡  K♡  A♢  7♠  10♢  6♢  6♠
*  Player3: J♡  7♢  A♣  Q♡  A♡  A♠  J♣  10♠  9♡
   Player4: Q♠  Q♣  6♣  K♣  Q♢  K♢  8♡  10♣  8♣
   Player3: Schiebe
   Player4: Undeufe

------------------------------------------------------------------------------
Trick 1: Undeufe
------------------------------------------------------------------------------
   Player1: 7♣  9♣  8♢  J♢  7♡  10♡  8♠  J♠  K♠
   Player2: 9♢  9♠  6♡  K♡  A♢  7♠  10♢  6♢  6♠
   Player3: J♡  7♢  A♣  Q♡  A♡  A♠  J♣  10♠  9♡
*  Player4: Q♠  Q♣  6♣  K♣  Q♢  K♢  8♡  10♣  8♣
   Trick:   Q♢

*  Player1: 7♣  9♣  8♢  J♢  7♡  10♡  8♠  J♠  K♠
   Player2: 9♢  9♠  6♡  K♡  A♢  7♠  10♢  6♢  6♠
   Player3: J♡  7♢  A♣  Q♡  A♡  A♠  J♣  10♠  9♡
   Player4: Q♠  Q♣  6♣  K♣  K♢  8♡  10♣  8♣
   0:8♢  1:J♢ ? 
```

## bots_vs_bots.py ##

Let 2 bot-teams play against each other.

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py -h

```
    usage: bots_vs_bots.py [-h] --bot13 BOT13 [--bot24 BOT24]
                           [--num-games NUM_GAMES] [--verbose]
                           [--first {1,2,3,4}] [--scenario SCENARIO]

    options:
      -h, --help            show this help message and exit
      --bot13 BOT13         type of Player1/Player3 bot.
      --bot24 BOT24         type of Player2/Player4 bot.
      --num-games NUM_GAMES, -n NUM_GAMES
                        number of games played.
      --verbose, -v         show played cards.
      --first {1,2,3,4}, -f {1,2,3,4}
                            Set starting player (1-4).
      --scenario SCENARIO, -s SCENARIO
                            load scenario file.
```

E.g. let **ismcts** play **1** round against **simple**, **Player4** plays
first, and we want to see detailed output:

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 simple -n 1 -f 4 -v

```
      1/1 
------------------------------------------------------------------------------
   Player1: 6♣  J♣  Q♣  7♢  8♢  7♡  6♠  8♠  10♠
   Player2: 7♣  10♣  Q♢  K♢  9♡  A♡  7♠  J♠  A♠
   Player3: K♣  A♣  6♢  9♢  J♢  J♡  Q♡  K♡  K♠
*  Player4: 8♣  9♣  10♢  A♢  6♡  8♡  10♡  9♠  Q♠

   --------
   Player4: Schiebe  Obenabe  Undeufe                        => Schiebe
   Player1: Schiebe  Obenabe  Undeufe                        => Schiebe
   Player2: Schiebe  Obenabe  Undeufe                        => Schiebe
   Player3: Schiebe  Obenabe  Undeufe                        => Undeufe
   --------
   Trick 1: ↑
   Player3: K♣  A♣  6♢  9♢  J♢  J♡  Q♡  K♡  K♠               => 6♢
   Player4: 10♢  A♢                                          => 6♢  A♢
   Player1: 7♢  8♢                                           => 6♢  A♢  8♢
   Player2: Q♢  K♢                                           => 6♢  A♢  8♢  Q♢
   --------
   Trick 2: ↓
   Player3: K♣  A♣  9♢  J♢  J♡  Q♡  K♡  K♠                   => Q♡
   Player4: 6♡  8♡  10♡                                      => Q♡  6♡
   Player1: 7♡                                               => Q♡  6♡  7♡
   Player2: 9♡  A♡                                           => Q♡  6♡  7♡  A♡
   --------
   Trick 3: ↑
   Player2: 7♣  10♣  K♢  9♡  7♠  J♠  A♠                      => 7♣
   Player3: K♣  A♣                                           => 7♣  K♣
   Player4: 8♣  9♣                                           => 7♣  K♣  9♣
   Player1: 6♣  J♣  Q♣                                       => 7♣  K♣  9♣  Q♣
   --------
   Trick 4: ↓
   Player2: 10♣  K♢  9♡  7♠  J♠  A♠                          => K♢
   Player3: 9♢  J♢                                           => K♢  J♢
   Player4: 10♢                                              => K♢  J♢  10♢
   Player1: 7♢                                               => K♢  J♢  10♢  7♢
   --------
   Trick 5: ↑
   Player2: 10♣  9♡  7♠  J♠  A♠                              => 7♠
   Player3: K♠                                               => 7♠  K♠
   Player4: 9♠  Q♠                                           => 7♠  K♠  9♠
   Player1: 6♠  8♠  10♠                                      => 7♠  K♠  9♠  6♠
   --------
   Trick 6: ↓
   Player1: 6♣  J♣  8♠  10♠                                  => 6♣
   Player2: 10♣                                              => 6♣  10♣
   Player3: A♣                                               => 6♣  10♣  A♣
   Player4: 8♣                                               => 6♣  10♣  A♣  8♣
   --------
   Trick 7: ↑
   Player3: 9♢  J♡  K♡                                       => 9♢
   Player4: 8♡  10♡  Q♠                                      => 9♢  Q♠
   Player1: J♣  8♠  10♠                                      => 9♢  Q♠  10♠
   Player2: 9♡  J♠  A♠                                       => 9♢  Q♠  10♠  9♡
   --------
   Trick 8: ↓
   Player3: J♡  K♡                                           => K♡
   Player4: 8♡  10♡                                          => K♡  8♡
   Player1: J♣  8♠                                           => K♡  8♡  J♣
   Player2: J♠  A♠                                           => K♡  8♡  J♣  J♠
   --------
   Trick 9: ↑
   Player3: J♡                                               => J♡
   Player4: 10♡                                              => J♡  10♡
   Player1: 8♠                                               => J♡  10♡  8♠
   Player2: A♠                                               => J♡  10♡  8♠  A♠
-------------------------------------------------------------------------------
   Undeufe:
   --------
   Player1:  15 - 7♠ K♠ 9♠ 6♠
   Player2:  37 - Q♡ 6♡ 7♡ A♡  7♣ K♣ 9♣ Q♣  K♢ J♢ 10♢ 7♢
   Player3:  80 - 6♢ A♢ 8♢ Q♢  6♣ 10♣ A♣ 8♣  9♢ Q♠ 10♠ 9♡  K♡ 8♡ J♣ J♠
   Player4:  25 - J♡ 10♡ 8♠ A♠  + 5
------------------------------------------------------------------------------
Player1:                   15  15
Player2:                   37  37
Player3:                   80  80
Player4:                   25  25

Player1 + Player3:         95  95
Player2 + Player4:         62  62
==============================================================================
```

E.g. let **ismcts** play **10** rounds against **cheater**, **Player1** plays
first (default), we only want to see statistics output (default), and the card
distribution is loaded from **scenario_2.cs**:

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 cheater -n 10 --scenario scenario_2 

```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
     1/10 |   0 |  96 |  20 |  41 |   20  |  137  | 27.9s
     2/10 |   0 |  16 |  22 | 119 |   21  |  136  | 28.4s
     3/10 |   0 |   0 | 136 |  21 |   59  |   97  | 28.5s
     4/10 |   0 | 128 |   0 |  29 |   44  |  112  | 28.4s
     5/10 |  11 |  53 |   0 |  93 |   37  |  119  | 29.7s
     6/10 |   0 |  53 |   0 | 104 |   31  |  125  | 25.7s
     7/10 |   0 |   0 | 137 |  20 |   46  |  110  | 29.7s
     8/10 |   0 |  62 |   0 |  95 |   40  |  116  | 26.9s
     9/10 |   0 |  42 |   0 | 115 |   36  |  120  | 31.3s
    10/10 |   0 |  22 |  18 | 117 |   34  |  122  | 26.8s
------------------------------------------------------------------------------
Player1:                   11   1
Player2:                  472  47
Player3:                  333  33
Player4:                  754  75

Player1 + Player3:        344  34
Player2 + Player4:       1226 122
==============================================================================
```

# Agent Configuration Files #

## random.json ##

```
{
    "type": "random"
}
```
Only contains the agent type (**DO NOT CHANGE IT**).

## simple.json ##

```
{
    "type": "simple",
    "debug_player": -1,
    "nof_eval_games": 100
}
```
- **type**": agent type (**DO NOT CHANGE**).
    - simple
- **debug_player**: display selection details for this player.
    - 0 => Player1
    - 1 => Player2
    - 2 => Player3
    - 3 => Player4

- **nof_eval_games**: number of evaluation games to decide for Schiebe, Obenabe, or Undeufe.
    - =0 => random pick.
    - \>0 => number of evaluation games.

## cheater.json ##

```
{
    "type": "cheater",
    "num_rounds": 100,
    "temperature": 0.7,
    "simple": false,
    "log_tree": false,
    "max_depth": 3,
    "log_nlwt": true,
    "show_trick": -2,
    "show_player": 0 
}
```
- **type**": agent type (**DO NOT CHANGE**).
    - cheater
- **num_rounds**: number of MCTS rollouts.
- **temperature**: exploitation/exploration ratio.
   - smaller => more exploitation (narrower tree)
   - larger => more exploration (wider tree)
- **simple**: select simulation bot.
   - false => RandomBot.
   - true => SimpleBot (slower but better results).
- **log_tree**: show MCTS tree for player selected by 'show_player'.
   - false => off.
   - true => on.
- **max_depth**: maximum number of levels shown by 'log_tree'.
- **log_nlwt**: show number of nodes, levels, win percentage, and time per
                rollout for player selected by 'show_player'.
   - false => off.
   - true => on.
- **show_trick**: game state for which we want to see MCTS details for the
                  player selected by 'show_player'.
   - -1 => declaration phase.
   - 0 - 8 => trick1 - trick9.
   - other => off. 
- **show_player**: show MCTS details for this player.
   - 0 => Player1.
   - 1 => Player2.
   - 2 => Player3.
   - 3 => Player4.

## ismcts.json ##

```
{
    "type": "ismcts",
    "num_rounds": 200,
    "temperature": 0.7,
    "simple": false,
    "log_tree": false,
    "max_depth": 3,
    "log_nlwt": false,
    "show_trick": -2,
    "show_player": 0 
}
```
- **type**": agent type (**DO NOT CHANGE**).
    - ismcts
- **num_rounds**: number of MCTS rollouts.
- **temperature**: exploitation/exploration ratio.
   - smaller => more exploitation (narrower tree)
   - larger => more exploration (wider tree)
- **simple**: select simulation bot.
   - false => RandomBot.
   - true => SimpleBot (slower but better results).
- **log_tree**: show MCTS tree for player selected by 'show_player'.
   - false => off.
   - true => on.
- **max_depth**: maximum number of levels shown by 'log_tree'.
- **log_nlwt**: show number of nodes, levels, win percentage, and time per
                rollout for player selected by 'show_player'.
   - false => off.
   - true => on.
- **show_trick**: game state for which we want to see MCTS details for the
                  player selected by 'show_player'.
   - -1 => declaration phase.
   - 0 - 8 => trick1 - trick9.
   - other => off. 
- **show_player**: show MCTS details for this player.
   - -1 => off.
   - 0 => Player1.
   - 1 => Player2.
   - 2 => Player3.
   - 3 => Player4.

# Scenario Files #

Lines with leading '#' are comments.  
Each line has 10 fields separated by ','.
- field 1: player (P1, P2, P3, or P4).
- fields 2 - 10: cards in player's hand.
   - rank-suit (rank: 6, 7, 8, 9, 10, J, Q, K, A suit: C, D, H, S)

## scenario_1.cs ##

Scenario, where cards for each player are specified.
```
# Slalom-Jass Scenario:
# Player1: 7♣  9♣  8♢  J♢  7♡  10♡  8♠  J♠  K♠
# Player2: 6♣  J♣  Q♣  10♢  Q♢  6♡  8♡  A♡  A♠
# Player3: K♣  A♣  6♢  K♢  A♢  J♡  6♠  7♠  9♠
# Player4: 8♣  10♣  7♢  9♢  9♡  Q♡  K♡  10♠  Q♠
# 
P1, 7-C, 9-C, 8-D, J-D, 7-H, 10-H, 8-S, J-S, K-S
P2, 6-C, J-C, Q-C, 10-D, Q-D, 6-H, 8-H, A-H, A-S
P3, K-C, A-C, 6-D, K-D, A-D, J-H, 6-S, 7-S, 9-S
P4, 8-C, 10-C, 7-D, 9-D, 9-H, Q-H, K-H, 10-S, Q-S
```

## scenario_2.cs ##

Scenario, where only Player1's cards are specified.  
The remaining cards will be randomly distributed to Player2, Player3, and
Player4.

```
# Slalom-Jass Scenario:
# Player1: 7♣  9♣  8♢  J♢  7♡  10♡  8♠  J♠  K♠
# 
P1, 7-C, 9-C, 8-D, J-D, 7-H, 10-H, 8-S, J-S, K-S
```

# MCTS Analysis #

## log_nlwt ##

To see a little MCTS info for Player1 set:

```
{
    "type": "ismcts",
    ...
    "log_nlwt": true,
    ...
    "show_player": 0 
}
```

It's best used when running bots_vs_bots.py in verbose mode:

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 simple -n 1 --verbose

```
       1/1 
------------------------------------------------------------------------------
*  Player1: 9♣  10♣  J♣  K♣  10♢  A♢  9♡  7♠  8♠
   Player2: 6♣  8♣  Q♣  A♣  9♢  K♢  7♡  J♡  K♡
   Player3: 7♢  8♢  Q♢  A♡  6♠  9♠  10♠  J♠  A♠
   Player4: 7♣  6♢  J♢  6♡  8♡  10♡  Q♡  Q♠  K♠


   nodes:200 levels:6 wins:44.4% time:13.42 ms/rollout

   --------
   Player1: Schiebe  Obenabe  Undeufe                        => Schiebe
```
Now we get a log message before each play selection of Player1:
- nodes:200 => the MCTS tree contains 200 nodes.
- levels:6 => the MCTS tree is 6 levels deep.
- wins:44.4% => the selected play had a win ratio (wins/visited) of 44.4%.
- time:13.42 ms/rollout => it took an average time of 13.42 ms per rollout.

**Notes**:
- The win ratio represents the value of the current state. E.g. the win ratio
  for the very 1st play, gives us an evaluation of the chances to win the game
  with this hand.
- In the example above we saw that 200 rollouts created 200 nodes. With larger
  rollout numbers it is possible to see 'nodes < rollouts'. In this cases some
  of the nodes are terminal nodes. If we reach a terminal node during
  **Selection**, we can skip **Expansion** and **Simulation** and immediately
  execute **Backpropagation** to update the win statistics.

## log_tree ##

To see more MCTS info we can log the tree:
```
{
    "type": "ismcts",
    ...
    "log_tree": true,
    "max_depth": 3,
    ...
    "show_player": 0 
}
```

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 simple -n 1 --verbose
```
      1/1 
------------------------------------------------------------------------------
*  Player1: 7♣  9♣  8♢  A♢  6♡  10♡  J♡  K♡  9♠
   Player2: 8♣  10♣  Q♢  7♡  6♠  10♠  J♠  Q♠  K♠
   Player3: 6♣  K♣  A♣  9♢  10♢  J♢  K♢  9♡  7♠
   Player4: J♣  Q♣  6♢  7♢  8♡  Q♡  A♡  8♠  A♠


root
-- 1 -- P1 Obenabe 198 0.536
---- 2 ---- P1 A♢ 161 0.553
------ 3 ------ P2 K♢ 36 0.486
------ 3 ------ P2 6♢ 32 0.442
------ 3 ------ P2 7♢ 23 0.437
------ 3 ------ P2 Q♢ 19 0.420
------ 3 ------ P2 J♢ 18 0.513
------ 3 ------ P2 10♢ 14 0.405
------ 3 ------ P2 9♢ 12 0.389
------ 3 ------ P2 A♠ 1 0.828
------ 3 ------ P2 10♣ 1 0.452
------ 3 ------ P2 A♡ 1 0.000
------ 3 ------ P2 8♠ 1 0.223
------ 3 ------ P2 6♠ 1 0.369
------ 3 ------ P2 J♠ 1 0.866
---- 2 ---- P1 J♡ 20 0.506
------ 3 ------ P2 A♡ 6 0.739
------ 3 ------ P2 7♡ 3 0.518
------ 3 ------ P2 8♡ 2 0.580
------ 3 ------ P2 Q♡ 2 0.344
------ 3 ------ P2 9♡ 2 0.436
------ 3 ------ P2 6♠ 1 0.146
------ 3 ------ P2 A♣ 1 0.299
------ 3 ------ P2 J♠ 1 0.580
------ 3 ------ P2 A♠ 1 0.153
---- 2 ---- P1 7♣ 9 0.495
------ 3 ------ P2 Q♣ 2 0.615
------ 3 ------ P2 6♣ 1 0.344
------ 3 ------ P2 J♣ 1 0.146
------ 3 ------ P2 8♣ 1 0.102
------ 3 ------ P2 K♣ 1 1.000
------ 3 ------ P2 A♣ 1 0.459
------ 3 ------ P2 10♣ 1 0.790
---- 2 ---- P1 8♢ 2 0.478
------ 3 ------ P2 J♢ 1 0.561
---- 2 ---- P1 9♠ 1 0.089
---- 2 ---- P1 6♡ 1 0.268
---- 2 ---- P1 10♡ 1 0.369
---- 2 ---- P1 K♡ 1 0.115
---- 2 ---- P1 9♣ 1 0.121
-- 1 -- P1 Undeufe 1 0.153
-- 1 -- P1 Schiebe 1 0.000
   --------
   Player1: Schiebe  Obenabe  Undeufe                        => Obenabe
```
Now we see before each decision of Player1 the MCTS tree built to make this
decision. Only 3 of 6 levels (see 'log_nlwt' example above) are shown, but
to understand the decision 1 level ("max_depth": 1) is usually enough:

```
------------------------------------------------------------------------------
*  Player1: 6♣  8♣  J♣  8♢  J♢  6♡  9♡  J♠  A♠
   Player2: 9♣  Q♣  K♣  Q♢  8♡  J♡  7♠  10♠  K♠
   Player3: A♣  6♢  9♢  10♢  A♢  7♡  Q♡  A♡  9♠
   Player4: 7♣  10♣  7♢  K♢  10♡  K♡  6♠  8♠  Q♠


root
-- 1 -- P1 Schiebe 197 0.509
-- 1 -- P1 Undeufe 2 0.274
-- 1 -- P1 Obenabe 1 0.268
   --------
   Player1: Schiebe  Obenabe  Undeufe                        => Schiebe
```

Here, Player1 selected 197 out of 200 rollouts the path through the play 'Schiebe', which resulted in a 'wins/visited' ratio of 0.509 => 'Schiebe' was selected.

**Notes**:
- The 'wins/visited' ratio of the selected play gives us the value of this game
  state (i.e. the chances to win the game with these cards).
- The 'number of rollouts per play' count shows us the impact of the
  'temperature' parameter. In this example we used a temperature of 0.7,
  resulting in 197 rollouts through the child with the best win ratio
  ('Schiebe'), while the 2nd best child ('Undeufe') got only 2 rollouts.

## show_trick ##

A detailed view of all 5 ISMCTS phases for one game state and player is
available, if we set: 

```
{
    "type": "ismcts",
    ...
    "show_trick": -1,
    "show_player": 0 
}
```

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 simple -n 1 --verbose

```
      1/1 
------------------------------------------------------------------------------
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 8♣  K♣  Q♢  6♡  9♡  J♡  Q♡  8♠  9♠
   Player3: 6♣  9♣  A♣  6♢  8♢  9♢  10♢  10♠  J♠
   Player4: 7♣  J♣  J♢  K♢  A♢  10♡  A♡  6♠  K♠

ROLLOUT 1

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 7♣  Q♢  6♡  9♡  A♡  8♠  9♠  J♠  K♠
   Player3: 9♣  K♣  A♣  10♢  K♢  10♡  Q♡  6♠  10♠
   Player4: 6♣  8♣  J♣  6♢  8♢  9♢  J♢  A♢  J♡

P1: Schiebe  Obenabe  Undeufe 
EXPAND: Schiebe
SIMULATE: P1:0 P2:28 P3:0 P4:129

ROLLOUT 2

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 7♣  K♣  8♢  9♢  K♢  9♡  A♡  9♠  10♠
   Player3: J♣  A♣  6♢  10♢  A♢  6♡  J♡  6♠  8♠
   Player4: 6♣  8♣  9♣  J♢  Q♢  10♡  Q♡  J♠  K♠

P1: Obenabe  Undeufe 
EXPAND: Obenabe
SIMULATE: P1:52 P2:36 P3:27 P4:42

ROLLOUT 3

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 6♣  7♣  8♣  9♣  8♢  9♢  K♢  A♢  K♠
   Player3: J♣  K♣  A♣  J♢  10♡  Q♡  A♡  6♠  10♠
   Player4: 6♢  10♢  Q♢  6♡  9♡  J♡  8♠  9♠  J♠

P1: Undeufe 
EXPAND: Undeufe
SIMULATE: P1:0 P2:106 P3:38 P4:13

ROLLOUT 4

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 7♣  9♣  A♣  6♢  J♢  9♡  Q♡  A♡  J♠
   Player3: J♣  K♣  8♢  10♢  K♢  A♢  6♡  8♠  10♠
   Player4: 6♣  8♣  9♢  Q♢  10♡  J♡  6♠  9♠  K♠

P1: Schiebe :0.00 Obenabe :0.50 Undeufe :0.24
SELECT: Obenabe
P1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠ 
EXPAND: K♡
SIMULATE: P1:23 P2:94 P3:0 P4:40

ROLLOUT 5

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 6♣  8♣  J♣  10♢  K♢  10♡  Q♡  10♠  J♠
   Player3: 7♣  9♣  A♣  8♢  J♢  A♢  6♡  J♡  A♡
   Player4: K♣  6♢  9♢  Q♢  9♡  6♠  8♠  9♠  K♠

P1: Schiebe :0.00 Obenabe :0.32 Undeufe :0.24
SELECT: Obenabe
P1: 10♣  Q♣  7♢  7♡  8♡  7♠  Q♠  A♠ 
EXPAND: 7♡
SIMULATE: P1:0 P2:0 P3:157 P4:0

ROLLOUT 6

DETERMINISATION:
*  Player1: 10♣  Q♣  7♢  7♡  8♡  K♡  7♠  Q♠  A♠
   Player2: 8♣  K♣  9♢  Q♢  6♡  Q♡  A♡  8♠  9♠
   Player3: 6♣  7♣  A♣  10♢  J♢  K♢  A♢  10♡  J♠
   Player4: 9♣  J♣  6♢  8♢  9♡  J♡  6♠  10♠  K♠

P1: Schiebe :0.00 Obenabe :0.55 Undeufe :0.24
SELECT: Obenabe
P1: 10♣  Q♣  7♢  8♡  7♠  Q♠  A♠ 
EXPAND: 7♠
SIMULATE: P1:0 P2:78 P3:49 P4:30
...
```
Before Player1 makes the decision to play 'Schiebe', 'Obenabe', or 'Undeufe',
all 5 phases of 200 rollouts are logged to show how the MCTS tree was built.
This is mainly used for debugging or for a better understanding of the MCTS process.

# ISMCTS Testing #

Testing ISMCTS agents to find the optimum 'num_rounds', 'temperature', and
'simple' parameters. 

## Number of Games ##

Wnen running a test with:

    $ cd my_path/slalom_jass/src
    $ python3 bots_vs_bots.py --bot13 ismcts --bot24 simple -n 300

We'll see a lot of change in the averages during the 1st few games:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
    1/300 |  96 |   0 |   0 |  61 |   96  |   61  | 24.4s
    2/300 |   4 |  59 |  94 |   0 |   97  |   60  | 18.5s
    3/300 |   0 |   0 | 134 |  23 |  109  |   47  | 23.8s
    4/300 | 157 |   0 |   0 |   0 |  121  |   35  | 25.1s
    5/300 | 108 |   0 |  49 |   0 |  128  |   28  | 26.5s
    6/300 |  30 |  34 |  67 |  26 |  123  |   33  | 27.4s
    7/300 |  61 |  52 |  44 |   0 |  120  |   36  | 25.9s
    8/300 |   0 |  55 |  61 |  41 |  113  |   43  | 19.3s
    9/300 |  39 |  95 |   0 |  23 |  104  |   52  | 22.7s
   10/300 |  38 |   0 | 119 |   0 |  110  |   46  | 23.4s
   ...
```

But after 100 games the averages settle around certain values:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
  ...
  100/300 | 157 |   0 |   0 |   0 |   89  |   67  | 24.5s
  101/300 |  61 |   0 |  96 |   0 |   89  |   67  | 25.8s
  102/300 | 140 |   3 |   0 |  14 |   90  |   66  | 22.1s
  103/300 |  25 |  24 |  67 |  41 |   90  |   66  | 22.6s
  104/300 |   0 | 145 |  12 |   0 |   89  |   67  | 21.3s
  105/300 |  89 |  29 |   6 |  33 |   89  |   67  | 21.8s
  106/300 |   0 |  87 |   0 |  70 |   88  |   68  | 15.6s
  107/300 |  59 |   0 |   0 |  98 |   88  |   68  | 24.0s
  108/300 |   0 |   0 |  24 | 133 |   88  |   68  | 20.8s
  109/300 |   0 |  19 | 122 |  16 |   88  |   68  | 25.9s
  110/300 |  31 |  25 | 101 |   0 |   88  |   68  | 20.9s
  ...
  200/300 |  72 |  27 |   0 |  58 |   89  |   67  | 22.3s
  201/300 |   0 |  27 | 130 |   0 |   89  |   67  | 28.9s
  202/300 | 117 |  40 |   0 |   0 |   89  |   67  | 17.0s
  203/300 |   0 |  21 |  91 |  45 |   89  |   67  | 20.3s
  204/300 |   0 |   0 |  85 |  72 |   89  |   67  | 20.7s
  205/300 |  26 |  99 |   0 |  32 |   89  |   67  | 25.5s
  206/300 |   0 |  33 |  73 |  51 |   89  |   67  | 26.7s
  207/300 |   0 |   0 | 157 |   0 |   89  |   67  | 25.3s
  208/300 |  49 |  54 |   0 |  54 |   89  |   67  | 20.2s
  209/300 |  72 |  25 |   0 |  60 |   89  |   67  | 25.3s
  210/300 |  97 |  23 |   0 |  37 |   89  |   67  | 25.2s
```

=> Tests should be run over **at least 100 games**.

## Simulation with RandomBot or SimpleBot  ##

RandomBot is faster but SimpleBot is expected to get better results.

600 rollouts with temperature 0.7 simulating with **RandomBot**:

```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
  ...
   95/100 |  20 |  63 |  13 |  61 |   79  |   77  | 37.5s
   96/100 |  53 |  29 |   0 |  75 |   79  |   77  | 24.8s
   97/100 |  46 |  43 |  10 |  58 |   79  |   77  | 39.4s
   98/100 |  30 |  96 |  31 |   0 |   78  |   78  | 27.4s
   99/100 |  59 |  52 |  40 |   6 |   79  |   77  | 35.1s
  100/100 |   0 |  89 |  68 |   0 |   78  |   78  | 30.4s
----------------------------------------------------------
Player1:                 4601  46
Player2:                 4010  40
Player3:                 3294  32
Player4:                 3795  37

Player1 + Player3:       7895  78
Player2 + Player4:       7805  78
===========================================================
```

600 rollouts with temperature 0.7 simulating with **SimpleBot**:

```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  93 |   0 |  64 |   0 |   88  |   68  | 47.6s
   96/100 |  38 |   0 |  96 |  23 |   89  |   67  | 38.6s
   97/100 | 157 |   0 |   0 |   0 |   89  |   67  | 39.3s
   98/100 |  28 |  15 | 114 |   0 |   90  |   66  | 29.7s
   99/100 |  25 |  47 |  85 |   0 |   90  |   66  | 40.3s
  100/100 |  90 |  25 |  26 |  16 |   90  |   66  | 31.7s
---------------------------------------------------------
Player1:                 4912  49
Player2:                 3292  32
Player3:                 4160  41
Player4:                 3336  33

Player1 + Player3:       9072  90
Player2 + Player4:       6628  66
=========================================================
```
**SimpleBot** is not much slower than **RandomBot** but yields definitely
better results.

## Number of Rollouts ##

The more rollouts, the better the results, but the longer it takes to play out
a game.

**100 rollouts** with temperature 0.7 simulating with SimpleBot:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  36 |  56 |   0 |  65 |   82  |   74  | 5.3s
   96/100 |  51 |   0 |   0 | 106 |   82  |   74  | 5.0s
   97/100 |  40 |   0 |  12 | 105 |   82  |   74  | 6.4s
   98/100 |  57 |   0 |  14 |  86 |   82  |   74  | 6.5s
   99/100 |  61 |  60 |  36 |   0 |   82  |   74  | 6.8s
  100/100 |  13 |  21 |  58 |  65 |   82  |   74  | 5.9s
---------------------------------------------------------
Player1:                 4059  40
Player2:                 4126  41
Player3:                 4152  41
Player4:                 3363  33

Player1 + Player3:       8211  82
Player2 + Player4:       7489  74
=========================================================
```

**600 rollouts** with temperature 0.7 simulating with SimpleBot:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  93 |   0 |  64 |   0 |   88  |   68  | 47.6s
   96/100 |  38 |   0 |  96 |  23 |   89  |   67  | 38.6s
   97/100 | 157 |   0 |   0 |   0 |   89  |   67  | 39.3s
   98/100 |  28 |  15 | 114 |   0 |   90  |   66  | 29.7s
   99/100 |  25 |  47 |  85 |   0 |   90  |   66  | 40.3s
  100/100 |  90 |  25 |  26 |  16 |   90  |   66  | 31.7s
---------------------------------------------------------
Player1:                 4912  49
Player2:                 3292  32
Player3:                 4160  41
Player4:                 3336  33

Player1 + Player3:       9072  90
Player2 + Player4:       6628  66
=========================================================
```

## Temperature ##

600 rollouts with **temperature 0.35** simulating with SimpleBot:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  30 | 105 |  22 |   0 |   80  |   76  | 39.1s
   96/100 |  27 | 105 |   0 |  25 |   79  |   77  | 29.5s
   97/100 | 157 |   0 |   0 |   0 |   80  |   76  | 38.6s
   98/100 |   0 | 124 |  33 |   0 |   80  |   76  | 23.1s
   99/100 | 144 |   0 |  13 |   0 |   80  |   76  | 42.8s
  100/100 |  54 |  40 |  63 |   0 |   81  |   75  | 32.2s
-----------------------------------------------------------
Player1:                 4089  40
Player2:                 4220  42
Player3:                 4044  40
Player4:                 3347  33

Player1 + Player3:       8133  81
Player2 + Player4:       7567  75
```

600 rollouts with **temperature 0.7** simulating with SimpleBot:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  93 |   0 |  64 |   0 |   88  |   68  | 47.6s
   96/100 |  38 |   0 |  96 |  23 |   89  |   67  | 38.6s
   97/100 | 157 |   0 |   0 |   0 |   89  |   67  | 39.3s
   98/100 |  28 |  15 | 114 |   0 |   90  |   66  | 29.7s
   99/100 |  25 |  47 |  85 |   0 |   90  |   66  | 40.3s
  100/100 |  90 |  25 |  26 |  16 |   90  |   66  | 31.7s
---------------------------------------------------------
Player1:                 4912  49
Player2:                 3292  32
Player3:                 4160  41
Player4:                 3336  33

Player1 + Player3:       9072  90
Player2 + Player4:       6628  66
```

600 rollouts with **temperature 1.4** simulating with SimpleBot:
```
          |     |     |     |     |    Average    |
    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time
----------+-----+-----+-----+-----+-------+-------+-------
   ...
   95/100 |  69 |   0 |  10 |  78 |   85  |   71  | 41.1s
   96/100 |  19 |  12 |  86 |  40 |   85  |   71  | 29.5s
   97/100 |  35 |  71 |  51 |   0 |   85  |   71  | 38.3s
   98/100 |  63 |  35 |  25 |  34 |   85  |   71  | 29.1s
   99/100 |  63 |   0 |   0 |  94 |   85  |   71  | 39.7s
  100/100 |  23 |   7 | 127 |   0 |   86  |   70  | 46.2s
----------------------------------------------------------
Player1:                 4521  45
Player2:                 3685  36
Player3:                 4107  41
Player4:                 3387  33

Player1 + Player3:       8628  86
Player2 + Player4:       7072  70
```

A **temperature near 0.7** seems to be the right choice.