"""
Let 1 human play a round of Slalom-Jass against 3 bots of same type.
"""
from pathlib import Path
import argparse
import json
from slalom_jass.agents import HumanAgent, RandomBot
from slalom_jass.game import GameState


# absolute path to files used in this program
BASE_PATH = Path(__file__).resolve().parent


def load_agent(filename):
    """
    Load agent type and parameters from json-file.

    Args:
        filename (str):     filename.

    Returns:
        Agent:  agent created from data in json-file.
    """
    # add extension '.json' to filename
    filename = filename + '.json'

    # get absolute path to agent 
    agent_path = str(BASE_PATH / 'data' / 'agents' / filename)

    with open(agent_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data['type'] == 'human':
        agent = HumanAgent()
    elif data['type'] == 'random':
        agent = RandomBot()
#    elif data['type'] == 'simple':
#        agent = SimpleBot()
#    elif data['type'] == 'mcts_cheater':
#        agent = MCTSCheater(data['num_rounds'],
#                          data['temperature'],
#                          data['simple'],
#                          data['log_tree'],
#                          data['max_depth'],
#                          data['log_nlwt'],
#                          data['show_turn'])
#    elif data['type'] == 'ismcts':
#        agent = ISMCTSAgent(data['num_rounds'],
#                          data['temperature'],
#                          data['simple'],
#                          data['log_tree'],
#                          data['max_depth'],
#                          data['log_nlwt'],
#                          data['show_turn'])
    else:
        raise ValueError(f"No such agent type '{data['type']}'")

    return agent


def simulate_game(agent1, agent2, agent3, agent4, dealer=3):
    """
    Let 4 agents play a single round of Slalom-Jass against each other.

    Args:
        agent1 (Agent):     bot playing Player1.
        agent2 (Agent):     bot playing Player2.
        agent3 (Agent):     bot playing Player3.
        agent4 (Agent):     bot playing Player4.
        first (int):        first player.

    Returns:
        tuple:     points per agent.
    """
    # map player index to agent
    agent_map = {0: agent1, 1: agent2, 2: agent3, 3: agent4}

    # create gamestate for new round (with Player1 as dealer)
    game = GameState.new_round(dealer)
    # deal cards and determine starting player
    game.start_round()

    # Game starts with declaration phase
    print("\n----------------------------------------------------------"
          "--------------------")
    print("Declarations")
    print("-----------------------------------------------------------"
          "-------------------")
    # print game state => player hands
    game.print_state()

    # play 9 tricks of one round.
    while not game.is_over():
        if game.tricks >= 0:
            mode = 'Obenabe' if game.higher_card_wins() else 'Undeufe'
            # Trick phase 
            if game.turns == 0:
                # print banner at start of each trick 
                print("\n------------------------------------------------------"
                      "------------------------")
                print(f"Trick {game.tricks + 1}: {mode}")
                print("--------------------------------------------------------"
                      "----------------------")
            # print game state before each player selects a card
            game.print_state()

        # ask next player's agent to select a play (declaration or card)
        play = agent_map[game.next_player].select_play(game)
        if game.tricks < 0:
            # declaration phase => print player's declaration
            print(f"   {game.players[game.next_player].name}: {play}")

        else:
            # Trick phase => print table after play
            if len(game.table) == 0:
                print(f"   Trick:   {str(play)}\n")
            else:
                print(f"   Trick:   {game.show_table_cards()}  {str(play)}\n")

        game = game.apply_play(play)

    print("==============================================================================")

    # print detailed results
    points = game.count_points()
    print(f"   {'Obenabe' if game.obenabe else 'Undeufe'}:")
    print("   --------")
    for p, player in enumerate(game.players):
        print(f"   {player.name}: {points[p]:>3} -"
              f" {player.show_tricks()}", end='')
        if p == game.next_player:
            print("  + 5")   # for last trick
        else:
            print()
    print("==============================================================================")

    # return tuple of points
    return points


def main():
    """
    Let 4 agents play against itself.

    Agent types and parameters are loaded from json-files.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--bots', required=True)
    parser.add_argument('--first', '-f', default=1, type=int,
                        choices={1, 2, 3, 4},
                        help="Set starting player (1-4).")
    args = parser.parse_args()

    # create agents.
    agent1 = HumanAgent()
    agent2 = load_agent(args.bots)
    agent3 = load_agent(args.bots)
    agent4 = load_agent(args.bots)

    # the dealer is the player on the left of the 1st player
    # e.g. Player1 (game.players[0]) shall play first
    #      => Player4 (game.players[3]) must be the dealer.
    dealer = (args.first + 2) % 4

    # play 1 game
    simulate_game(agent1, agent2, agent3, agent4, dealer)


if __name__ == '__main__':
    main()
