#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage:
    ts17 [-v|--version] [-h|--help]
    ts17 run [-d] [-o <repfile>] [-s <seed>] [-t <timelimit>] <ai> ...
    ts17 replay <repfile>

options:
    -h, --help     show this message
    -v, --version  show current version

    -d             enable debug mode, allow programmatically pause the game
    -o <repfile>   log to file, if file name is not specified, current time
                   will be used
    -s <seed>      specify the map seed
    -t <timelimit> set the time limit of the game in seconds
"""


import docopt
import queue
import json
import random
import os
import signal
import sys
import time
import threading

import ai_proxy
import action
import uiobj
#   Bug remain
# import logger

import ts17core
import ts17core.interface

__version__ = '0.1-a'


class Timer:
    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is None:
            self._start = self._func()

    def stop(self):
        if self._start is not None:
            end = self._func()
            self.elapsed += end - self._start
            self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    @running.setter
    def running(self, value: bool):
        if value:
            self.start()
        else:
            self.stop()

    @property
    def current_time(self):
        return self.elapsed if self._start is None else self.elapsed + self._func() - self._start

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


class EndSignalGenerator (threading.Thread):
    def __init__(self, game_obj, time_limit: float):
        threading.Thread.__init__(self)
        self.daemon = True
        self._game = game_obj
        self._limit = time_limit

    def run(self):
        global root_logger
        while 1:
            if self._game.current_time > self._limit:
                root_logger.info('put stop signal')
                self._game.enqueue(0, action.Action('{"action":"_platform"}', "_end", None))
                return
            else:
                time.sleep(self._limit - self._game.current_time)


class Logging:
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self, timer=(lambda: time.ctime()[4:-5])):
        self.level = self.__class__.INFO
        self.__set_error_color = ''
        self.__set_warning_color = ''
        self.__set_debug_color = ''
        self.__reset_color = ''
        self.__get_time_str = timer
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            self.__set_error_color = '\x1b[31m'
            self.__set_warning_color = '\x1b[33m'
            self.__set_debug_color = '\x1b[32m'
            self.__reset_color = '\x1b[m'

    def log(self, level, fmt, *args):
        return '%s - [%s] %s\n' % (level, self.__get_time_str(), fmt % args)

    def dummy(self, *args, **kwargs):
        pass

    def debug(self, fmt, *args):
        sys.stderr.write(self.__set_debug_color + self.log('DEBUG', fmt, *args) + self.__reset_color)

    def info(self, fmt, *args):
        sys.stderr.write(self.log('INFO', fmt, *args))

    def warn(self, fmt, *args):
        sys.stderr.write(self.__set_warning_color + self.log('WARNING', fmt, *args) + self.__reset_color)

    def error(self, fmt, *args):
        sys.stderr.write(self.__set_error_color + self.log('ERROR', fmt, *args) + self.__reset_color)

    def critical(self, fmt, *args):
        sys.stderr.write(self.__set_error_color + self.log('CRITICAL', fmt, *args) + self.__reset_color)

    def basic_config(self, **kwargs):
        self.level = int(kwargs.get('level', self.__class__.INFO))
        if self.level > self.__class__.DEBUG:
            self.debug = self.dummy


class Game:
    def __init__(self, time_limit=0., seed=None, info_callback=(lambda x: None), start_paused=False, player_num=2):
        if seed is None:
            seed = random.randrange(0, 4294967296)
        self._seed = seed
        self._timer = Timer()
        self._info_callback = info_callback
        self._logger = Logging(timer=lambda: '%.2f' % self._timer.current_time)
        self._logger.info('game seed = %d', self._seed)
        self._logger.level = Logging.DEBUG
        self._time_limit = time_limit
        self._logic = ts17core.interface.Interface()
        init_json = '{"action":"init","seed":' + str(self._seed) + ',"player":'+str(player_num)+'}'
        self._logic.setInstruction(init_json)
        self._queue = queue.PriorityQueue()
        self._last_action_timestamp = 0
        self.__action_count = 0
        if not start_paused:
            self._timer.start()
        if time_limit:
            EndSignalGenerator(game_obj=self, time_limit=time_limit).start()
        self.__mutex = threading.Lock()

    @property
    def seed(self) -> int:
        return self._seed

    def mainloop(self):
        while 1:
            next_action = self._queue.get(block=True)
            self._logger.debug('>>>>>>>> recv %s', next_action[2].action_json or '')
            if next_action[2].action_name == '_pause':
                self._timer.running = not self._timer.running
                continue
            elif next_action[2].action_name == '_end':
                self._logger.info('stop signal received')
                break
            if self._time_limit and next_action[0] > self._time_limit:
                break
            if self.__logic_time(next_action[0]) > self._last_action_timestamp:
                ret = None
                while self.__logic_time(next_action[0]) > self._last_action_timestamp:
                    ret = self._logic.nextTick()
                    self._last_action_timestamp += 1
                self._info_callback(ret)
            next_action[2].set_timestamp(self._last_action_timestamp)
            if next_action[2].action_name != 'query':
                # run_logger.log_action(next_action[2])
                pass
            next_action[2].run(self._logic)
            self._logger.debug('<<<<<<<< fin')

    def enqueue(self, timestamp, act):
        self.__mutex.acquire()
        self._queue.put((timestamp, self.__action_count, act))
        self.__action_count += 1
        self.__mutex.release()

    @property
    def current_time(self) -> float:
        return self._timer.current_time

    @staticmethod
    def __logic_time(timestamp: float) -> int:
        return int(timestamp)


game_uiobj = None
root_logger = Logging()


def push_queue_ai_proxy(obj: str, game_obj: Game):
    global root_logger
    timestamp = game_obj.current_time
    act = json.loads(obj).get('action')
    ret = None
    if act in ["init", "move", "use_skill", "upgrade_skill"]:
        game_obj.enqueue(timestamp, action.Action(obj, 'instruction', None))
    elif act in ["query_map", "query_status"]:
        ret = queue.Queue()
        game_obj.enqueue(timestamp, action.Action(obj, 'query', ret))
    elif act and act[0] == '_':
        game_obj.enqueue(float(0.), action.Action('{"action":"_platform"}', act, None))
    ret_str = None
    if ret:
        root_logger.debug('waiting for ret_str')
        ret_str = ret.get(block=True)
        root_logger.debug('core returned \''+str(ret_str)+'\'')
    return ret_str


def main():
    if __debug__:
        print('__debug__ == ' + str(__debug__))
    args = docopt.docopt(__doc__, version = 'ts17-platform ' + __version__ + ' [ts17-core ver ' + ts17core.__version__ + ']')
    if args['run']:
        run_main(args)
    elif args['replay']:
        replay_main(args)
    else:
        docopt.docopt(__doc__, argv=['-h'])


def run_main(args: dict):
    global game_uiobj

    game_obj = Game(time_limit=float(args['-t'] or 0), seed=args['-s'], player_num=len(args['<ai>']))

    # init ai_proxy
    ai_proxy.start(args['<ai>'], lambda x: push_queue_ai_proxy(x, game_obj))

    #   init ui
    game_uiobj = uiobj.UIObject(lambda x: push_queue_ai_proxy(x, game_obj), ai_id=-1)

    # main loop
    game_obj.mainloop()

    # ai_proxy.stopAI()
    if __debug__:
        print('['+str(game_timer.current_time)+'] \x1b[1;31mquit\x1b[m')
    os.kill(os.getpid(), signal.SIGTERM)


def replay_main(args: dict):
    pass

if __name__=='__main__':
    main()
