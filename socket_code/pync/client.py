from test import connect
from socket import socket, gethostname

def makeclient():
    s = socket()
    s.connect((gethostname(), 12345))
    return s

if __name__ == '__main__':
    s = makeclient()
    connect(s)
