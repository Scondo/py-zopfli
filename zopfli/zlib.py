from __future__ import absolute_import

import zopfli
import zopfli.zopfli
import zlib

levit = {1: 1,
         2: 3,
         3: 5,
         4: 10,
         5: 15,
         6: 25,
         7: 100,
         8: 500,
         9: 2000
       }
MASTER_BLOCK_SIZE = 20000000


def bytecross(first, second, border):
    mask = 0
    for i in range(0, border):
        mask = mask + pow(2, i)
    first = first & mask
    second = second & ~mask
    return first | second


class compressobj(object):
    def __init__(self, level=None, **kwargs):
        self.crc = None
        self.buf = bytearray('')
        self.bit = 0
        self.first = True
        self.opt = kwargs
        self.lastbyte = ''
        if level != None:
            self.opt['numiterations'] = levit[level]

    def _header(self):
        cmf = 120
        flevel = 0
        fdict = 0
        cmfflg = 256 * cmf + fdict * 32 + flevel * 64
        fcheck = 31 - cmfflg % 31
        cmfflg += fcheck

        out = bytearray()
        out.append(cmfflg / 256)
        out.append(cmfflg % 256)
        return out

    def _tail(self):
        out = bytearray()
        out.append((self.crc >> 24) % 256)
        out.append((self.crc >> 16) % 256)
        out.append((self.crc >> 8) % 256)
        out.append(self.crc % 256)
        return out

    def _updatecrc(self):
        if self.buf == None:
            return
        if self.crc == None:
            self.crc = zlib.adler32(str(self.buf))
        else:
            self.crc = zlib.adler32(str(self.buf), self.crc)

    def _compress(self, final=None):
        self._updatecrc()
        blockfinal = 1 if final else 0
        data = zopfli.zopfli.deflate(str(self.buf), old_tail=buffer(self.lastbyte), bitpointer=self.bit, blockfinal=blockfinal, **self.opt)
        self.buf = bytearray('')
        res = bytearray(data[0])
        self.bit = data[1]
        if final:
            self.lastbyte = ''
            return res
        else:
            self.lastbyte = res[-32:]
            return res[:-32]

    def compress(self, string):
        global MASTER_BLOCK_SIZE
        self.buf.extend(bytearray(string))
        if len(self.buf) > MASTER_BLOCK_SIZE:
            out = bytearray()
            if self.first:
                out.extend(self._header())
                self.first = False
            out.extend(self._compress())
            return str(out)

    def flush(self):
        out = bytearray()
        if self.first:
            out.extend(self._header())
        out.extend(self._compress(True))
        out.extend(self._tail())
        return str(out)


def compress(data, **kwargs):
    """zlib.compress(data, **kwargs)
    
    """ + zopfli.__COMPRESSOR_DOCSTRING__  + """
    Returns:
      String containing a zlib container
    """
    cmpobj = compressobj(**kwargs)
    data1 = cmpobj.compress(data)
    data2 = cmpobj.flush()

    if data1 == None:
        return data2
    else:
        return data1 + data2
