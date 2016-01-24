#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import nose
import json

from src import action


class LogicProxy:
    def __init__(self):
        self.queue = []

    def setInstruction(self, action_json):
        try:
            self.queue.append(json.loads(action_json))
        except Exception:
            pass

    def getInstruction(self, action_json):
        try:
            self.queue.append(json.loads(action_json))
        except Exception:
            pass
        return '{}'


class TestAction:
    @staticmethod
    def test_run_basic():
        act = action.Action('{}', 'instruction', None)
        logic = LogicProxy()
        act.run(logic)
        nose.tools.assert_equal(logic.queue, [{}])

    @staticmethod
    def test_run_non_logic():
        act = action.Action('{}', '_platform', None)
        logic = LogicProxy()
        act.run(logic)
        nose.tools.assert_equal(logic.queue, [])

    @staticmethod
    def test_timestamp():
        act = action.Action('{}', '_platform', None)
        act.set_timestamp(123.456)
        nose.tools.assert_equal(json.loads(act.action_json), {'time':123})
