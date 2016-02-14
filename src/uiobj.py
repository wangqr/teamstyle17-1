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
        print ('SocketThread init OK.')

    def run(self):
        self.clientsocket, self.clientaddress = self.socket.accept()
        print('Established connection from ' + str(self.clientaddress))
        while 1: # TODO while not game.stopped:
            data = self.clientsocket.recv(self.bufsize).decode()
            ret = self.queue_function(data)
            if ret is not None:
                clientsocket.send(ret.encode())

class UIObject:
    def __init__(self, queue_function, host = 'localhost', port = 6000, backlog = 1, ai_id = -1):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(backlog)
        self.socket_thread = SocketThread(self.socket, queue_function)
        self.socket_thread.start()
