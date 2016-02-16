#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import threading


class Action:
    def __init__(self, action_json, action_name, return_queue):
        self.action_name = action_name
        self.action_json = action_json
        self.return_queue = return_queue

    def run(self, logic):
        if self.action_name == 'instruction':
            try:
                logic.setInstruction(self.action_json)
            except Exception:
                pass
        elif self.action_name == 'query':
            try:
                ret = logic.getInstruction(self.action_json)
            except Exception as e:
                print('[ERROR] \x1b[1;31mlogic exception ' + type(e).__name__ + ' [' + str(e) + ']\x1b[m')
                ret = '{"message": "logic exception ' + type(e).__name__ + ' [' + str(e) + '"]}'
            self.return_queue.put(ret)

    def set_timestamp(self, time: int):
        q = json.loads(self.action_json)
        q['time'] = int(time)
        self.action_json = json.dumps(q)
