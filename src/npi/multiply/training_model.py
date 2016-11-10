# coding: utf-8
# training model for multiplication
import os
import pickle
import curses

from npi.multiply.config import FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH
from npi.multiply.lib import MultiplicationEnv, MultiplicationProgramSet, MultiplicationTeacher, create_char_map, create_questions, run_npi
from npi.multiply.model import MultiplicationNPIModel
from npi.core import ResultLogger, RuntimeSystem
from npi.terminal_core import TerminalNPIRunner, Terminal


def main(stdscr, output_filename, filename: str, model_path: str):
    system = RuntimeSystem()
    program_set = MultiplicationProgramSet()

    with open(filename, 'rb') as f:
        steps_list = pickle.load(f)
    terminal = Terminal(stdscr, create_char_map())
    terminal.init_window(FIELD_WIDTH, FIELD_ROW)
    npi_model = MultiplicationNPIModel(system, terminal, model_path, program_set)
    npi_model.fit(steps_list)


if __name__ == '__main__':


    import sys
    DEBUG_MODE = os.environ.get('DEBUG')
    if DEBUG_MODE:
        output_filename = None
    else:
        output_filename = sys.argv[1]
    train_filename = sys.argv[2]
    model_output = sys.argv[3]
    curses.wrapper(main, output_filename, train_filename, model_output)
    print("finish training multiplication data")
    #vmain(output_filename, train_filename, model_output)
