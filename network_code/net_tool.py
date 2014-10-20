#!/usr/bin/python
from __future__ import print_function
from optparse import OptionParser
import os
import sys
import socket
import select

# found this on the internet. really wishing it came with comments. works
# rather much like netcat does, so we're on the right track.

# this was written by a C guy.
# buffers correctly now, and uses select correctly.

class NetTool:
    def run(self):
        self.stdin = os.fdopen(sys.stdin.fileno(), 'r', 1)
        self.parse_options()
        self.connect_socket()
        self.forward_data()

    def parse_options(self): # {{{
        parser = OptionParser(usage="usage: %prog [options]")

        parser.add_option("-c", "--connect",
            action="store_true",
            dest="connect",
            help="Connect to a remote host")

        parser.add_option("-l", "--listen",
            action="store_false",
            dest="connect",
            help="Listen for a remote host to connect to self host")

        parser.add_option("-r",
            "--remote-host",
            action="store",
            type="string",
            dest="hostname",
            help="Specify the host to connect to")

        parser.add_option("-p",
            "--port",
            action="store",
            type="int",
            dest="port",
            help="Specify the TCP port")

        parser.set_defaults(connect=None, hostname=None)
        (options, args) = parser.parse_args();

        if (options.connect == None):
            sys.stdout.write("no connection type specified\n")
            parser.print_help()
            sys.exit()

        if(options.port == None):
            sys.stdout.write("no port specified\n")
            parser.print_help()
            sys.exit()

        if(options.connect and (options.hostname == None)):
            sys.stdout.write("connect type requires a hostname\n")
            parser.print_help()
            sys.exit()

        self.connect = options.connect
        self.hostname = options.hostname
        self.port = options.port
        # }}}

    def connect_socket(self): # {{{
        if(self.connect):
            # initiate connection to remote host
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, self.port))
        else:
            # listen and wait for a connection
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', self.port))
            server.listen(1)
            self.socket, address = server.accept()
        # }}}

    def forward_data(self): # {{{
        self.socket.setblocking(0)
        while True:
            # {{{
            # read_ready, write_ready, in_error = select.select([self.socket, sys.stdin], [], [self.socket, sys.stdin])
            # try:
            #     buf = self.socket.recv(100)
            #     while(buf != ''):
            #         sys.stdout.write(buffer)
            #         sys.stdout.flush()
            #         buf = self.socket.recv(100)
            #     if(buf == ''):
            #         return
            # except socket.error as e:
            #     sys.stderr.write('[-] Error: {}\n'.format(e))
            #     pass
            # while(True):
            #     r, w, e = select.select([sys.stdin],[],[],0)
            #     if(len(r) == 0):
            #         break;
            #     c = sys.stdin.read(1)
            #     if(c == ''):
            #         return
            #     if(self.socket.sendall(c) != None):
            #         return
            # }}}

            read_ready, write_ready, in_error = select.select(
                    [self.socket, self.stdin], [], [self.socket, self.stdin])
            if read_ready[0] == self.socket:
                buf = self.socket.recv(256)
                if(buf == ''):
                    return
                sys.stdout.write(buf)
                sys.stdout.flush()
            elif read_ready[0] == self.stdin:
                buf = self.stdin.readline()
                if(buf == ''):
                    return
                self.socket.sendall(buf)
        # }}}

if __name__ == '__main__':
    tool = NetTool()
    tool.run()

# vim: fdm=marker et sts=4
