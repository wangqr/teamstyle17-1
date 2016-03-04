#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import json
import queue
import time
import threading

import main
import action
import ts17core


class RunLogger(threading.Thread):
    def __init__(self, filename):
        threading.Thread.__init__(self)
        if not filename:
            filename = 'ts17_' + time.strftime('%m%d%H%M%S') + '.rpy'
        self._filename = filename
        self._fp = gzip.open(self._filename, 'wt', encoding='utf-8')
        self.sig = queue.Queue()

    def run(self):
        while 1:
            q = self.sig.get(block=True)
            if q == 0:
                self._fp.close()
                break
            self._fp.write(q)
            self._fp.write('\n')

    def exit(self):
        self.sig.put(0)


class RepGame:
    MAX_DELAY_ROUNDS = 1
    ROUNDS_PER_SEC = 100

    def __init__(self, start_paused=False, verbose=False):
        self._timer = main.Timer()
        self._info_callback = lambda _: None
        self._logger = main.Logging(
            timer=lambda: '%d @ %.6f' % (self.__logic_time(self._timer.current_time), self._timer.current_time))
        self._logger.basic_config(level=main.Logging.DEBUG if verbose else main.Logging.INFO)
        self._logic = ts17core.interface.Interface(self.__info_callback)
        self.queue = queue.Queue()
        self.sig = queue.Queue()
        self._last_action_timestamp = 0
        self._paused = start_paused

    def mainloop(self):
        action_buffer = None
        if not self._paused:
            self._timer.start()
        while 1:
            next_action = None
            if self.queue.empty():
                break
            t = 0
            if action_buffer is not None:
                t = self.__timeout_before_round(min(action_buffer[0], self._last_action_timestamp + 1))
            if self._paused or not self.sig.empty() or t > 0:
                try:
                    q = self.sig.get(block=True, timeout=(None if self._paused else t))
                except queue.Empty:
                    q = None
                if q == 0:
                    break
                elif q == 1:
                    self._timer.running = not self._timer.running
                    self._paused = not self._paused
                    continue
                elif type(q) == tuple:
                    """
                    平台查询指令 (str, queue)
                    """
                    next_action = (self._last_action_timestamp, action.Action(q[0], 'query', q[1]))
            if next_action is None:
                if action_buffer and action_buffer[0] <= self.__logic_time(self.current_time):
                    next_action = action_buffer
                    action_buffer = None
                else:
                    next_action = self.queue.get()
            while next_action[0] > self._last_action_timestamp and self.__logic_time(
                    self.current_time) > self._last_action_timestamp:
                self._logic.nextTick()
                self._last_action_timestamp += 1
            if next_action[0] < self.__logic_time(self.current_time):
                self._timer.current_time = self.__real_time(next_action[0] + 1)
            elif next_action[0] > self.__logic_time(self.current_time):
                action_buffer = next_action
                continue
            j_str = next_action[1].action_json
            if j_str.endswith('\n'):
                j_str = j_str.replace('\n', '')
            self._logger.debug('>>>>>>>> recv %s', j_str or '')
            while next_action[0] > self._last_action_timestamp:
                self._logic.nextTick()
                self._last_action_timestamp += 1
            next_action[1].run(self._logic)
            self._logger.debug('<<<<<<<< fin')

    def __info_callback(self, obj: str):
        if obj.find('"end"') >= 0:
            self.sig.put(0)
        self._info_callback(obj)

    @property
    def current_time(self) -> float:
        return self._timer.current_time

    @staticmethod
    def __logic_time(timestamp: float) -> int:
        return int(timestamp * RepGame.ROUNDS_PER_SEC)

    @staticmethod
    def __real_time(timestamp: int) -> float:
        return timestamp / RepGame.ROUNDS_PER_SEC

    def __timeout_before_round(self, timestamp: int):
        return timestamp / RepGame.ROUNDS_PER_SEC - self.current_time


'''
    # Run current logic with instructions from UI_GROUP
    def run_logic (self):
        pass
        # check with UI_GROUP about the specification
        # 'last_action_id' should be constantly updated whenever an action is operated

    def new_logic (self, init_time):
        self.logic_list[self.logic_count] = Logic(init_time)		# The number of arguments of 'Logic.__init__()' requires further notice
        self.current_logic = logic_count
        self.logic_count += 1

        # action_list[0] is the initialization action
        # ??? Object of class 'Interface'?
        # ??? 'setInstruction' should include logic_id
        setInstruction(self.action_list[0])
        action_id = 1
        while (action_id < self.action_count) and (self.action_list[action_id]['time'] < init_time):
            # Object of class 'Interface'?
            setInstruction(self.action_list[action_id])
            action_id += 1
        self.logic_list[self.logic_count].last_action_id = action_id - 1
        run_logic()

    def time_travel (self, time_dest):
        logic_id = 0
        nearest_logic = -1
        found_available = False
        while (logic_id < self.logic_count):
            if (self.logic_list[logic_id].current_time < time_dest):
                if (found_available == False):
                    found_available = True
                    nearest_logic = logic_id
                if (self.logic_list[logic_id].current_time > self.logic_list[nearest_logic].current_time):
                    nearest_logic = logic_id
            logic_id += 1
        if (found_available):
            self.current_logic = nearest_logic
            action_id = self.logic_list[self.current_logic].last_action_id + 1
            # Assume there exists an ending action
            while (self.action_list[action_id]['time'] < time_dest):
                self.logic_list[self.current_logic].last_action_id = action_id
                setInstruction(self.logic_list[action_id])
                action_id += 1
            run_logic()
        else:
            new_logic(time_dest)
            run_logic()
'''
