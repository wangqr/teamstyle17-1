#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
from threading import Thread
from multiprocessing import Process


class Action(object):
    # TODO
    def __init__(self):
        pass

    def run(self):
        pass


class CAction(ctypes.Structure):
    # TODO
    _fields_ = [('foo', ctypes.c_int)]


class CGameInfo(ctypes.Structure):
    # TODO: Game info
    _fields_ = [('bar', ctypes.c_int)]


def update_info(enqueue, ai_id):
    # TODO: Get sth from logic
    info = None

    # TODO: Convert info from Python type to C type
    c_info = CGameInfo()

    return c_info  # C structure


def get_action_from_cpp(enqueue, ai_id, c_act):  # c_act is a C structure
    # TODO: Use c_act to create an action
    act = Action()

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
        def get_action(c_act):
            # This function will be convert into a C function pointer and pass to dll_main
            get_action_from_cpp(enqueue, self.id, c_act)

        c_get_action = ctypes.CFUNCTYPE(None, ctypes.POINTER(CAction))(get_action)

        def update():
            # Also pass to dll_main
            info = update_info(enqueue, self.id)
            return ctypes.addressof(info)

        c_update = ctypes.CFUNCTYPE(ctypes.c_void_p)(update)  # return a C structure pointer to ai (a void*, infect)

        # Start AI
        self.dll_main(c_get_action, c_update)


class AIThread(object):  # The name of this class is Thread but it may be a Process
    def __init__(self, core, method='thread'):
        assert isinstance(core, AICore)
        self.core = core
        self.method = Process if method == 'process' else Thread  # How to start an AI

    def start(self, enqueue):
        # Start AI thread
        ai_thread = self.method(target=self.core.start_ai, args=(enqueue,))

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

    if method not in ('thread', 'process'):
        method = 'thread'

    # Create AI threads
    ai_threads = []
    for ai_id, path in enumerate(ai_paths):
        ai_core = AICore(ai_id, path)
        ai_threads.append(AIThread(ai_core, method))

    # Start AI Threads
    for ai in ai_threads:
        ai.start(enqueue)
