#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
import action
from threading import Thread, current_thread
from multiprocessing import Process

def communicate_with_dll(dll_message, enqueue_func, ai_id):
    assert isinstance(dll_message, bytes)

    msg_send = str(dll_message)[2:-1]

    msg_send.replace('$ID', str(ai_id))

    # send msg_send to logic
    msg_receive = '********' # 一个很奇怪的问题：用 C++ 读取 Python 传过来的长字符串的时候前 8 个字符会随机（目测）变成别的字符，所以用 * 替换掉...

    if msg_send.startswith('ACT'):  # 只发送不接收
        enqueue_func(msg_send[4:])

    if msg_send.startswith('QRY'):  # 发送 and 接收
        msg_receive += enqueue_func(msg_send[4:])

    return ctypes.addressof(ctypes.create_string_buffer(bytes(msg_receive, encoding='ascii')))



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

    def start_ai(self, enqueue_func):

        def communicate(dll_message):
            # Also pass to dll_main
            assert isinstance(dll_message, bytes)
            return communicate_with_dll(dll_message, enqueue_func, self.id)

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
