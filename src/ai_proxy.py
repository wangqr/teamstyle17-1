#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
from threading import Thread, current_thread, Lock
from multiprocessing import Process


def update_info(enqueue, ai_id):
    # Get sth from logic (send and get json strings?)
    py_info = None

    # Convert info from Python string to C string
    c_info = ctypes.create_string_buffer(b"UpdateInfo (send by Python)")  # test
    print(c_info.value)

    return c_info  # C string


def get_action_from_cpp(enqueue, ai_id, c_action):
    # c_action is a bytes string
    # TODO: THREAD LOCK (important!)

    assert isinstance(c_action, bytes)
    ai_id = int(current_thread().name[-1])
    print('Received a massage from ai %d (%s) :' % (ai_id, current_thread().name), c_action)  # test

    # c_action --> act
    act = None

    # Send action to platform main thread
    enqueue(act)


class AICore(object):
    def __init__(self, ai_id, path):
        assert path.endswith(('.dll', '.so'))  # AI file should be a DLL or a Unix shared library
        self.id = ai_id
        self.path = path
        self.dll_main = self.load_dll_main()

    def load_dll_main(self):
        # Load DLL main function
        dll = ctypes.cdll.LoadLibrary(self.path)
        dll_main = dll.StartAI  # StartAi is the main function in dll (a C function)
        return dll_main

    def start_ai(self, enqueue):
        def get_action(c_action):
            # This function will be convert into a C function pointer and pass to dll_main
            get_action_from_cpp(enqueue, self.id, c_action)

        c_get_action = ctypes.CFUNCTYPE(None, ctypes.c_char_p)(get_action)

        def update():
            # Also pass to dll_main
            info = update_info(enqueue, self.id)
            return ctypes.addressof(info)

        c_update = ctypes.CFUNCTYPE(ctypes.c_char_p)(update)  # return a c char pointer (C string)

        # Start AI
        self.dll_main(c_get_action, c_update, self.id)


class AIThread(object):  # The name of this class is Thread but it may be a Process
    def __init__(self, core, method='thread'):
        assert isinstance(core, AICore)
        self.core = core
        self.method = Process if method == 'process' else Thread

    def start(self, enqueue):
        # Start AI thread

        ai_thread = self.method(target=self.core.start_ai, args=(enqueue,), name='ai%d' % self.core.id)

        try:
            ai_thread.start()
        except Exception as error:  # TODO: Deal with runtime errors
            raise error


def start(ai_paths, enqueue, method='thread'):
    """
    Interface Function for platform main thread

    Args:
    ai_paths : a list, paths of ai files (maybe .dll files)
    enqueue : a function defined by main thread, be used to send message
    method : either 'thread' (default) or 'process', choose to start each ai whether in a subthread or a subprocess
    """

    assert isinstance(ai_paths, list)

    method = 'thread'

    # Create AI threads
    ai_threads = []
    for ai_id, path in enumerate(ai_paths):
        ai_core = AICore(ai_id, path)
        ai_threads.append(AIThread(ai_core, method))

    # Start AI Threads
    for ai in ai_threads:
        ai.start(enqueue)
