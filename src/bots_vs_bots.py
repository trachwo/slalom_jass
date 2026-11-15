"""
Let 1 bot play a round of Slalom-Jass against 3 other bots.
"""
from pathlib import Path
import argparse
import time
import random
import json
import openpyxl
from openpyxl.styles import Font, Alignment

from slalom_jass.agents import HumanAgent, RandomBot, SimpleBot, MCTSCheater,\
     ISMCTSAgent
from slalom_jass.game import simulate_game
from slalom_jass.game.scenario import Scenario


# absolute path to files used in this program
BASE_PATH = Path(__file__).resolve().parent

class ExcelReport():
    """
    Spreadsheet for game data.
    """
    def __init__(self, filename):
        """
        Initializer.

        Args:
            filename (str):     name of xlsx-file.
        """
        self.filename = filename

        # try to load existing spreadsheet
        try:
            self.wb = openpyxl.load_workbook(filename)
            sheet = self.wb.active

        except FileNotFoundError:
            # File doesn't exist => create new spreadsheet.
            self.wb = openpyxl.Workbook()
            sheet = self.wb.active
            sheet.title = 'Slalom-Jass Report'

            # create headers in row 1 and 2
            sheet['A2'] = 'Seed'
            sheet.merge_cells('B1:E1')
            sheet['B1'] = 'Hands'
            sheet['B2'] = 'Player 1'
            sheet['C2'] = 'Player 2'
            sheet['D2'] = 'Player 3'
            sheet['E2'] = 'Player 4'
            sheet['F2'] = 'Declaration'
            sheet.merge_cells('G1:O1')
            sheet['G1'] = 'Tricks'
            sheet['G2'] = '1'
            sheet['H2'] = '2'
            sheet['I2'] = '3'
            sheet['J2'] = '4'
            sheet['K2'] = '5'
            sheet['L2'] = '6'
            sheet['M2'] = '7'
            sheet['N2'] = '8'
            sheet['O2'] = '9'
            sheet.merge_cells('P1:U1')
            sheet['P1'] = 'Scores'
            sheet['P2'] = 'P1'
            sheet['Q2'] = 'P2'
            sheet['R2'] = 'P3'
            sheet['S2'] = 'P4'
            sheet['T2'] = 'P1+P3'
            sheet['U2'] = 'P2+P4'

            # change header font
            header_font = Font(bold=True)
            for row_of_cell_objects in sheet['A1:U2']:
                for cell_obj in row_of_cell_objects:
                    cell_obj.font = header_font
                    cell_obj.alignment = Alignment(horizontal='center')

            # change column dimensions
            for col in ['B', 'C', 'D', 'E']:
                sheet.column_dimensions[col].width = 27

            sheet.column_dimensions['F'].width = 15

            for col in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']:
                sheet.column_dimensions[col].width = 15

            # freeze top 2 rows (= header)
            sheet.freeze_panes = 'A3'

        self.row = sheet.max_row + 1    # next empty row in spreadsheet

    def add_log(self, seed, log, points):
        """
        Add log of one game to the next row of the spreadsheet.

        Args:
            seed (int):     random generator seed for this round.
            log (list):     list of log strings for 1 game.
            points (list):  points won this round.
        """
        sheet = self.wb.active
        row = self.row

        if seed is not None:
            sheet[f"A{row}"] = seed
        sheet[f"B{row}"] = log[1][12:]
        sheet[f"C{row}"] = log[2][12:]
        sheet[f"D{row}"] = log[3][12:]
        sheet[f"E{row}"] = log[4][12:]
        sheet[f"F{row}"] = log[0][9:]
        sheet[f"G{row}"] = f"{log[5][10]} P{log[5][18]}: {log[5][21:]}"
        sheet[f"H{row}"] = f"{log[6][10]} P{log[6][18]}: {log[6][21:]}"
        sheet[f"I{row}"] = f"{log[7][10]} P{log[7][18]}: {log[7][21:]}"
        sheet[f"J{row}"] = f"{log[8][10]} P{log[8][18]}: {log[8][21:]}"
        sheet[f"K{row}"] = f"{log[9][10]} P{log[9][18]}: {log[9][21:]}"
        sheet[f"L{row}"] = f"{log[10][10]} P{log[10][18]}: {log[10][21:]}"
        sheet[f"M{row}"] = f"{log[11][10]} P{log[11][18]}: {log[11][21:]}"
        sheet[f"N{row}"] = f"{log[12][10]} P{log[12][18]}: {log[12][21:]}"
        sheet[f"O{row}"] = f"{log[13][10]} P{log[13][18]}: {log[13][21:]}"
        sheet[f"P{row}"] = points[0]
        sheet[f"Q{row}"] = points[1]
        sheet[f"R{row}"] = points[2]
        sheet[f"S{row}"] = points[3]
        sheet[f"T{row}"] = points[0] + points[2]
        sheet[f"U{row}"] = points[1] + points[3]

        for row_of_cell_objects in sheet[f'A{row}:U{row}']:
             for cell_obj in row_of_cell_objects:
                cell_obj.font = Font(size=8)
                if cell_obj.column in [16, 17, 18, 19, 20, 21]:
                    cell_obj.alignment = Alignment(horizontal='right')
                if cell_obj.column in [1, 2, 3, 4, 5, 6]:
                    cell_obj.alignment = Alignment(horizontal='center')

        self.row += 1

    def save(self):
        """
        Save spreadsheet.
        """
        self.wb.save(self.filename)


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
    parser.add_argument('--excel', '-e', default=None,
                        help="create spreadsheet.")
    parser.add_argument('--seed', type=int, default=None,
                        help="Seed random generator.")
    parser.add_argument('--fixed', '-x', action='store_true',
                        help="Fixed first player.")
    parser.add_argument('--declaration', '-d', default=None, type=str,
                        choices={'obenabe', 'undeufe'},
                        help="Select type of game.")
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

    if args.excel is not None:
        # add extension'.xlxs' to excel-name
        excel_file = args.excel + '.xlsx'
        # set excel path
        excel_path = Path(str(BASE_PATH / 'data' / 'logs' / excel_file))
        excel = ExcelReport(excel_path)
    else:
        excel = None

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
                               args.verbose, True, args.declaration)
#        print(log)
        # add log to spreadsheet
        if excel is not None:
            seed = args.seed + i if args.seed is not None else None
            excel.add_log(seed, log, points)

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

    # save spreadsheet.
    if excel is not None:
        excel.save()

if __name__ == '__main__':
    main()
