#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import main
import json


class Action:
    def __init__(self, action_json, action_name, return_queue):
        self.action_name = action_name
        self.action_json = action_json
        self.return_queue = return_queue
        self.__time_stamp = 0

    def run(self, logic):
        if self.action_name == 'instruction':
            try:
                logic.setInstruction(self.action_json)
            except Exception as e:
                main.root_logger.error('logic exception %s [%s]', (type(e).__name__, str(e)))
        elif self.action_name == 'query':
            try:
                ret = logic.getInstruction(self.action_json)
            except Exception as e:
                main.root_logger.error('logic exception %s [%s]', (type(e).__name__, str(e)))
                ret = '{"message": "logic exception ' + type(e).__name__ + ' [' + str(e) + ']"}'
            main.root_logger.debug('core_ret = %s' % repr(ret))
            q = json.loads(ret)
            q['time'] = self.__time_stamp
            self.return_queue.put(json.dumps(q))
        elif self.action_name == 'time':
            self.return_queue.put('{"time":%d}' % self.__time_stamp)

    def set_timestamp(self, time: int):
        self.__time_stamp = time
        q = json.loads(self.action_json)
        q['time'] = int(time)
        self.action_json = json.dumps(q)
