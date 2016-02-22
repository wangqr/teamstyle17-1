#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
from threading import Thread, current_thread
from multiprocessing import Process

max_message_length = 10000


def set_string_value(buffer, string):
    for i, char in enumerate(string):
        buffer[i] = ord(char)
    buffer[len(string)] = 0


def communicate_with_dll(dll_message, enqueue_func, ai_id, string_buffer):
    assert isinstance(dll_message, bytes)

    action_name, *msg = str(dll_message)[2:-1].split(sep=' ')
    msg_from_logic = ''
    skill_types = ['longAttack', 'shortAttack', 'shield', 'teleport', 'visionUp', 'healthUp']

    if action_name in ['query_map', 'query_status']:
        msg_send = r'{"action": "%s","time": 0,"ai_id": %d}' % (action_name, ai_id)
        msg_from_logic += enqueue_func(msg_send)

    elif action_name == 'move':
        msg_send = r'{"action": "move","time": 0,"ai_id": %d,"x": %d,"y": %d,"z": %d}' % (
            ai_id, int(msg[0]), int(msg[1]), int(msg[2]))
        enqueue_func(msg_send)

    elif action_name == 'use_skill' and 0 <= int(msg[0]) < len(skill_types):  # 技能在技能列表中
        msg_send = r'{"action": "use_skill","time": 0,"ai_id": %d,"skill_type": "%s","x": %d,"y": %d,"z": %d,"target": %d}' \
                   % (ai_id, skill_types[int(msg[0])], int(msg[1]), int(msg[2]), int(msg[3]), -1)  # target 是有用的吗？
        enqueue_func(msg_send)

    elif action_name == 'upgrade_skill' and 0 <= int(msg[0]) < len(skill_types):
        msg_send = r'{"action": "upgrade_skill","time": 0,"ai_id": %d,"skill_type": "%s"}' % (ai_id, skill_types[int(msg[0])])
        enqueue_func(msg_send)

    elif action_name == 'pause':
        pass

    set_string_value(string_buffer, msg_from_logic)
    return ctypes.addressof(string_buffer)


class AICore(object):
    def __init__(self, ai_id, path):
        assert path.endswith(('.dll', '.so'))
        self.id = ai_id
        self.path = path
        self.dll_main = self.load_dll_main()
        self.c_string_buffer = ctypes.create_string_buffer(max_message_length)

    def load_dll_main(self):
        # Load DLL main function
        dll = ctypes.cdll.LoadLibrary(self.path)
        dll_main = dll.StartAI  # StartAi is the main function in dll (a C function)
        return dll_main

    def start_ai(self, enqueue_func):
        def communicate(dll_message):
            # Also pass to dll_main
            assert isinstance(dll_message, bytes)
            return communicate_with_dll(dll_message, enqueue_func, self.id, self.c_string_buffer)

        c_communicate = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_char_p)(communicate)

        # Start AI
        self.dll_main(c_communicate, self.id)


class AIThread(object):
    def __init__(self, core, enqueue_func, method='thread'):
        assert isinstance(core, AICore)
        self.core = core
        self.method = Process if method == 'process' else Thread
        self.ai_thread = None

    def create_thread(self, enqueue_func):
        self.ai_thread = self.method(target=self.core.start_ai, args=(enqueue_func,), name='ai%d' % self.core.id)

    def start(self):
        # Start AI thread
        try:
            self.ai_thread.start()
        except Exception as error:  # TODO: Deal with runtime errors
            raise error


def start(ai_paths, enqueue_func):
    """
    Interface Function for platform main thread

    Args:
    ai_paths : a list, paths of ai files (maybe .dll files)
    enqueue_func : a function defined by main thread, be used to send message
    """

    assert isinstance(ai_paths, list)

    method = 'thread'

    # Create AI threads
    ai_threads = []
    for ai_id, path in enumerate(ai_paths):
        ai_threads.append(AIThread(AICore(ai_id, path), method))
        ai_threads[ai_id].create_thread(enqueue_func)

    # Start AI Threads
    for ai in ai_threads:
        ai.start()
