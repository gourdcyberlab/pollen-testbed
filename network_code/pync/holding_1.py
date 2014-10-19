#!/usr/bin/env python

from __future__ import print_function
import socket
import threading
from time import sleep

buflen = 1024

def listen(s):
    print('starting listen')
    while True:
        data = s.recv(buflen)
        if data == '':
            break
        print(data)
    s.close()
    print('listen ending')

def talk(s):
    print('starting talk')
    while True:
        try:
            line = raw_input()
        except (EOFError, KeyboardInterrupt):
            break
        s.send(line)
    s.close()
    print('talk ending')

def connect(s):
    print('starting connect')
    s_li = s.dup()
    s_ta = s.dup()

    li = threading.Thread(target=listen, args=[s_li])
    ta = threading.Thread(target=talk, args=[s_ta])

    li.start()
    ta.start()

    li.join()
    ta.join()

    s.close()
    print('connect ending')
