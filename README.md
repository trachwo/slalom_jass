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

This describes how to download the source code and install the Slalom-Jass
package locally.

## Python ##
Install Python3:  
-> <https://realpython.com/installing-python/>

## Slalom-Jass

Clone the 'slalom_jass' repository from **github**  
-> git@github.com:trachwo/slalom_jass.git

or download the zip-file **(green '<> Code' button)**


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
- **bot_vs_bots.py**: let bots play against themselves.
- **human_vs_bots.py**: let human player play against bots.

**src/slalom_jass**: slalom_jass sub-modules:
- **__init__.py**: makes *slalom_jass* a Python package.
- **cards.py**: implementation of playing cards.

**src/slalom_jass/game/**: game logic sub-module:
- **__init__.py**: makes *game* a Python package.
- **player.py**: Player class keeping track of player hands.
- **info.py**: GameInfo class keeping track of played cards and suits not
               followed.
- **scenario**: Scenario class used to load player hands from CSV-file.
- **game**: GameState class containing the Slalom-Jass state machine.

**src/slalom_jass/agents/**: game agents.
- **__init__.py**: makes *agents* a Python package.
- **base.py**: Agent class => base class for all game agents.
- **human.py**: agent representing a human player => user interface.
- **naive.py**: RandomBot class (random play selection) and SimpleBot class
                (using simple heuristic for play selection).
- **mcts_cheater.py**: MCTSCheater class => MCTS agent with perfect information
                       (i.e he is looking at other players' cards!)
- **ismcts.py**: ISMCTSAgent class => Single-Observer Informatin Set MCTS agent.

**src/data/agents**: agent configuration files.
- **human.json**: human player configuraion.
- **random.json**: RandomBot configuraion.
- **simple.json**: SimpleBot configuration.
- **cheater.json**: MCTSCheater configuration.
- **ismcts.json**: ISMCTSAgent configuration.

**src/data/scenarios**: scenarios with preset player hands.
- **scenario_1.cs**: example for scenario, where all hands are specidfied.
- **scenario_2.cs**: example for scenario, where only one hand is specified.