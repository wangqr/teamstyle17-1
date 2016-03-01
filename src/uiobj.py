#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import socket
import threading


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
                int(obj['id']), int(object_types.index(obj['type'])), obj['pos'][0], obj['pos'][1], obj['pos'][2], obj['r'])
            ret_strs.append(obj_str)
        ret_str += ';'.join(ret_strs) + ';\n'

    return ret_str  # ret_str 的末尾有一个 \n


class SocketThread(threading.Thread):
    def __init__(self, sock, queue_function, bufsize = 4096):
        threading.Thread.__init__(self)
        self.socket = sock
        self.clientsocket = None
        self.clientaddress = None
        self.queue_function = queue_function
        self.bufsize = bufsize
        self.end = False

    def run(self):
        while not self.end:
            try:
                self.clientsocket, self.clientaddress = self.socket.accept()
            except OSError:
                continue
            if __debug__:
                print('[INFO] platform (UI) Established connection from ' + str(self.clientaddress))
            while not self.end:
                try:
                    data = self.clientsocket.recv(self.bufsize).decode()
                except UnicodeDecodeError as e:
                    print('[ERROR] \x1b[1;31mplatform (UI) exception ' + type(e).__name__ + ' [' + str(e) + ']\x1b[m')
                    ret = '{"message": "platform (UI) exception ' + type(e).__name__ + ' [' + str(e) + '"]}'
                    data = None
                if data == '':
                    self.clientsocket.close()
                    if __debug__:
                        print('[INFO] platform (UI) Connection reset by peer.')
                    break
                lines = data.split('\n')
                for data in lines:  # 这样处理可以吗?
                    if data is not None:
                        ret_json = self.queue_function(data)
                        action_name = json.loads(data)['action']
                        ret = load_msg_from_logic(ret_json, action_name)  # 使用和选手接口同样的处理方式 by mxj
                    if ret is not None:
                        self.clientsocket.send(ret.encode())


class UIObject:
    def __init__(self, queue_function, host = 'localhost', port = 6000, backlog = 1, ai_id = -1):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(backlog)
        self.socket_thread = SocketThread(self.socket, queue_function)
        self.socket_thread.start()

    def exit(self):
        self.socket_thread.end = True
        self.socket.close()
        self.socket_thread.join()
