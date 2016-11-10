# coding: utf-8
import curses
import os
import pickle

from npi.multiply.config import FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH
from npi.multiply.lib import MultiplicationEnv, MultiplicationProgramSet, MultiplicationTeacher, create_char_map, create_questions, run_npi
from npi.multiply.model import MultiplicationNPIModel
from npi.core import ResultLogger, RuntimeSystem
from npi.terminal_core import TerminalNPIRunner, Terminal


def main(stdscr, model_path: str, num: int, result_logger: ResultLogger):
    terminal = Terminal(stdscr, create_char_map())
    terminal.init_window(FIELD_WIDTH, FIELD_ROW)
    program_set = MultiplicationProgramSet()
    multiplyition_env = MultiplicationEnv(FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH)

    questions = create_questions(num)
    if DEBUG_MODE:
        questions = questions[-num:]
    system = RuntimeSystem(terminal=terminal)
    npi_model = MultiplicationNPIModel(system, terminal, model_path, program_set)
    npi_runner = TerminalNPIRunner(terminal, npi_model, recording=False)
    npi_runner.verbose = DEBUG_MODE
    correct_count = wrong_count = 0
    for data in questions:
        multiplyition_env.reset()
        run_npi(multiplyition_env, npi_runner, program_set.ADD, data)
        result_logger.write(data)
        terminal.multiply_log(data)
        if data['correct']:
            correct_count += 1
        else:
            wrong_count += 1
    return correct_count, wrong_count


if __name__ == '__main__':
    import sys
    DEBUG_MODE = os.environ.get('DEBUG')
    model_path_ = sys.argv[1]
    num_data = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    log_filename = sys.argv[3] if len(sys.argv) > 3 else 'result.log'
    cc, wc = curses.wrapper(main, model_path_, num_data, ResultLogger(log_filename))
    print("Accuracy of MultiplicationNPIModel %s(OK=%d, NG=%d)" % (cc/(cc+wc), cc, wc))
