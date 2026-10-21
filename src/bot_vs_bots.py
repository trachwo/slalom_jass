"""
Let 1 bot play a round of Slalom-Jass against 3 other bots.
"""
from pathlib import Path
import argparse
import time
import json
from slalom_jass.agents import HumanAgent, RandomBot, SimpleBot, MCTSCheater,\
     ISMCTSAgent
from slalom_jass.game import simulate_game
from slalom_jass.game.scenario import Scenario


# absolute path to files used in this program
BASE_PATH = Path(__file__).resolve().parent


def load_agent(filename):
    """
    Load agent type and parameters from json-file.

    Args:
        filename (str):     filename (without extension).

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
    elif data['type'] == 'simple':
        agent = SimpleBot(data['debug_player'])
    elif data['type'] == 'cheater':
        agent = MCTSCheater(data['num_rounds'],
                          data['temperature'],
                          data['simple'],
                          data['log_tree'],
                          data['max_depth'],
                          data['log_nlwt'],
                          data['show_trick'],
                          data['show_player'])
    elif data['type'] == 'ismcts':
        agent = ISMCTSAgent(data['num_rounds'],
                          data['temperature'],
                          data['simple'],
                          data['log_tree'],
                          data['max_depth'],
                          data['log_nlwt'],
                          data['show_trick'],
                          data['show_player'])
    else:
        raise ValueError(f"No such agent type '{data['type']}'")

    return agent


def main():
    """
    Let 4 agents play against itself.

    Agent types and parameters are loaded from json-files.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot13', required=True,
                        help="type of Player1/Player3 bot." )
    parser.add_argument('--bot24', default='simple',
                        help="type of Player2/Player4 bot.")
    parser.add_argument('--num-games', '-n', type=int, default=10,
                        help="number of games played.")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="show played cards.")
    parser.add_argument('--first', '-f', default=1, type=int,
                        choices={1, 2, 3, 4},
                        help="Set starting player (1-4).")
    parser.add_argument('--scenario', '-s', default=None,
                        help="load scenario file.")
    args = parser.parse_args()

    # create agents.
    agent1 = load_agent(args.bot13)
    agent2 = load_agent(args.bot24)
    agent3 = load_agent(args.bot13)
    agent4 = load_agent(args.bot24)

    # the dealer is the player on the left of the 1st player
    # e.g. Player1 (game.players[0]) shall play first
    #      => Player4 (game.players[3]) must be the dealer.
    dealer = (args.first + 2) % 4

    if args.scenario is not None:
        # add extension '.cs' to scenario-name
        scenario_file = args.scenario + '.cs'

        # load scenario from CSV-file
        # get absolute path to agent 
        scenario_path = str(BASE_PATH / 'data' / 'scenarios' / scenario_file)

        # create scenario
        scenario = Scenario(scenario_path)
        # load scenario from CSV-file
        scenario.load()
    else:
        scenario = None

    # reset total points
    total = [0 for _ in range(4)]

    print()
    for i in range(args.num_games):
        start_time = time.time()
        print(f"{str(i + 1) + '/' + str(args.num_games):>9}: ",
               end='')
        if args.verbose:
            # show details
            print("\n----------------------------------------------------------"
                  "------------------------------------------")
        # simulate 1 game
        points = simulate_game(agent1, agent2, agent3, agent4, dealer, scenario,
                               args.verbose)
        if args.verbose:
            print("------------------------------------------------------------"
                  "----------------------------------------")
        else:
            print(f"P1:{points[0]:>3} P2:{points[1]:>3} P3:{points[2]:>3}"
                  f" P4:{points[3]:>3}   time:{time.time() - start_time:.1f}s")

        # add to total points
        for i in range(4):
            total[i] += points[i]

        # next dealer
        dealer = (dealer + 1) % 4

    # print final score
    if not args.verbose:
        print("----------------------------------------------------------------"
              "------------------------------------")
    for i in range(4):
        print(f"Player{i+1}: {total[i]:>20} {total[i]/args.num_games:.2f}")
    print()
    print(f"Player1 + Player3: {total[0] + total[2]:>10}"
          f" {(total[0] + total[2])/args.num_games:.2f}")

    print(f"Player2 + Player4: {total[1] + total[3]:>10}"
          f" {(total[1] + total[3])/args.num_games:.2f}")

    print("===================================================================="
          "================================")

if __name__ == '__main__':
    main()
