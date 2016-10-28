# coding: utf-8
# create training data for multiplication
import os
import curses
import pickle
from copy import copy

from npi.multiply.config import FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH
from npi.multiply.lib import MultiplicationEnv, MultiplicationProgramSet, MultiplicationTeacher, create_char_map, create_questions, run_npi
from npi.core import ResultLogger
from npi.terminal_core import TerminalNPIRunner, Terminal


def main(stdscr, filename: str, num_of_questions: int, result_logger: ResultLogger):
    terminal = Terminal(stdscr, create_char_map())
    terminal.init_window(FIELD_WIDTH, FIELD_ROW)
    program_set = MultiplicationProgramSet()
    multiplication_env = MultiplicationEnv(FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH, terminal)

    questions = create_questions(num_of_questions)
    teacher = MultiplicationTeacher(program_set, terminal)
    npi_runner = TerminalNPIRunner(terminal, teacher, result_logger)
    npi_runner.verbose = DEBUG_MODE
    steps_list = []
    for data in questions:
        multiplication_env.reset()
        q = copy(data)
        run_npi(multiplication_env, npi_runner, program_set.MUL, data)
        steps_list.append({"q": q, "steps": npi_runner.step_list})
        result_logger.write(data)
        terminal.add_log(data)

    if filename:
        with open(filename, 'wb') as f:
            pickle.dump(steps_list, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    import sys
    DEBUG_MODE = os.environ.get('DEBUG')
    if DEBUG_MODE:
        output_filename = None
        num_data = 3
        log_filename = 'result_multiplication.log'
    else:
        output_filename = sys.argv[1] if len(sys.argv) > 1 else None
        num_data = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        log_filename = sys.argv[3] if len(sys.argv) > 3 else 'result_multiplication.log'

    logger = ResultLogger(log_filename)
    curses.wrapper(main, output_filename, num_data, logger)
    print("create %d training data" % num_data)
