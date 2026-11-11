"""
Let 1 bot play a round of Slalom-Jass against 3 other bots.
"""
from pathlib import Path
import argparse
import time
import random
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
        agent = SimpleBot(data['debug_player'],
                          data['nof_eval_games'])
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
    Let 2 agents play against 2 agents.

    Partners (P1/P3, P2/P4) have the same type.

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
    parser.add_argument('--logfile', '-l', default=None,
                        help="create log-file.")
    parser.add_argument('--seed', type=int, default=None,
                        help="Seed random generator.")
    parser.add_argument('--fixed', action='store_true',
                        help="Fixed first player")
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

    if args.logfile is not None:
        # add extension'.log' to logfile-name
        log_file = args.logfile + '.log'
        # set log-file path
        logfile_path = Path(str(BASE_PATH / 'data' / 'logs' / log_file))
    else:
        logfile_path = None

    # reset total points
    total = [0 for _ in range(4)]

    if not args.verbose:
        # print statistics header
        print()
        print("          |     |     |     |     |    Average    |")
        print("    Games |  P1 |  P2 |  P3 |  P4 | P1+P3 | P2+P4 | Time")
        print("----------+-----+-----+-----+-----+-------+-------+-------")

    if logfile_path is not None:
        with logfile_path.open('w', encoding='utf-8') as lfile:
            lfile.write(
                f"-----------------------------------------------------\n"
                f"Scenario: "
                f"{args.scenario if args.scenario is not None else '---'}\n"
                f"Bots P1/P3: {args.bot13}\n"
                f"Bots P2/P4: {args.bot24}\n"
                f"Base Seed: {args.seed if args.seed is not None else '---'}\n"
                )

    for i in range(args.num_games):
        if args.seed is not None:
            # seed random generator => reproducible card distribution
            random.seed(args.seed + i)

        start_time = time.time()
        print(f"{str(i + 1) + '/' + str(args.num_games):>9} ",
               end='')
        if args.verbose:
            # show details
            print("\n----------------------------------------------------------"
                  "--------------------")
        # simulate 1 game
        points, log = simulate_game(agent1, agent2, agent3, agent4, dealer, scenario,
                               args.verbose, True)
        if logfile_path is not None:
            with logfile_path.open('a', encoding='utf-8') as lfile:
                lfile.write("-----------------------------------------------------\n")
                lfile.write(f"   {str(i + 1) + '/' + str(args.num_games)}   "
                            f"{log[0]}   P1/P3:{points[0] + points[2]}   "
                            f"P2/P4: {points[1] + points[3]}\n")
                lfile.write("-----------------------------------------------------\n")
                for line in log[1:]:
                    lfile.write(line + '\n')

        # calculate current total and average
        total = [total[x] + points[x] for x in range(len(total))]
        avg_13 = (total[0] + total[2]) / (i + 1)
        avg_24 = (total[1] + total[3]) / (i + 1)

        if args.verbose:
            print("------------------------------------------------------------"
                  "------------------")
        else:
            print(f"| {points[0]:>3} | {points[1]:>3} | {points[2]:>3} |"
                  f" {points[3]:>3} | {avg_13:5.1f} | {avg_24:5.1f} |"
                  f" {time.time() - start_time:.1f}s")

        # next dealer
        if not args.fixed:
            # new dealer and starting player (shift 1 to the right)  
            dealer = (dealer + 1) % 4

    # print final score
    if not args.verbose:
        print("----------------------------------------------------------------"
              "--------------")
    for i in range(4):
        print(f"Player{i+1}: {total[i]:>20} {total[i]/args.num_games:6.1f}")
    print()
    print(f"Player1 + Player3: {total[0] + total[2]:>10}"
          f" {(total[0] + total[2])/args.num_games:6.1f}")

    print(f"Player2 + Player4: {total[1] + total[3]:>10}"
          f" {(total[1] + total[3])/args.num_games:6.1f}")

    print("===================================================================="
          "==========")

if __name__ == '__main__':
    main()
