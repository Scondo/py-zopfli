#!/usr/bin/env python

import gzip
import unittest
import zlib
import zopfli.gzip
import zopfli.zlib
import StringIO


class Tests(object):
    data = unittest.__doc__

    def test_reversible(self):
        data = self.data
        self.assertEquals(self.decompress(self.compress(data)), data)

    def test_iterations_help(self):
        data = self.data
        self.assertTrue(len(self.compress(data, numiterations=1)) > len(self.compress(data, numiterations=1000)))


class ZlibTest(unittest.TestCase, Tests):
    compress = staticmethod(zopfli.zlib.compress)
    decompress = staticmethod(zlib.decompress)

    def test_object(self):
        compressed = None
        data = ""
        zopfli.zlib.MASTER_BLOCK_SIZE = 1000
        compressor = zopfli.zlib.compressobj(1)
        while compressed == None:
            compressed = compressor.compress(self.data)
            data = data + self.data
        compressed = compressed + compressor.flush()
        self.assertEquals(self.decompress(compressed), data)

class GzipTest(unittest.TestCase, Tests):
    compress = staticmethod(zopfli.gzip.compress)

    def decompress(self, s):
        return gzip.GzipFile(fileobj=StringIO.StringIO(s)).read()


if __name__ == "__main__":
    unittest.main()
