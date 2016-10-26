# coding: utf-8
# create training data for multiplication
import os
import curses
import pickle
from copy import copy # shallow copy

from npi.add.config import FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH
from npi.add.lib import MultiplicationEnv, MultiplicationProgramSet, MultiplicationTeacher, create_char_map, create_questions, run_npi
from npi.core import ResultLogger
from npi.terminal_core import TerminalNPIRunner, Terminal
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer, TfidfTransformer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics

def main(stdscr, filename: str, num_of_questions: int, result_logger: ResultLogger):
    terminal = Terminal(stdscr, create_char_map())
    terminal.init_window(FIELD_WIDTH, FIELD_ROW)
    program_set = MultiplicationProgramSet()
    multiplication_env = MultiplicationEnv(FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH)

    questions = create_questions(num_of_questions)
    teacher = MultiplicationTeacher(program_set)
    npi_runner = TerminalNPIRunner(terminal, teacher)
    npi_runner.verbose = DEBUG_MODE
    steps_list = []
    for data in questions:
        multiplication_env.reset()
        q = copy(data)
        run_npi(multiplication_env, npi_runner, program_set.ADD, data)
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
        log_filename = 'result.log'
    else:
        output_filename = sys.argv[1] if len(sys.argv) > 1 else None
        num_data = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        log_filename = sys.argv[3] if len(sys.argv) > 3 else 'result.log'
    curses.wrapper(main, output_filename, num_data, ResultLogger(log_filename))
    print("create %d training data" % num_data)
