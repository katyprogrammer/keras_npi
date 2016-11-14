#!/usr/bin/env python
# coding: utf-8
# anything related to terminal display is here
import curses
import numpy as np

from npi.core import Program, IntegerArguments, NPIStep, StepOutput, StepInput, StepInOut, ResultLogger

__author__ = 'k_morishita'


class Screen:
    data = None

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.init_screen()

    def init_screen(self):
        self.data = np.zeros([self.height, self.width], dtype=np.int8)

    def fill(self, ch):
        self.data.fill(ch)

    def as_float32(self):
        return self.data.astype(np.float32)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item]


class Terminal:
    W_TOP = 1
    W_LEFT = 1
    LOG_WINDOW_HEIGHT = 40
    LOG_WINDOW_WIDTH = 160
    INFO_WINDOW_HEIGHT = 10
    INFO_WINDOW_WIDTH = 40

    main_window = None
    info_window = None
    log_window = None

    def __init__(self, stdscr, char_map=None):
        print(type(stdscr))
        self.stdscr = stdscr
        self.char_map = char_map or dict((ch, chr(ch)) for ch in range(128))
        self.log_list = []
        print("finish init")

    def init_window(self, width, height):
        # _curses.error: must call initscr() first
        # curses.initscr()
        print("start init_window")
        curses.curs_set(0)
        border_win = curses.newwin(height + 2, width + 2, self.W_TOP, self.W_LEFT)  # h, w, y, x
        border_win.box()
        self.stdscr.refresh()
        border_win.refresh()
        self.main_window = curses.newwin(height, width, self.W_TOP + 1, self.W_LEFT + 1)
        self.main_window.refresh()
        self.main_window.timeout(1)
        self.info_window = curses.newwin(self.INFO_WINDOW_HEIGHT, self.INFO_WINDOW_WIDTH,
                                         self.W_TOP + 1, self.W_LEFT + width + 2)
        self.log_window = curses.newwin(self.LOG_WINDOW_HEIGHT, self.LOG_WINDOW_WIDTH,
                                        self.W_TOP + max(height, self.INFO_WINDOW_HEIGHT) + 5, self.W_LEFT)
        self.log_window.refresh()
        print("finish init_window")

    def wait_for_key(self):
        self.stdscr.getch()

    def update_main_screen(self, screen):
        for y in range(screen.height):
            line = "".join([self.char_map[ch] for ch in screen[y]])
            self.ignore_error_add_str(self.main_window, y, 0, line)

    def update_main_window_attr(self, screen, y, x, attr):
        ch = screen[y, x]
        self.ignore_error_add_str(self.main_window, y, x, self.char_map[ch], attr)

    def refresh_main_window(self):
        self.main_window.refresh()

    def update_info_screen(self, info_list):
        self.info_window.clear()
        for i, info_str in enumerate(info_list):
            self.info_window.addstr(i, 2, info_str)
        self.info_window.refresh()

    def add_log(self, line):
        self.log_list.insert(0, str(line)[:self.LOG_WINDOW_WIDTH])
        self.log_list = self.log_list[:self.LOG_WINDOW_HEIGHT-1]
        self.log_window.clear()
        for i, line in enumerate(self.log_list):
            line = str(line) + " " * (self.LOG_WINDOW_WIDTH - len(str(line)))
            self.log_window.addstr(i, 0, line)
        self.log_window.refresh()

    @staticmethod
    # TODO what is she trying to say here?
    def ignore_error_add_str(win, y, x, s, attr=curses.A_NORMAL):
        """一番右下に書き込むと例外が飛んでくるけど、漢は黙って無視するのがお作法らしい？"""
        try:
            win.addstr(y, x, s, attr)
        except curses.error:
            pass


def show_env_to_terminal(terminal, env):
    terminal.update_main_screen(env.screen)
    for i, p in enumerate(env.pointers):
        terminal.update_main_window_attr(env.screen, i, p, curses.A_REVERSE)
    terminal.refresh_main_window()

# reset max_depth and max_step
class TerminalNPIRunner:
    def __init__(self, terminal: Terminal, model: NPIStep=None, recording=True, max_depth=100, max_step=10000, result_logger=ResultLogger('result_multiplication.log')):
        self.terminal = terminal
        self.model = model
        self.steps = 0
        self.step_list = []
        self.alpha = 0.5
        self.verbose = True
        self.recording = recording
        self.max_depth = max_depth
        self.max_step = max_step
        self.result_logger = result_logger

    def reset(self):
        self.steps = 0
        self.step_list = []
        self.model.reset()

    def display_env(self, env, force=False):
        if (self.verbose or force) and self.terminal:
            show_env_to_terminal(self.terminal, env)

    def display_information(self, program: Program, arguments: IntegerArguments, result: StepOutput, depth: int):
        if self.verbose and self.terminal:
            information = [
                "Step %2d Depth: %2d" % (self.steps, depth),
                program.description_with_args(arguments),
                'r=%.2f' % result.r,
            ]
            if result.program:
                information.append("-> %s" % result.program.description_with_args(result.arguments))
            self.terminal.update_info_screen(information)
            self.wait()

    def npi_program_interface(self, env, program: Program, arguments: IntegerArguments, depth=0):
        if self.max_depth < depth or self.max_step < self.steps:
            if self.max_step < self.steps:
                print("stop iteration becasue there are too many steps")
                self.terminal.add_log("stop iteration becasue it's too deep")
            if self.max_depth < depth:
                print("stop iteration becasue there are too many steps")
                self.terminal.add_log("stop iteration becasue it's too deep")
            raise StopIteration()

        self.model.enter_function()
        # self.terminal.add_log("enter function")
        result = StepOutput(0, None, None)
        # self.terminal.add_log(result)
        while result.r < self.alpha:
            self.terminal.add_log("in a function")
            self.steps += 1
            if self.max_step < self.steps:
                print("stop iteration becasue there are too many steps")
                self.terminal.add_log("stop iteration becasue there are too many steps")
                raise StopIteration()
            env_observation = env.get_observation()
            #self.terminal.add_log(env_observation)
            # run our model for one step
            # result is a StepOutput
            result = self.model.step(env_observation, program, arguments.copy())
            self.terminal.add_log("after excuting funciton")
            # self.terminal.add_log(result)
            # what's the intuition of recording
            if self.recording:
                self.step_list.append(StepInOut(StepInput(env_observation, program, arguments.copy()), result))
            self.display_information(program, arguments, result, depth)

            if program.output_to_env:
                # self.terminal.add_log("output_to_env")
                program.do(env, arguments.copy())
                self.display_env(env)
            else:
                self.terminal.add_log(str(program))
                if result.program:  # modify original algorithm
                    # self.terminal.add_log("execute sub_program")
                    self.npi_program_interface(env, result.program, result.arguments, depth=depth+1)
        self.terminal.add_log("exit funtion")
        self.model.exit_function()

    def wait(self):
        self.terminal.wait_for_key()
