# coding: utf-8
import os
import pickle

from npi.multiply.config import FIELD_ROW, FIELD_WIDTH, FIELD_DEPTH
from npi.multiply.lib import MultiplicationEnv, MultiplicationProgramSet, MultiplicationTeacher, create_char_map, create_questions, run_npi
from npi.multiply.model import MultiplicationNPIModel
from npi.core import ResultLogger, RuntimeSystem
from npi.terminal_core import TerminalNPIRunner, Terminal


def main(filename: str, model_path: str):
    system = RuntimeSystem()
    program_set = MultiplicationProgramSet()

    with open(filename, 'rb') as f:
        steps_list = pickle.load(f)

    npi_model = MultiplicationNPIModel(system, model_path, program_set)
    npi_model.fit(steps_list)


if __name__ == '__main__':
    import sys
    DEBUG_MODE = os.environ.get('DEBUG')
    train_filename = sys.argv[1]
    model_output = sys.argv[2]
    main(train_filename, model_output)
