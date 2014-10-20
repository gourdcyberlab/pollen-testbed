#!/usr/bin/env python

import itertools

'''
Functions for converting between strings (formatted as varints) and integers.
'''

class VarintError(ValueError):
    '''Invalid varint string.'''
    def __init__(self, message='', string=None):
        ValueError.__init__(self, message)
        self.string = string

# Can't add methods to `int` or `str`, so we have these functions instead.
def varint_str(x):
    '''Convert a number to its string varint representation.'''
    out = []
    while x != (x & 0x7F):
        n, x = x & 0x7F, x >> 7
        out += [chr(n | 0x80)]
    out += [chr(x)]
    return str.join('', out)

def varint_with_remainder(s):
    '''Convert a string representation of a varint to an integer, with the
    remainder of the string.
    Returns (remainder, num).'''
    try:
        items = list(itertools.takewhile((lambda c: ord(c) & 0x80), s))
        items.append(s[len(items)])
        n = reduce((lambda x, (i, c): x+((ord(c) & 0x7F) << (i*7))), enumerate(items), 0)
        return s[len(items):], n
    except IndexError:
        raise VarintError('Not a valid varint', s)

def varint_num(s):
    '''Convert a string representaion of a varint to an integer.'''
    return varint_with_remainder(s)[1]

def varint_list(s):
    '''Convert a string of varints to integers. Assumes that there is no
    trailing string after final varint'''
    while s:
        s, n = varint_with_remainder(s)
        yield n
