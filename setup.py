#!/usr/bin/env python
"""
pyzopfli
======

Python bindings to zopfli
"""

from setuptools import setup, Extension

setup(
    name='pyzopfli',
    version='0.1.0',
    author='Pavel Zlatovratsky (Scondo)',
    author_email='scondo@mail.ru',
    description='Zopfli module for python',
    long_description=__doc__,
    py_modules = [
        'pyzopfli',
        'pyzopfli.zlib',
        ],
    ext_modules = [Extension('pyzopfli.zopfli',
                             opts = "-O2 -W -Wall -Wextra -ansi -pedantic -lm",
                             sources = [
                'pyzopfli/blocksplitter.c',
                'pyzopfli/cache.c',
                'pyzopfli/deflate.c',
                'pyzopfli/squeeze.c',
                'pyzopfli/hash.c',
                'pyzopfli/katajainen.c',
                'pyzopfli/lz77.c', 
                'pyzopfli/tree.c',
                'pyzopfli/util.c',
                'pyzopfli/zopflimodule.c',
                ],
                             libraries = []
                             )],
    packages = ["pyzopfli"],
    zip_safe=True,
    license='ASL',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Compression',
        ],
    scripts = [
        ],
    url = "https://github.com/Scondo/pyzopfli",
    install_requires = [
        ]
)

