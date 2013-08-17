PYZOPFLI
========

cPython bindings for [zopfli][zopfli].


USAGE
=====

pyzopfli is a package which allows using [zopfli][zopfli] library in Python.

Main public module is pyzopfli.zlib. It provides emulation of standard 
zlib module and can be used in any application as drop-in replace. 
Decompression functions are imported in pyzopfli.zlib from zlib.

    import pyzopfli.zlib as zlib
    
pyzopfli may be used with gzip or zipfile modules of standard library 
by replacing their zlib module attribute in runtime.  

	import pyzopfli.zlib as zlib
	import zipfile
	zipfile.zlib = zlib

You also can slightly cheat and control power of compression 
with 'levit' attribute of pyzopli.zlib module

    import pyzopfli.zlib as zlib
	zlib.levit[zlib.Z_DEFAULT_COMPRESSION] = iterations

pyzopfli.zlib passes standard's library unittest with same failures as native zlib
(few failures are errors of decompressor)
Same for gzip and zipfile modules with replaced zlib.

[zopfli]: http://googledevelopers.blogspot.com/2013/02/compress-data-more-densely-with-zopfli.html

TODO
====

* Zopfli isn't optimal for already compressed file. Post-processing required 
to keep some blocks uncompressed.
