#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
import main
import json
from threading import Thread

max_message_length = 1000000


def set_string_value(buffer, string):
    assert len(string) + 1 < max_message_length
    for i, char in enumerate(string):
        buffer[i] = ord(char)
    buffer[len(string)] = 0


def load_msg_from_logic(msg, action_name, ai_id, skill_types=None, object_types=None):
    info = json.loads(msg)
    ret_str = ''
    ret_str_list = []

    # print('[INFO] %s called by ai %d' % (action_name, ai_id))
    # print('[INFO] msg from logic [%s]' % msg)

    try:
        if action_name == 'query_status':
            ret_str_list.append('%d|' % ai_id)
            for player in info['players']:
                if player['ai_id'] != ai_id:
                    continue
                skill_levels = [0] * 6
                skill_cds = [-1] * 6
                for skill in player['skills']:
                    index = skill_types.index(skill['name'])
                    skill_levels[index] = skill['level']
                    skill_cds[index] = skill['cd']
                s = '%d %d %d %d %d %.10f %.10f %.10f %.10f %.10f %.10f %.10f %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d;' % (
                    player['id'], player['health'], player['max_health'], player['vision'], player['ability'], player['r'],
                    player['pos'][0], player['pos'][1], player['pos'][2], player['speed'][0], player['speed'][1], player['speed'][2],
                    skill_levels[0], skill_levels[1], skill_levels[2], skill_levels[3], skill_levels[4], skill_levels[5],
                    skill_cds[0], skill_cds[1], skill_cds[2], skill_cds[3], skill_cds[4], skill_cds[5],
                    player['longattackcasting'], player['shieldtime'], player['dashtime'])
                ret_str_list.append(s)
            ret_str = ' '.join(ret_str_list)

        elif action_name == 'query_map':
            ret_str_list.append('%d|' % info['time'])
            for obj in info['objects']:
                s = '%d %d %d %.10f %.10f %.10f %.10f %d %d;' % (
                    int(obj['id']), int(obj['ai_id']), int(object_types.index(obj['type'])),
                    obj['pos'][0], obj['pos'][1], obj['pos'][2], obj['r'], obj['longattackcasting'], obj['shieldtime'])
                ret_str_list.append(s)
            ret_str = ' '.join(ret_str_list)

    except KeyError as err:
        main.root_logger.error('ai_proxy exception %s [%s]' % (type(err).__name__, str(err)))

    # print("[INFO] ret for dll [%s]" % ret_str)
    return ret_str


def communicate_with_dll(dll_message, enqueue_func, ai_id, string_buffer):
    assert isinstance(dll_message, bytes)

    action_name, *msg = str(dll_message)[2:-1].split(sep=' ')
    skill_types = ['longAttack', 'shortAttack', 'shield', 'dash', 'visionUp', 'healthUp']
    object_types = ['player', 'food', 'nutrient', 'spike', 'target', 'bullet', 'source']

    ret = ''

    try:
        if action_name in ['query_map', 'query_status']:
            info_send = dict(action=action_name, time=0, ai_id=ai_id)
            info_send['id'] = int(msg[0]) if action_name == 'query_status' and int(msg[0]) != -1 else ai_id + 1
            msg_send = json.dumps(info_send)
            msg_from_logic = enqueue_func(msg_send)
            ret = load_msg_from_logic(msg_from_logic, action_name, ai_id, skill_types, object_types)

        elif action_name == 'move':
            info_send = dict(action='move', time=0, ai_id=ai_id, id=int(msg[0]), x=float(msg[1]), y=float(msg[2]), z=float(msg[3]))
            info_send['id'] = int(msg[0]) if int(msg[0]) != -1 else ai_id + 1  # For Debug
            msg_send = json.dumps(info_send)
            enqueue_func(msg_send)

        elif action_name == 'use_skill' and int(msg[0]) in range(4):  # 技能在技能列表中
            info_send = dict(action='use_skill', time=0, ai_id=ai_id, skill_type=skill_types[int(msg[0])],
                             id=int(msg[1]), target=int(msg[2]), x=float(msg[3]), y=float(msg[4]), z=float(msg[5]))
            info_send['id'] = int(msg[1]) if int(msg[1]) != -1 else ai_id + 1  # For Debug
            msg_send = json.dumps(info_send)
            enqueue_func(msg_send)

        elif action_name == 'upgrade_skill' and int(msg[0]) in range(6):
            info_send = dict(action='upgrade_skill', time=0, skill_type=skill_types[int(msg[0])], ai_id=ai_id, id=int(msg[1]))
            info_send['id'] = int(msg[1]) if int(msg[1]) != -1 else ai_id + 1  # For Debug
            msg_send = json.dumps(info_send)
            enqueue_func(msg_send)

        elif action_name == 'pause':
            msg_send = r'{"action": "_pause","ai_id": %d}' % ai_id
            enqueue_func(msg_send)

        elif action_name == 'query_time':
            msg_send = r'{"action": "query_time","ai_id": %d}' % ai_id
            msg_received = enqueue_func(msg_send)
            current_time = json.loads(msg_received)['time']  # 返回的字段中应该有 'time'
            ret = str(int(current_time))
    except Exception as err:
        main.root_logger.error('[ERROR] ai%d exception %s [%s]' % (ai_id, err.__name__, str(err)))
        ret = ''

    set_string_value(string_buffer, ret)
    return ctypes.addressof(string_buffer)


class AICore(object):
    def __init__(self, ai_id, path):
        self.id = ai_id
        self.path = path
        self.dll_main = self.load_dll_main()
        self.c_string_buffer = ctypes.create_string_buffer(max_message_length)
        self._c_communicate = None

    def load_dll_main(self):
        # Load DLL main function
        try:
            dll = ctypes.cdll.LoadLibrary(self.path)
        except OSError:
            main.root_logger.warn('It seems that AI "%s" is not built for current architecture.', self.path)
            return lambda *x: None
        dll_main = dll.StartAI  # StartAi is the main function in dll (a C function)
        return dll_main

    def start_ai(self, enqueue_func):
        def communicate(dll_message):
            # Also pass to dll_main
            assert isinstance(dll_message, bytes)
            return communicate_with_dll(dll_message, enqueue_func, self.id, self.c_string_buffer)

        self._c_communicate = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_char_p)(communicate)

        # Start AI
        while 1:
            try:
                self.dll_main(self._c_communicate, self.id)
            except Exception as err:
                main.root_logger.error('[ERROR] ai%d exception %s [%s]' % (self.id, err.__name__, str(err)))


class AIThread(object):
    def __init__(self, core):
        assert isinstance(core, AICore)
        self.core = core
        self.ai_thread = None

    def create_thread(self, enqueue_func):
        self.ai_thread = Thread(target=self.core.start_ai, args=(enqueue_func,), name='ai%d' % self.core.id, daemon=True)

    def start(self):
        # Start AI thread
        self.ai_thread.start()


def start(ai_paths, enqueue_func):
    """
    Interface Function for platform main thread

    Args:
    ai_paths : a list, paths of ai files (maybe .dll files)
    enqueue_func : a function defined by main thread, be used to send message
    """

    assert isinstance(ai_paths, list)

    # Create AI threads
    ai_threads = []
    for ai_id, path in enumerate(ai_paths):
        ai_threads.append(AIThread(AICore(ai_id, path)))
        ai_threads[ai_id].create_thread(enqueue_func)

    # Start AI Threads
    for ai in ai_threads:
        ai.start()
