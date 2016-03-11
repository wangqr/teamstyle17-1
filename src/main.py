#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage:
    ts17 [-v|--version] [-h|--help]
    ts17 run [-r <repfile>] [-s <seed>] [-t <timelimit>] [-u <port>] [-V] <ai> ...
    ts17 replay [-u <port>] [-V] <repfile>

options:
    -h, --help     show this message
    -v, --version  show current version

    -r <repfile>   specify the name of the rep file
    -s <seed>      specify the map seed
    -t <timelimit> set the time limit of the game in seconds
    -u <port>      open UI socket on the specified port
    -V             verbose output
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
import logger

import ts17core
import ts17core.interface

__version__ = '1.0'


class Timer:
    def __init__(self, func=None):
        if func is None:
            if time.__dict__.get('perf_counter'):
                func = time.perf_counter
            else:
                func = time.clock
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

    @current_time.setter
    def current_time(self, value: float):
        self.elapsed += value - self.current_time

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


class EndSignalGenerator(threading.Thread):
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
        if self.level > self.__class__.DEBUG:
            return
        sys.stderr.write(self.__set_debug_color + self.log('DEBUG', fmt, *args) + self.__reset_color)

    def info(self, fmt, *args):
        if self.level > self.__class__.INFO:
            return
        sys.stderr.write(self.log('INFO', fmt, *args))

    def warn(self, fmt, *args):
        if self.level > self.__class__.WARN:
            return
        sys.stderr.write(self.__set_warning_color + self.log('WARNING', fmt, *args) + self.__reset_color)

    def error(self, fmt, *args):
        if self.level > self.__class__.ERROR:
            return
        sys.stderr.write(self.__set_error_color + self.log('ERROR', fmt, *args) + self.__reset_color)

    def critical(self, fmt, *args):
        if self.level > self.__class__.CRITICAL:
            return
        sys.stderr.write(self.__set_error_color + self.log('CRITICAL', fmt, *args) + self.__reset_color)

    def basic_config(self, **kwargs):
        self.level = int(kwargs.get('level', self.__class__.INFO))


class Game:
    MAX_DELAY_ROUNDS = 1
    ROUNDS_PER_SEC = 100

    def __init__(self, rep_file_name: str, verbose: bool, time_limit: float, seed: int, start_paused=False,
                 player_num=2):
        if seed is None:
            seed = random.randrange(0, 4294967296)
        self._seed = seed
        self._timer = Timer()
        self._info_callback = lambda _: None
        self._logger = Logging(
            timer=lambda: '%d @ %.6f' % (self.__logic_time(self._timer.current_time), self._timer.current_time))
        self._logger.info('game seed = %d', self._seed)
        self._logger.basic_config(level=Logging.DEBUG if verbose else Logging.INFO)
        self._run_logger = logger.RunLogger(filename=rep_file_name)
        self._run_logger.start()
        self._time_limit = time_limit
        self._logic = ts17core.interface.Interface(self.__info_callback)
        init_json = '{"action":"init","seed":' + str(self._seed) + ',"player":' + str(player_num) + '}'
        self._logic.setInstruction(init_json)
        self._run_logger.sig.put(init_json)
        self._queue = queue.PriorityQueue()
        self._last_action_timestamp = 0
        self.__action_count = 0
        self._start_paused = start_paused
        self.__pause_field = 0
        if time_limit:
            EndSignalGenerator(game_obj=self, time_limit=time_limit).start()
        self.__mutex = threading.Lock()
        self._sync = False

    def mainloop(self):
        if not self._start_paused:
            self.__pause_field = 0
            self._timer.start()
        else:
            self.__pause_field = 1
        while not self._time_limit or self.current_time < self._time_limit:
            if self._sync and self._queue.empty():
                self._sync = False
                if self.__pause_field == 0:
                    self._timer.start()
            next_action = None
            while next_action is None and (
                        not self._queue.empty() or self.__logic_time(self.current_time) == self._last_action_timestamp):
                try:
                    next_action = self._queue.get(block=True, timeout=self.__timeout_before_next_tick)
                except queue.Empty:
                    pass
            if next_action is None:
                self._logic.nextTick()
                self._last_action_timestamp += 1
                self._logger.debug('')
                continue
            self._logger.debug('>>>>>>>> recv %s', next_action[2].action_json or '')
            if next_action[2].action_name == '_pause':
                self.__pause_field ^= (1 << (1 + json.loads(next_action[2].action_json)['ai_id']))
                if self.__pause_field:
                    self._timer.stop()
                else:
                    self._timer.start()
                self._logger.debug('<<<<<<<< fin')
                continue
            elif next_action[2].action_name == '_end':
                self._logger.info('terminate signal received')
                self._logger.debug('<<<<<<<< fin')
                break
            elif next_action[2].action_name == 'game_end':
                self._logger.debug('<<<<<<<< fin')
                self._logger.info('****GAME END****')
                self._logger.info('WINNER = %d', json.loads(next_action[2].action_json)['ai_id'])
                next_action[2].set_timestamp(self._last_action_timestamp)
                self._run_logger.sig.put(next_action[2].action_json)
                break
            if self.__logic_time(next_action[0]) > self._last_action_timestamp:
                if not self._sync and self.__logic_time(
                        next_action[0]) - self._last_action_timestamp > self.__class__.MAX_DELAY_ROUNDS:
                    self._timer.stop()
                    self._sync = True
                    self._logger.warn('logic is %d rounds slower than main timer, trying to sync by pausing ...',
                                      self.__logic_time(next_action[0]) - self._last_action_timestamp)
                while self.__logic_time(next_action[0]) > self._last_action_timestamp:
                    self._logic.nextTick()
                    self._last_action_timestamp += 1
            next_action[2].set_timestamp(self._last_action_timestamp)
            if next_action[2].action_name == 'instruction':
                self._run_logger.sig.put(next_action[2].action_json)
            next_action[2].run(self._logic)
            self._logger.debug('<<<<<<<< fin')
        self._logger.info('clean up')
        self._run_logger.exit()
        self._run_logger.join()

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
        return int(timestamp * Game.ROUNDS_PER_SEC)

    @property
    def __timeout_before_next_tick(self):
        return self.current_time % (1 / self.__class__.ROUNDS_PER_SEC)

    def __info_callback(self, obj: str):
        if obj.find('"end"') >= 0:
            j = json.loads(obj)
            winner_id = -2
            for js in j:
                if js['info'] == 'end':
                    winner_id = js['ai_id']
            self.enqueue(0, action.Action('{"action":"game_end", "ai_id":%d}' % winner_id, 'game_end', None))
        self._info_callback(obj)


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
    elif act in ["query_time"]:
        ret = queue.Queue()
        game_obj.enqueue(timestamp, action.Action(obj, 'time', ret))
    elif act and act[0] == '_':
        game_obj.enqueue(float(0.),
                         action.Action('{"action":"_platform","ai_id":%d}' % json.loads(obj).get('ai_id'), act, None))
    ret_str = None
    if ret:
        root_logger.debug('waiting for ret_str')
        ret_str = ret.get(block=True)
        root_logger.debug('core returned \'' + str(ret_str) + '\'')
    return ret_str


def _sigint_handler(*args, **kwargs):
    global root_logger
    root_logger.error('SIGINT')
    time.sleep(0.3)
    os.kill(os.getpid(), signal.SIGTERM)


def main():
    global root_logger
    signal.signal(signal.SIGINT, _sigint_handler)
    args = docopt.docopt(__doc__,
                         version='ts17-platform ' + __version__ + ' [ts17-core ver ' + ts17core.__version__ + ']')
    root_logger.basic_config(level=(Logging.DEBUG if args['-V'] else Logging.INFO))
    if args['run']:
        run_main(args)
        root_logger.info('quit.')
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)
    elif args['replay']:
        replay_main(args)
        root_logger.info('quit.')
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        docopt.docopt(__doc__, argv=['-h'])


def info_call_back(ui_obj, obj: str):
    global root_logger
    root_logger.debug('core info %s', obj)
    ui_obj.enqueue(obj)


def run_main(args: dict):
    global root_logger

    # check duplicate
    if len(args['<ai>']) != len(set(args['<ai>'])):
        root_logger.error('Duplicate items in AI list. You should make copies if needed.')
        return

    for ai in args['<ai>']:
        if not os.path.isfile(ai) or not ai.endswith(('.dll', '.so')):
            root_logger.error('"%s" is not a valid AI.', x)
            return

    # check time limit
    if args['-t'] is not None:
        try:
            args['-t'] = float(args['-t'])
        except ValueError:
            root_logger.error('Time limit should be a positive number.')
            return
        if args['-t'] <= 0:
            root_logger.error('Time limit should be a positive number.')
            return

    # check seed
    if args['-s'] is not None:
        try:
            args['-s'] = int(args['-s'])
        except ValueError:
            root_logger.error('Seed should be in range [0, 4294967296).')
            return
        if args['-s'] < 0 or args['-s'] >= 4294967296:
            root_logger.error('Seed should be in range [0, 4294967296).')
            return

    rep_file_name = args['-r'] or ('ts17_' + time.strftime('%m%d%H%M%S') + '.rpy')

    if not rep_file_name.endswith('.rpy'):
        rep_file_name += '.rpy'

    game_obj = Game(time_limit=float(args['-t'] or 0), seed=int(args['-s']) if args['-s'] else None,
                    player_num=len(args['<ai>']), verbose=args['-V'], rep_file_name=rep_file_name)

    # init ai_proxy
    ai_proxy.start(args['<ai>'], lambda x: push_queue_ai_proxy(x, game_obj))

    # init ui
    game_ui_obj = None
    if args['-u']:
        game_ui_obj = uiobj.UIObject(game_obj, ai_id=-1, port=int(args['-u']))
        game_obj._info_callback = lambda x: info_call_back(game_ui_obj, x)
        game_ui_obj.start()

    # main loop
    game_obj.mainloop()

    # exit ui thread
    if game_ui_obj and game_ui_obj.is_alive():
        game_ui_obj.exit()

    # ai_proxy.stopAI()
    root_logger.info('quit.')

    time.sleep(0.3)
    os.kill(os.getpid(), signal.SIGTERM)


def replay_main(args: dict):
    global root_logger

    rep_file_name = args['<repfile>']

    if not rep_file_name.endswith('.rpy'):
        rep_file_name += '.rpy'

    if not os.path.isfile(rep_file_name):
        root_logger.error('"%s" is not a valid replay file.', rep_file_name)
        return

    rep_mgr = logger.RepManager(rep_file_name=rep_file_name, verbose=args['-V'])

    game_ui_obj = None
    if args['-u']:
        game_ui_obj = uiobj.UIObject(rep_mgr, ai_id=-1, port=int(args['-u']))
        rep_mgr._info_callback = lambda x: info_call_back(game_ui_obj, x)
        rep_mgr._ui_running = lambda: bool(
            game_ui_obj and game_ui_obj.is_alive() and game_ui_obj.send_thread and game_ui_obj.send_thread.is_alive())
        game_ui_obj.start()

    rep_mgr.mainloop()

    if game_ui_obj and game_ui_obj.is_alive():
        game_ui_obj.exit()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Unexpected error.')
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)
'''

if __name__ == '__main__':
    main()
'''
