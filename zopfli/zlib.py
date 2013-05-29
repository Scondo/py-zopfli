from __future__ import absolute_import

import zopfli
import zopfli.zopfli
from zlib import adler32
from zlib import crc32
from zlib import decompress, decompressobj
from zlib import error
try:
    from zlib import DEFLATED, DEF_MEM_LEVEL, MAX_WBITS, Z_DEFAULT_STRATEGY
    from zlib import Z_NO_FLUSH, Z_SYNC_FLUSH, Z_FULL_FLUSH, Z_FINISH
    from zlib import Z_NO_COMPRESSION, Z_BEST_SPEED, Z_BEST_COMPRESSION, Z_DEFAULT_COMPRESSION
except ImportError:
    Z_NO_FLUSH = 0
    #Z_PARTIAL_FLUSH = 1
    Z_SYNC_FLUSH = 2
    Z_FULL_FLUSH = 3
    Z_FINISH = 4
    #Z_BLOCK = 5
    #Z_TREES = 6
    #Compression levels.
    Z_NO_COMPRESSION = 0
    Z_BEST_SPEED = 1
    Z_BEST_COMPRESSION = 9
    Z_DEFAULT_COMPRESSION = -1
    #Compression strategy
    Z_FILTERED = 1
    Z_HUFFMAN_ONLY = 2
    Z_RLE = 3
    Z_FIXED = 4
    Z_DEFAULT_STRATEGY = 0
    #The deflate compression method (the only one supported in this version).
    DEFLATED = 8
    DEF_MEM_LEVEL = 8
    MAX_WBITS = 15

levit = {-1: 15,
         0: 1,
         1: 1,
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


def int2bitlist(data, length):
    res = []
    nowbyte = data
    for nbit in range(0, length):
        (nowbyte, bit) = divmod(nowbyte, 2)
        res.append(bit)
    res.reverse()
    return res


def bitlist2int(data):
    data = list(data)
    data.reverse()
    res = 0
    for nbit, bit in enumerate(data):
        res += bit << nbit
    return res


class compressobj(object):
    def __init__(self, level=Z_DEFAULT_COMPRESSION, method=DEFLATED, windowBits=MAX_WBITS, memlevel=DEF_MEM_LEVEL, strategy=Z_DEFAULT_STRATEGY, **kwargs):
        '''simulate zlib deflateInit2
        level - compression level
        method - compression method, only DEFLATED supported
        windowBits - should be in the range 8..15, practically ignored
                     can also be -8..-15 for raw deflate
                     zlib also have gz with "Add 16 to windowBit" - not implemented here
        memlevel - originally specifies how much memory should be allocated
                    zopfli - ignored
        strategy - originally is used to tune the compression algorithm
                    zopfli - ignored
        '''
        if method != DEFLATED:
            raise error
        self.raw = windowBits < 0
        if abs(windowBits) > MAX_WBITS or abs(windowBits) < 5:
            raise ValueError
        self.crc = None
        self.buf = bytearray('')
        self.bit = 0
        self.first = True
        self.opt = kwargs
        self.lastbyte = ''
        if 'numiterations' not in self.opt:
            if level in levit:
                self.opt['numiterations'] = levit[level]
            else:
                raise error

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
        if self.buf == None or self.raw:
            return
        if self.crc == None:
            self.crc = adler32(str(self.buf))
        else:
            self.crc = adler32(str(self.buf), self.crc)

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
            if not self.raw and self.first:
                out.extend(self._header())
                self.first = False
            out.extend(self._compress())
            return str(out)
        else:
            return b''

    def flush(self, mode=Z_FINISH):
        out = bytearray()
        #mode = Z_FINISH
        if not self.raw and self.first:
            out.extend(self._header())
        out.extend(self._compress(mode == Z_FINISH))
        if mode != Z_FINISH:
            self.bit = self.bit % 8
            if self.bit:
                work = int2bitlist(self.lastbyte.pop(), 8)
            else:
                work = [0, 0, 0, 0, 0, 0, 0, 0]
            work.reverse()
            if self.bit > 4:
                work.extend((0, ) * 8)
            work[self.bit:self.bit + 3] = [0, 0, 0]
            work.reverse()
            self.lastbyte.append(bitlist2int(work[-8:]))
            if len(work) == 16:
                self.lastbyte.append(bitlist2int(work[:8]))
            self.lastbyte.extend((0, 0, 255, 255))
            out.extend(self.lastbyte)
            self.lastbyte = ''
            self.bit = 0
            #add void fixed block

        if not self.raw and mode == Z_FINISH:
            out.extend(self._tail())
        return str(out)


def compress(data, level=6, **kwargs):
    """zlib.compress(data, **kwargs)
    
    """ + zopfli.__COMPRESSOR_DOCSTRING__  + """
    Returns:
      String containing a zlib container
    """
    cmpobj = compressobj(level=level, **kwargs)
    data1 = cmpobj.compress(data)
    data2 = cmpobj.flush()

    if data1 == None:
        return data2
    else:
        return data1 + data2
