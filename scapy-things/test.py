# checking the correctness of different versions of int2varint and varint2int
# functions. at least, i'm pretty sure that's what this is.

def geta(x):
    out = []
    while True:
        y, x = x & 0x7F, x >> 7
        if x == 0:
            out += [chr(y)]
            break
        else:
            out += [chr(y | 0x80)]
    return str.join('', out)

def getb(x):
    out = []
    while x > 0x7F:
        y, x = x & 0x7F, x >> 7
        out += [chr(y | 0x80)]
    out += [chr(x)]
    return str.join('', out)

def seta(m):
    n = 0
    for i, c in enumerate(m):
        c = ord(c)
        n += (c & 0x7F) << (7 * i)
        if not c & 0x80:
            break
    else:
        raise ValueError('Not a valid varint.')
    return n, m[i+1:]

def setb(m):
    from itertools import takewhile
    items = list(takewhile((lambda c: ord(c) & 0x80), m))
    items.append(m[len(items)])
    n = reduce((lambda x, (i, c): (ord(c) & 0x7F) << (i*7)), enumerate(items), 0)
    return n, m[len(items):]

n = 1000
getarange = [geta(x) for x in range(n)]
getbrange = [getb(x) for x in range(n)]

getworks = (getarange == getbrange)

setarange = [seta(hex(x)) for x in range(n)]
setbrange = [setb(hex(x)) for x in range(n)]

setworks = (setarange == setbrange)
