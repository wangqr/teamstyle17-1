#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
usage:
    ts17 [-v|--version] [-h|--help]
    ts17 run [-d] [-o <repfile>] [-t <timelimit>] <ai> ...
    ts17 replay <repfile>

options:
    -h, --help     show this message
    -v, --version  show current version

    -d             enable debug mode, allow programmatically pause the game
    -o <repfile>   log to file, if file name is not specified, current time
                   will be used
    -t <timelimit> set the time limit of the game in seconds
'''


import docopt
import queue
import json
import random
import os
import signal
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
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global action_queue
        global game_timer
        while 1:
            if game_timer.current_time > time_limit:
                end_action = action.Action('{"action":"_platform"}', "_end", None)
                if __debug__:
                    print('['+str(game_timer.current_time)+'] put stop sig')
                action_queue.put((0, end_action))
                return
            else:
                time.sleep((time_limit - game_timer.current_time))


action_queue = queue.PriorityQueue()
game_timer = Timer()
time_limit = 0
game_uiobj = None


def push_queue_ai_proxy(obj: str):
    global action_queue
    global game_timer
    timestamp = game_timer.current_time
    act = json.loads(obj).get('action')
    action_name = None
    ret = None
    if act in ["init", "move", "use_skill", "upgrade_skill"]:
        action_name = 'instruction'
    elif act in ["query_map", "query_status"]:
        action_name = 'query'
        ret = queue.Queue()
    action_queue.put((timestamp, action.Action(obj, action_name, ret)))
    ret_str = None
    if ret:
        if __debug__:
            print('['+str(game_timer.current_time)+'] waiting for ret_str')
        ret_str = ret.get(block=True)
        if __debug__:
            print('['+str(game_timer.current_time)+'] core returned \''+str(ret_str)+'\'')
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
    global action_queue
    global game_timer
    global time_limit
    global game_uiobj

    last_action_timestamp = 0

    # init logic
    main_logic = ts17core.interface.Interface()

    game_started = True

    # init ai_proxy
    ai_proxy.start(args['<ai>'], push_queue_ai_proxy)

    #   init ui
    game_uiobj = uiobj.UIObject(push_queue_ai_proxy, ai_id = -1)

    #   get init action
    init_json = '{"action":"init","seed":' + str(random.randrange(0,4294967296)) + '}'
    main_logic.setInstruction(init_json)

    #   init logger
    # run_logger = logger.Run_Logger(init_json)

    if args['-t']:
        time_limit = float(args['-t'])

    if time_limit > 0:
        EndSignalGenerator().start()

    game_timer.start()
    # main loop
    while game_started:
        next_action = action_queue.get(block=True)
        if __debug__:
            print('['+str(game_timer.current_time)+'] \x1b[1;32m>>>>>>>> recv id=' + str(json.loads(next_action[1].action_json).get('ai_id')) +' ' + json.loads(next_action[1].action_json).get('action') + ' '+ next_action[1].action_name +'\x1b[m')
        if next_action[1].action_name == '_pause':
            if args['-d']:
                game_timer.running = not game_timer.running
            else:
                print('illegal action: pause')
            continue
        elif next_action[1].action_name == '_end':
            if __debug__:
                print('['+str(game_timer.current_time)+'] \x1b[1;33mstop sig detected\x1b[m')
            break
        if next_action[0] > last_action_timestamp:
            last_action_timestamp = next_action[0]
        if time_limit and last_action_timestamp > time_limit:
            break
        next_action[1].set_timestamp(last_action_timestamp)
        if next_action[1].action_name != 'query':
            # run_logger.log_action(next_action[1])
            pass
        next_action[1].run(main_logic)
        if __debug__:
            print('['+str(game_timer.current_time)+'] \x1b[1;32m<<<<<<<< fin ' + next_action[1].action_json +'\x1b[m')
    # ai_proxy.stopAI()
    if __debug__:
        print('['+str(game_timer.current_time)+'] \x1b[1;31mquit\x1b[m')
    os.kill(os.getpid(), signal.SIGTERM)


def replay_main(args: dict):
    pass

if __name__=='__main__':
    main()
