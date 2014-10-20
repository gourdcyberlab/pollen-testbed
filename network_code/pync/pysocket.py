########################################
# I don't think this is going to work...
########################################
from __future__ import print_function

from socket import socket

__buflen = 65536

class pysocket(socket):
    class __unique_value:
        pass

    def recv(self, count=__unique_value):
        print('[+] value passed:', count)
        if count != __unique_value:
            return super(pysocket, self).recv(count)
        data = []
        while True:
            buf = super(pysocket, self).recv(__buflen)
            data += buf
            if len(buf) != __buflen:
                return data
