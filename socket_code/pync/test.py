#!/usr/bin/env python

from __future__ import print_function
from socket import socket
from sys import stdin, argv
from select import select

buflen = 1024
default_port = 12345

def handle_stdin(stdin, sock):
    line = stdin.readline()
    if line == '':
        return 'done'
    sock.send(line)

def handle_sock(sock):
    data = ''
    while True:
        buf = sock.recv(buflen)
        if buf == '':
            return 'done'
        data += buf
        if len(buf) != buflen:
            break
    print(data, end='')

def get_server(portno=default_port):
    s = socket()
    s.bind(('', portno))
    s.listen(5)
    return s

def get_client(host='localhost', portno=default_port):
    s = socket()
    s.connect((host, portno))
    return s

def connect(s):
    try:
        # using 'retval' and a string for now, may change to something more
        # robust later, or just to a boolean
        retval = None
        while retval != 'done':
            # see note 1
            item = select([s, stdin], [], [])[0][0]
            if type(item) == socket:
                retval = handle_sock(item)
            elif type(item) == file:
                retval = handle_stdin(item, s)
    finally:
        s.close()

def main():
    if len(argv) < 2:
        print('[-] Not enough arguments')
        return
    if 's' in argv[1]:
        s = get_server()
        c, a = s.accept()
        connect(c)
        s.close()
    elif 'c' in argv[1]:
        s = get_client()
        connect(s)

if __name__ == '__main__':
    main()

# note 1: the 'select' thingy.
# the select function takes 3 lists (so it seems): things we want to read from,
# things we want to write to, and other random stuffy stuffs that tommy doesn't
# know about. We're only interested in reading from stuff, because we can print
# stuff whenever. what it returns is basically it's parameters in a tuple. that
# is, it returns three lists back to you, no matter what. so, for the two index
# references at the end of blahblah()[0][0], we are first grabbing the
# items-for-reading list, and then we are grabbing the first item in that list.
# I believe it is possible for the read-items list to have multiple objects in
# it, but we don't need to worry about items after the first, because a
# successive call to select() will return those items again (b/c they're still
# ready for reading).
