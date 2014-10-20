from test import connect
from socket import socket, gethostname

def makeserver():
    s = socket()
    s.bind((gethostname(), 12345))
    s.listen(5)
    while True:
        yield s.accept()

if __name__ == '__main__':
    for c, a in makeserver():
        connect(c)
