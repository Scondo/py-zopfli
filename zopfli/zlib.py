from __future__ import absolute_import

import zopfli
import zopfli.zopfli
import zlib

def compress(data, **kwargs):
    """zlib.compress(data, **kwargs)
    
    """ + zopfli.__COMPRESSOR_DOCSTRING__  + """
    Returns:
      String containing a zlib container
    """
    checksum = zlib.adler32(data)
    cmf = 120
    flevel = 0
    fdict = 0
    cmfflg = 256 * cmf + fdict * 32 + flevel * 64
    fcheck = 31 - cmfflg % 31
    cmfflg += fcheck
    out = bytearray()
    out.append(cmfflg / 256)
    out.append(cmfflg % 256)

    out.extend(zopfli.zopfli.deflate(data, **kwargs))

    out.append((checksum >> 24) % 256)
    out.append((checksum >> 16) % 256)
    out.append((checksum >> 8) % 256)
    out.append(checksum % 256)
    return buffer(out)
