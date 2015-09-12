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

import argparse
import docopt
import queue
import sys
import time
import threading

import ai_proxy
import action
import core

__version__='0.1-a'

action_queue = queue.PriorityQueue()
game_start_time = 0

def push_queue_ai_proxy(obj: action.Action):
    global action_queue
    global game_start_time
    action_queue.put((time.time() - game_start_time, obj))

def main():
    args = docopt.docopt(__doc__, version='ts17-platform '+__version__+' [ts17-core ver '+core.__version__+']')
    print(args)
    if(args['run']):
        run_main(args)
    elif(args['replay']):
        replay_main(args)
    else:
        docopt.docopt(__doc__, argv=['-h'])

def run_main(args: dict):
    global action_queue
    global game_start_time

    last_action_time_stamp = 0

    # init logic
    #TODO

    # init ai_proxy
    ai_proxy.start(args['<ai>'], push_queue_ai_proxy)

    # init ui
    #TODO

    # init logger
    #TODO

    game_started = True
    game_start_time = time.time()

    time_limit=0
    if(args['-t']):
        time_limit=int(args['-t'])
    # main loop
    while(game_started):
        next_action=action_queue.get(block=True)
        if (next_action[0] > last_action_time_stamp):
            last_action_time_stamp = next_action[0]
        if(last_action_time_stamp > time_limit):
            break
        next_action[1].time_stamp = last_action_time_stamp
        #TODO log action
        next_action[1].run()

def replay_main(args: dict):
    pass

if (__name__=='__main__'):
    main()
