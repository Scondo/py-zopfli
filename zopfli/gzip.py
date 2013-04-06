from __future__ import absolute_import

import zopfli
import zopfli.zopfli
import zlib

def compress(data, *args, **kwargs):
    """gzip.compress(data, **kwargs)
    
    """ + zopfli.__COMPRESSOR_DOCSTRING__  + """
    Returns:
      String containing a gzip container
    """
    crcvalue = zlib.crc32(data)
    out = bytearray()
    out.append(31)   # ID1
    out.append(139)  # ID2
    out.append(8)    # CM
    out.append(0)    # FLG
    #MTIME
    out.extend((0, 0, 0, 0))
    out.append(2)    # XFL, 2 indicates best compression
    out.append(3)    # OS follows Unix conventions

    out.extend(zopfli.zopfli.deflate(data, **kwargs)[0])

    out.append(crcvalue % 256)
    out.append((crcvalue >> 8) % 256)
    out.append((crcvalue >> 16) % 256)
    out.append((crcvalue >> 24) % 256)

    #ISIZE
    insize = len(data)
    out.append(insize % 256)
    out.append((insize >> 8) % 256)
    out.append((insize >> 16) % 256)
    out.append((insize >> 24) % 256)
    return buffer(out)
