#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import queue
import sys
import time
import threading


import core.src
import ai_agent

__version__='0.1-a'

action_queue = queue.PriorityQueue()
game_start_time = 0
last_action_time_stamp = 0

def arg_handler() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Teamstyle 17 platform')
    parser.add_argument('-v', '--version', action='version', version='ts17-platform '+__version__+' [ts17-core ver '+core.src.__version__+']')
    parser.add_argument('-l', '--log', default=time.strftime('%Y%m%d%H%M%S')+'.rpy', type=argparse.FileType('w'), help='set the name of the replay file (default: current time)')
    parser.add_argument('-V', '--verbose', action='store_true', help='enable verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='allow controlling game procedure by ui')
    parser.add_argument('-r', '--replay', action='store_true', help='replay mode')
    parser.add_argument('ai', nargs='+', help='the path of the AI file')
    return parser.parse_args()

def push_queue_ai_agent(obj):
    #obj.time_stamp = time.time() - gameStartTime
    action_queue.put((time.time() - game_start_time, obj))

def main():
    args = arg_handler()

    # init logic
    #TODO

    # init ai_agent
    ai_agent.start(args.ai, push_queue_ai_agent)

    # init ui
    #TODO

    # init logger
    #TODO

    game_started = True
    game_start_time = time.time()

    # main loop
    while(game_started):
        next_action=action_queue.get(block=true)
        if (next_action[0] > last_action_time_stamp):
            last_action_time_stamp = next_action[0]
        next_action[1].time_stamp = last_action_time_stamp
        #TODO log action
        next_action[1].run()

if (__name__=='__main__'):
	main()
