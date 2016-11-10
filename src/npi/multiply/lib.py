# coding: utf-8
from random import random

import numpy as np

from npi.core import Program, IntegerArguments, StepOutput, NPIStep, PG_CONTINUE, PG_RETURN, ResultLogger
from npi.terminal_core import Screen, Terminal

__author__ = 'katy_lee'


class MultiplicationEnv:
    """
    Environment of Multiplication
    the idea is to add mul1 to 0 for mul2 times
    row0: in1 (initial as 0, and the set as last time output, serve as accomadator)
    row1: in2 (will consistently be mul1)
    row2: carry
    row3: output
    row4: mul1
    row5: mul2 (will decrease by 1 after each addition, serves as counter of addition program here)


    """
    def __init__(self, height, width, num_chars, terminal):
        self.screen = Screen(height, width)
        self.num_chars = num_chars
        self.pointers = [0] * height
        self.reset()
        self.terminal = terminal
    # reset the pointers and the content of row
    def reset(self):
        self.screen.fill(0)
        self.pointers = [self.screen.width-1] * self.screen.height  # rightmost

    # only reset the 1 to 4 th pointers after each addition
    def reset_pointers(self):
        for row in range (0, 4):
            self.pointers[row] = self.screen.width-1  # rightmost
        self.fill_row_with_zero(2)

    def fill_row_with_zero(self, row):
        self.screen[row, :].fill(0)

    def get_observation(self) -> np.ndarray:
        value = []
        for row in range(len(self.pointers)):
            # self.terminal.add_log(self.screen[row, self.pointers[row]])
            value.append(self.to_one_hot(self.screen[row, self.pointers[row]]))
        # self.terminal.add_log(np.array(value))
        return np.array(value)  # shape of FIELD_ROW * FIELD_DEPTH

    def to_one_hot(self, ch):
        ret = np.zeros((self.num_chars,), dtype=np.int8)
        if 0 <= ch < self.num_chars:
            ret[ch] = 1
        else:
            raise IndexError("ch must be 0 <= ch < %s, but %s" % (self.num_chars, ch))
        return ret

    def setup_problem(self, mul1, mul2):
        # set in1 as the value 0
        for i, s in enumerate(reversed("0")):
            self.screen[0, -(i+1)] = int(s) + 1
        # set in2 as the value mul1
        for i, s in enumerate(reversed("%s" % mul1)):
            self.screen[1, -(i+1)] = int(s) + 1
        # set
        for i, s in enumerate(reversed("%s" % mul1)):
            self.screen[4, -(i+1)] = int(s) + 1
        for i, s in enumerate(reversed("%s" % mul2)):
            self.screen[5, -(i+1)] = int(s) + 1
        # self.terminal.add_log(self.screen)

    def move_pointer(self, row, left_or_right):
        if 0 <= row < len(self.pointers):
            self.pointers[row] += 1 if left_or_right == 1 else -1  # LEFT is 0, RIGHT is 1
            self.pointers[row] %= self.screen.width

    def set_pointer(self, row, index):
        self.terminal.add_log("@@@@set pointer at index %d" % (index))
        self.pointers[row] = index
    # wirte single digit
    def write(self, row, ch):
        if 0 <= row < self.screen.height and 0 <= ch < self.num_chars:
            self.screen[row, self.pointers[row]] = ch
    # write the whole row(only used for SUB)
    # write 123
    def write_row(self, row, number):
        for i, s in enumerate(reversed("%s" % number)):
            self.screen[row, -(i+1)] = int(s) + 1 # TODO why + 1, is it because they want to reseve for 0 for null value?
        self.screen[row, -(i+2)] = 0
        self.set_pointer(row, (self.screen.width-i-1))

    # issues here
    def copy_output_row_to_in1_row(self):
        self.terminal.add_log("#####copy cat")
        for index in reversed(range(self.pointers[3], self.screen.width)):
            self.terminal.add_log("#index %d" % (index))
            ch = self.screen[3, index]
            if 0 <= ch < self.num_chars:
                self.screen[0, index] = ch


    def get_output(self):
        s = ""
        for ch in self.screen[3]:
            if ch > 0:
                s += "%s" % (ch-1)
        return int(s or "0")

    def get_mul2(self):
        s = ""
        for ch in self.screen[5]:
            if ch > 0:
                s += "%s" % (ch-1)
        self.terminal.add_log("get %s" % s)
        return int(s or "0")


class MovePtrProgram(Program):
    output_to_env = True
    PTR_IN1 = 0
    PTR_IN2 = 1
    PTR_CARRY = 2
    PTR_OUT = 3

    TO_LEFT = 0
    TO_RIGHT = 1

    def do(self, env: MultiplicationEnv, args: IntegerArguments):
        ptr_kind = args.decode_at(0)
        left_or_right = args.decode_at(1)
        env.move_pointer(ptr_kind, left_or_right)

class ResetPtrProgram(Program):
    output_to_env = True
    def do(self, env: MultiplicationEnv, args: IntegerArguments):
        env.reset_pointers()


class WriteProgram(Program):
    output_to_env = True
    WRITE_TO_CARRY = 0
    WRITE_TO_OUTPUT = 1

    def do(self, env: MultiplicationEnv, args: IntegerArguments):
        row = 2 if args.decode_at(0) == self.WRITE_TO_CARRY else 3
        digit = args.decode_at(1)
        env.write(row, digit+1)

class CopyProgram(Program):
    output_to_env = True
    def do(self, env: MultiplicationEnv, args: IntegerArguments):
        env.copy_output_row_to_in1_row()

class SubtractProgram(Program):
    output_to_env = True
    def do(self, env: MultiplicationEnv, args: IntegerArguments):
        # TODO should be able to deal with whole degree
        env.write_row(5, env.get_mul2()-1)


class MultiplicationProgramSet: # includes the addition Programset
    MUL = Program('MUL') # multiply mul1 and mul2, when mul2 == 0, stop.
    COPY = CopyProgram('COPY') # copy whatever on the fourth row(the output row) and write on the second row(In2)
    SUB = SubtractProgram('SUB') # subtract mul2 by 1
    NOP = Program('NOP')
    MOVE_PTR = MovePtrProgram('MOVE_PTR', 4, 2)  # PTR_KIND(4), LEFT_OR_RIGHT(2)
    RESET_PTR = ResetPtrProgram('RESET_PTR', 4)  # PTR_KIND(4), LEFT_OR_RIGHT(2)
    WRITE = WriteProgram('WRITE', 2, 10)       # INCARRY_OR_OUT(2), DIGITS(10)
    ADD = Program('ADD')
    ADD1 = Program('ADD1')
    CARRY = Program('CARRY')
    LSHIFT = Program('LSHIFT')
    RSHIFT = Program('RSHIFT')

    def __init__(self):
        self.map = {}
        self.program_id = 0
        self.register(self.MUL)
        self.register(self.SUB)
        self.register(self.COPY)
        self.register(self.NOP)
        self.register(self.MOVE_PTR)
        self.register(self.RESET_PTR)
        self.register(self.WRITE)
        self.register(self.ADD)
        self.register(self.ADD1)
        self.register(self.CARRY)
        self.register(self.LSHIFT)
        self.register(self.RSHIFT)

    def register(self, pg: Program):
        pg.program_id = self.program_id
        self.map[pg.program_id] = pg
        self.program_id += 1

    def get(self, i: int):
        return self.map.get(i)


class MultiplicationTeacher(NPIStep):
    def __init__(self, program_set: MultiplicationProgramSet, terminal: Terminal):
        self.pg_set = program_set
        self.step_queue = None
        self.step_queue_stack = []
        self.sub_program = {}
        self.register_subprogram(program_set.MUL     , self.pg_mul)
        self.register_subprogram(program_set.COPY    , self.pg_primitive)
        self.register_subprogram(program_set.SUB    , self.pg_primitive)
        self.register_subprogram(program_set.MOVE_PTR, self.pg_primitive)
        self.register_subprogram(program_set.RESET_PTR, self.pg_primitive)
        self.register_subprogram(program_set.WRITE   , self.pg_primitive)
        self.register_subprogram(program_set.ADD     , self.pg_add)
        self.register_subprogram(program_set.ADD1    , self.pg_add1)
        self.register_subprogram(program_set.CARRY   , self.pg_carry)
        self.register_subprogram(program_set.LSHIFT  , self.pg_lshift)
        self.register_subprogram(program_set.RSHIFT  , self.pg_rshift)
        self.terminal = terminal

    def reset(self):
        super(MultiplicationTeacher, self).reset()
        self.step_queue_stack = []
        self.step_queue = None

    def register_subprogram(self, pg, method):
        self.sub_program[pg.program_id] = method

    @staticmethod
    # TODO: stack_queue is for one program right?
    def decode_params(env_observation: np.ndarray, arguments: IntegerArguments):
        return env_observation.argmax(axis=1), arguments.decode_all()

    def enter_function(self):
        self.step_queue_stack.append(self.step_queue or [])
        self.step_queue = None

    def exit_function(self):
        self.step_queue = self.step_queue_stack.pop()

    def step(self, env_observation: np.ndarray, pg: Program, arguments: IntegerArguments) -> StepOutput:
        if not self.step_queue:
            # self.terminal.add_log("append subprogram")
            # self.terminal.add_log(pg.description_with_args(arguments))
            # put all my following sub_program in to the step_queue, for example, the size is four for mul_program
            self.step_queue = self.sub_program[pg.program_id](env_observation, arguments)
        if self.step_queue:
            # self.terminal.add_log("hello")
            # If there are sub_programs that I need to execute
            ret = self.convert_for_step_return(self.step_queue[0])
            # self.terminal.add_log("get subprogram Stepoutput")
            # self.terminal.add_log(ret)
            # remove the subprogram that I have execute
            self.step_queue = self.step_queue[1:]
        else:
            ret = StepOutput(PG_RETURN, None, None)
            # if there is no sub_prgorams that I need to execute
        return ret

    @staticmethod

    def convert_for_step_return(step_values: tuple) -> StepOutput:
        #
        if len(step_values) == 3:
            # this is the last step in my primitive function, with the first item specifying PG_RETURN
            return StepOutput(step_values[0], step_values[1], IntegerArguments(step_values[2]))
        else:

            return StepOutput(PG_CONTINUE, step_values[0], IntegerArguments(step_values[1]))

    @staticmethod
    def pg_primitive(env_observation: np.ndarray, arguments: IntegerArguments):
        return None

    def pg_mul(self, env_observation: np.ndarray, arguments: IntegerArguments):
        self.terminal.add_log("pg_mul")
        ret = []
        (in1, in2, carry, output, mul1, mul2), (a1, a2, a3) = self.decode_params(env_observation, arguments)
        self.terminal.add_log("in1: {}, in2: {}, carry: {} mul1: {}, mul2: {}".format(in1-1, in2-1, carry-1, mul1-1, mul2-1))
        # the zero means the pointer location has nothing, instead of a zero number
        if mul1 == 0 and mul2 == 0:
            return None

        if mul1 == 1 or mul2 == 1:
            self.terminal.add_log("mul1 or mul2 is zero")
            return None

        ret.append((self.pg_set.SUB, None))
        ret.append((self.pg_set.ADD, None))
        ret.append((self.pg_set.COPY, None))
        ret.append((self.pg_set.RESET_PTR, None))

        return ret

    def pg_add(self, env_observation: np.ndarray, arguments: IntegerArguments):
        self.terminal.add_log("pg_add")
        ret = []
        (in1, in2, carry, output, mul1, mul2), (a1, a2, a3) = self.decode_params(env_observation, arguments)

        if in1 == 0 and in2 == 0 and carry == 0:
            self.terminal.add_log("nothing to add")
            return None
        self.terminal.add_log("in1: {}, in2: {}, carry: {}".format(in1-1, in2-1, carry-1))
        ret.append((self.pg_set.ADD1, None))
        ret.append((self.pg_set.LSHIFT, None))
        return ret

    def pg_add1(self, env_observation: np.ndarray, arguments: IntegerArguments):
        self.terminal.add_log("pg_add1")
        ret = []
        p = self.pg_set
        (in1, in2, carry, output, mul1, mul2), (a1, a2, a3) = self.decode_params(env_observation, arguments)
        result = self.sum_ch_list([in1, in2, carry])
        self.terminal.add_log("in1: {}, in2: {}".format(in1-1, in2-1))
        ret.append((p.WRITE, (p.WRITE.WRITE_TO_OUTPUT, result % 10)))
        if result > 9:
            self.terminal.add_log("carry!")
            ret.append((p.CARRY, None))
    ##### TODO Yo! PG_RETURN  here! because this program will for sure terminate, we don't do add1 on the same position again
        ret[-1] = (PG_RETURN, ret[-1][0], ret[-1][1])
        return ret

    @staticmethod
    def sum_ch_list(ch_list):
        ret = 0
        for ch in ch_list:
            if ch > 0:
                ret += ch - 1
        return ret

    def pg_carry(self, env_observation: np.ndarray, arguments: IntegerArguments):
        ret = []
        p = self.pg_set
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_CARRY, p.MOVE_PTR.TO_LEFT)))
        ret.append((p.WRITE, (p.WRITE.WRITE_TO_CARRY, 1)))
        ret.append((PG_RETURN, p.MOVE_PTR, (p.MOVE_PTR.PTR_CARRY, p.MOVE_PTR.TO_RIGHT)))
        return ret

    def pg_lshift(self, env_observation: np.ndarray, arguments: IntegerArguments):
        ret = []
        p = self.pg_set
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_IN1, p.MOVE_PTR.TO_LEFT)))
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_IN2, p.MOVE_PTR.TO_LEFT)))
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_CARRY, p.MOVE_PTR.TO_LEFT)))
        ret.append((PG_RETURN, p.MOVE_PTR, (p.MOVE_PTR.PTR_OUT, p.MOVE_PTR.TO_LEFT)))
        return ret

    def pg_rshift(self, env_observation: np.ndarray, arguments: IntegerArguments):
        ret = []
        p = self.pg_set
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_IN1, p.MOVE_PTR.TO_RIGHT)))
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_IN2, p.MOVE_PTR.TO_RIGHT)))
        ret.append((p.MOVE_PTR, (p.MOVE_PTR.PTR_CARRY, p.MOVE_PTR.TO_RIGHT)))
        ret.append((PG_RETURN, p.MOVE_PTR, (p.MOVE_PTR.PTR_OUT, p.MOVE_PTR.TO_RIGHT)))
        return ret


def create_char_map():
    char_map = dict((i+1, "%s" % i) for i in range(10))
    char_map[0] = ' '
    return char_map

# num is given at script num is the number of random generated questions
def create_questions(num=100, max_number=10000):
    questions = []
    for in1 in range(1, 10):
        for in2 in range(1, 10):
            questions.append(dict(mul1=in1, mul2=in2))

    for in1 in range(10, 30):
        for in2 in range(10, 30):
            questions.append(dict(mul1=in1, mul2=in2))

    # for _ in range(num):
    #     questions.append(dict(mul1=int(random() * 100), mul2=int(random() * 100)))

    # for _ in range(100):
    #     questions.append(dict(in1=int(random() * 1000), in2=int(random() * 1000)))
    # ??
    # questions += [
    #     dict(mul1=4, mul2=4),
    # ]
    # frist questions in the question
    questions = [ dict(mul1=12, mul2=12),] + questions
    # bigger size questions
    # questions += create_random_questions(num=num, max_number=max_number)
    return questions


def create_random_questions(num=100, max_number=1000):
    questions = []
    for _ in range(num):
        questions.append(dict(mul1=int(random() * max_number), mul2=int(random() * max_number)))
    return questions

# run_npi(multiplication_env, npi_runner, self.program_set.MUL, question)
def run_npi(multiplication_env, npi_runner, program, data):
    data['expect'] = data['mul1'] * data['mul2']

    multiplication_env.setup_problem(data['mul1'], data['mul2'])

    npi_runner.reset()
    # TODO bug here: display_env
    npi_runner.display_env(multiplication_env, force=True)
    npi_runner.npi_program_interface(multiplication_env, program, IntegerArguments())

    data['result'] = multiplication_env.get_output()
    data['correct'] = data['result'] == data['expect']
