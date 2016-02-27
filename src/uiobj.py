#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading


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
                if data is not None:
                    ret = self.queue_function(data)
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
