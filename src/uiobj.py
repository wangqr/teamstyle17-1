#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import main
import action
import queue
import socket
import json
import threading


class RecvThread(threading.Thread):
    def __init__(self, sock, signal_queue, queue_function, bufsize=4096):
        threading.Thread.__init__(self)
        self.socket = sock
        self.queue_function = queue_function
        self.bufsize = bufsize
        self._send_signal_queue = signal_queue
        self.sig = queue.Queue()

    def run(self):
        buf = ''
        while 1:
            try:
                data = self.socket.recv(self.bufsize).decode()
            except UnicodeDecodeError as e:
                main.root_logger.error('platform (UI) exception %s [%s]', type(e).__name__, str(e))
                continue
            except OSError:
                break
            if data == '':
                break
            if data is not None:
                buf += data
                b = buf.find('{')
                if b < 0:
                    buf = ''
                else:
                    buf = buf[b:]
                e = buf.find('}')
                while e >= 0:
                    self.queue_function(buf[:e + 1])
                    b = buf.find('{', e + 1)
                    if b < 0:
                        buf = ''
                    else:
                        buf = buf[b:]
                    e = buf.find('}')
        self._send_signal_queue.put(1)


class SendThread(threading.Thread):
    def __init__(self, sock, signal_queue):
        threading.Thread.__init__(self)
        self.socket = sock
        self._send_signal_queue = signal_queue
        self.sig = queue.Queue()

    def run(self):
        while 1:
            q = self.sig.get(block=True)
            if q == 0:
                break
            else:

                # 强行预处理
                data_type = ''
                try:
                    j = json.loads(q)
                    if type(j) == dict:
                        if j.get('players') is not None:
                            data_type = 'query_status'
                        elif j.get('objects') is not None:
                            data_type = 'query_map'
                except ValueError:
                    pass
                if data_type != '':
                    q = load_msg_from_logic(q, data_type)
                if not q.endswith('\n'):
                    q += '\n'

                try:
                    self.socket.send(q.encode())
                except BrokenPipeError:
                    break
                except OSError:
                    break
        self._send_signal_queue.put(1)


def load_msg_from_logic(msg: str, action_name: str) -> str:  # 从 ai_proxy 移植过来
    skill_types = ['longAttack', 'shortAttack', 'shield', 'teleport', 'visionUp', 'healthUp']
    object_types = ['player', 'food', 'nutrient', 'spike', 'target', 'bullet']

    info = json.loads(msg)
    ret_str = ''

    if action_name == 'query_status':
        ret_strs = []
        for player in info['players']:
            skill_levels = dict().fromkeys(skill_types, 0)
            for skill in player['skills']:
                skill_levels[skill['name']] = skill['level']
            palyer_values = [player['id'], player['health'], player['max_health'], player['vision'], player['ability']]
            palyer_values.extend([skill_levels[skill] for skill in skill_types])
            ret_strs.append(' '.join([str(int(x)) for x in palyer_values]))
        ret_str = ';'.join(ret_strs) + ';\n'

    elif action_name == 'query_map':
        ret_str = '%d|' % info['time']
        ret_strs = []
        for obj in info['objects']:
            assert obj['type'] in object_types
            # ret_values.append([int(obj['id']), int(object_types.index(obj['type']))] + obj['pos']] + [obj['r']])
            obj_str = '%d %d %.30f %.30f %.30f %.30f' % (
                int(obj['id']), int(object_types.index(obj['type'])), obj['pos'][0], obj['pos'][1], obj['pos'][2],
                obj['r'])
            ret_strs.append(obj_str)
        ret_str += ';'.join(ret_strs) + ';\n'

    return ret_str  # ret_str 的末尾有一个 \n


class UIObject(threading.Thread):
    def __init__(self, game, host='localhost', port=6000, backlog=1, ai_id=-1):
        threading.Thread.__init__(self)
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(backlog)
        self.sig = queue.Queue()
        self.recv_thread = None
        self.send_thread = None
        self.ui_socket = None

        self._game_obj = game
        self._ai_id = ai_id

    def exit(self):
        self.socket.close()
        self.sig.put(0)
        self.__exit_child_threads()

    def __exit_child_threads(self):
        if self.ui_socket:
            self.ui_socket.close()
        if self.recv_thread and self.recv_thread.is_alive():
            self.recv_thread.sig.put(0)
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.sig.put(0)
        if self.recv_thread:
            self.recv_thread.join()
        if self.send_thread:
            self.send_thread.join()

    def push_queue_ui(self, obj: str):
        json_obj = json.loads(obj)
        act = json_obj.get('action')
        timestamp = json_obj.get('time') or self._game_obj.current_time
        if act and act[0] == '_':
            self._game_obj.enqueue(0., action.Action('{"action":"_platform","ai_id":%d}' % self._ai_id, act, None))
        else:
            self._game_obj.enqueue(timestamp, action.Action(obj, 'query', self.send_thread.sig))

    def enqueue(self, data: str):
        assert type(data) == str
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.sig.put(data)

    def run(self):
        self.sig.put(2)
        while 1:
            q = self.sig.get(block=True)
            if q == 0:
                break
            if q == 1:
                main.root_logger.info('platform (UI) Connection reset by peer.')
                self.__exit_child_threads()
            try:
                self.ui_socket, address = self.socket.accept()
                main.root_logger.info('platform (UI) Connection accepted from %s', repr(address))
                self.sig = queue.Queue()
                self.recv_thread = RecvThread(self.ui_socket, self.sig, self.push_queue_ui)
                self.recv_thread.start()
                self.send_thread = SendThread(self.ui_socket, self.sig)
                self.send_thread.start()
            except OSError:
                break
