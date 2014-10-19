#!/usr/bin/env python

from __future__ import print_function
from scapy.all import *

from varint import *

# The new field, for holding varints
class VarIntField(Field):
    # XXX: right now using naive `chr` and `ord` instead of struct methods

    def __init__(self, name, default):
        Field.__init__(self, name, default, fmt='B')
    def i2len(self, pkt, x):
        m = self._tostr(x)
        return len(m)
    def any2i(self, pkt, x):
        if isinstance(x, str):
            return varint_num(x)
        return x
    def addfield(self, pkt, s, val):
        if val is None:
            return s+'\x00'
        return s + varint_str(val)
    def getfield(self, pkt, m):
        if m in (None, ''):
            return 0, ''
        return varint_with_remainder(m)
    def randval(self):
        return RandVarInt()

class RandVarInt(RandBin):
    '''Generate random numbers between 0 and ~1e30, appropriate for testing
    values of varints.'''

    # what we're doing here is making a random bytestring, then setting the
    # first bit in each byte such that the binstring becomes a valid varint.
    #   -> 1 1 1 ... 1 0
    # then at the end we convert to integer value. the reason for this is
    # so that we get a good distribution of values. the random number
    # generators would only give us 12 significant digits of random, but we
    # were generating numbers up to 30 digits long, meaning we ended up with
    # some-random-number * 10**15. so we sidestepped the problem and got the
    # distribution we wanted to begin with, at the expense of a little more
    # computation.

    def __init__(self):
        RandBin.__init__(self, RandNumExpo(0.5, 1))

    def _fix(self):
        '''go look at how volatile values work'''
        f = RandBin._fix(self)
        f = [ord(x) | 0x80 for x in f]
        f[-1] &= 0x7f
        f = str.join('',(chr(x) for x in f))
        return varint_num(f)

class RandList(RandField):
    '''A list of random size and/or random items. By default, size is
    `RandNumExpo(0.1)`, and item is `RandChoice(RandString(), RandInt())`.'''
    def __init__(self,
                 size=RandNumExpo(0.1),
                 item=RandChoice(RandString(), RandInt()) ):
        self.size = size
        self.item = item
    def _fix(self):
        '''go look at how volatile values work'''
        return [self.item] * self.size

# adding a function for random values in a field list
def _randval(self):
    '''Return a list of a random number of our field'''
    # made specifically to be added to FieldListField
    return RandList(item=self.field.randval())
FieldListField.randval = _randval

def compare_digest(a, b):
    '''For comparing hash digests in constant time, avoiding timing attacks.'''
    # for use when hmac.compare_digest is not available (Python < 2.7.7)
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0

class Pollen(Packet):
    name = 'Pollen'
    # 32 bytes reserved for HMAC, 2 bytes for number-of-hosts, and a variable
    # number of bytes each for a variable number of hosts
    fields_desc = [ StrFixedLenField('hash', None, 32),
                    FieldLenField('length', None, fmt='H', count_of='hosts'),
                    FieldListField('hosts', None, VarIntField('', 0))
                  ]
    def post_build(self, pkt, pay):
        # TODO
        return Packet.post_build(self, pkt, pay)
