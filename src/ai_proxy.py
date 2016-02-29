#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI Proxy

import ctypes
import json
from threading import Thread
from multiprocessing import Process

max_message_length = 10000


def set_string_value(buffer, string):
    assert len(string) + 1 < max_message_length
    for i, char in enumerate(string):
        buffer[i] = ord(char)
    buffer[len(string)] = 0


def load_msg_from_logic(msg, action_name, ai_id, skill_types=None, object_types=None):
    info = json.loads(msg)
    ret_str = ''

    if action_name == 'query_status':
        skill_levels = dict().fromkeys(skill_types, 0)
        for player in info['players']:
            if player['id'] == ai_id:
                for skill in player['skills']:
                    skill_levels[skill['name']] = skill['level']
                ret_values = [player['id'], player['health'], player['vision'], player['ability']]
                ret_values.extend([skill_levels[skill] for skill in skill_types])
                assert len(ret_values) == 10  # id, health, vision, ability, 6 个技能的等级
                ret_str = ' '.join([str(int(x)) for x in ret_values])
                break
        assert ret_str != ''

    elif action_name == 'query_map':
        assert info['ai_id'] == ai_id
        ret_str = '%d|' % info['time']
        ret_values = []
        for obj in info['objects']:
            assert obj['type'] in object_types
            # ret_values.append([int(obj['id']), int(object_types.index(obj['type']))] + obj['pos']] + [obj['r']])
            obj_str = '%d %d %.30f %.30f %.30f %.30f' % (int(obj['id']), int(object_types.index(obj['type'])), obj['pos'][0],obj['pos'][1],obj['pos'][2] , obj['r'])
            ret_values.append(obj_str)
        ret_str += ';'.join(ret_values) + ';\n'

    return ret_str


def communicate_with_dll(dll_message, enqueue_func, ai_id, string_buffer):
    assert isinstance(dll_message, bytes)

    action_name, *msg = str(dll_message)[2:-1].split(sep=' ')
    skill_types = ['longAttack', 'shortAttack', 'shield', 'teleport', 'visionUp', 'healthUp']
    object_types = ['player', 'food', 'nutrient', 'spike', 'target', 'bullet']

    ret = ''

    if action_name in ['query_map', 'query_status']:
        info_send = dict(action=action_name, time=0, ai_id=ai_id)
        info_send['id'] = int(msg[0]) if action_name == 'query_status' and int(msg[0]) != -1 else ai_id
        msg_send = json.dumps(info_send)
        msg_from_logic = enqueue_func(msg_send)
        ret = load_msg_from_logic(msg_from_logic, action_name, ai_id, skill_types, object_types)

    elif action_name == 'move':
        info_send = dict(action='move', time=0, ai_id=ai_id, id=int(msg[0]), x=float(msg[1]), y=float(msg[2]), z=float(msg[3]))
        info_send['id'] = int(msg[0]) if int(msg[0]) != -1 else ai_id  # For Debug
        msg_send = json.dumps(info_send)
        enqueue_func(msg_send)

    elif action_name == 'use_skill' and int(msg[0]) in range(4):  # 技能在技能列表中
        info_send = dict(action='use_skill', time=0, ai_id=ai_id, skill_type=skill_types[int(msg[0])],
                         id=int(msg[1]), target=int(msg[2]), x=float(msg[3]), y=float(msg[4]), z=float(msg[5]))
        info_send['id'] = int(msg[1]) if int(msg[1]) != -1 else ai_id  # For Debug
        msg_send = json.dumps(info_send)
        enqueue_func(msg_send)

    elif action_name == 'upgrade_skill' and int(msg[0]) in range(6):
        info_send = dict(action='upgrade_skill', time=0, skill_type=skill_types[int(msg[0])], ai_id=ai_id, id=int(msg[1]))
        info_send['id'] = int(msg[1]) if int(msg[1]) != -1 else ai_id  # For Debug
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

    set_string_value(string_buffer, ret)
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
