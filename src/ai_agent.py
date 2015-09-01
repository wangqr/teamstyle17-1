# AI Agent

import ctypes
from multiprocessing import Process
from threading import Thread


class AiInfo(object):
    def __init__(self, ai_id, path):
        self.ai_id = ai_id
        self.path = path


class AiCore(AiInfo):
    def __init__(self):
        pass


class AiThread(AiCore):
    def __init__(self):
        self.thread # Initialize ai thread here
        # ...

    def start(self):
        self.thread.start()


def start(ai_paths, enqueue, method='thread'):
    """
    Interface Function for platform main thread

    Args:
    ai_paths : a list, paths of ai files (maybe .dll files)
    enqueue : a function defined by main thread, be used to send message
    method : either 'thread' (default) or 'process', choose to start each ai whether in a subthread or a subprocess
    """

    assert isinstance(ai_paths, list)

    ai_threads = []

    for ai_id, path in enumerate(ai_paths):
        pass

    for ai in ai_threads:
        ai.start()
