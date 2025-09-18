from __future__ import annotations
import importlib

import oxidized_importer
import sys
import os

def monkey_patch_debug():
    orig_find_spec = oxidized_importer.OxidizedFinder.find_spec

    def debug_find_spec(self, fullname, path=None, target=None):
        print(f"[OXIDIZED] Asked for: {fullname}")
        spec = orig_find_spec(self, fullname, path, target)
        if spec is None:
            print(f"[OXIDIZED] => NOT FOUND, passing to next finder.")
        else:
            print(f"[OXIDIZED] => FOUND!")
        return spec

    oxidized_importer.OxidizedFinder.find_spec = debug_find_spec

# for name in sorted(sys.modules.keys()):
#     print("sys.modules:", name)

monkey_patch_debug()
# Load those resources into an instance of our custom importer. This
# will read the index in the passed data structure and make all
# resources immediately available for importing.
finder = oxidized_importer.OxidizedFinder(relative_path_origin=os.getcwd())
finder.index_file_memory_mapped("/workspace/clive_workspace/clive/oxidized_resources_simply")

# If the relative path of filesystem-based resources is not relative
# to the current executable (which is likely the ``python3`` executable),
# you'll need to set ``origin`` to the directory the resources are
# relative to.
# finder = oxidized_importer.OxidizedFinder(
#     relative_path_origin=os.path.dirname(os.path.abspath(__file__)),
# )
# finder = oxidized_importer.OxidizedFinder(
#     relative_path_origin="/workspace/clive_workspace/clive/")
# packed_data = finder.serialize_indexed_resources()

# finder.index_bytes(packed_data)


# Register the meta path finder as the first item, making it the
# first finder that is consulted.
sys.meta_path.insert(0, finder)
# print(f"Indexy{finder.indexed_resources()}")
print("Udało się zaimportować oxidized_importer")
# At this point, you should be able to ``import`` modules defined
# in the resources data
# for name in sorted(sys.modules.keys()):
#     print("sys.modules po operacji:", name)


import __future__
import _collections_abc
import _compat_pickle
import _compression
import _markupbase
import _osx_support
import _py_abc
import _pydecimal
import _pyio
import _sitebuiltins
import _strptime
import _threading_local
import _weakrefset
import abc
import aifc
import argparse
import ast
import asyncio
import asyncio.base_events
import asyncio.base_futures
import asyncio.base_subprocess
import asyncio.base_tasks
import asyncio.constants
import asyncio.coroutines
import asyncio.events
import asyncio.format_helpers
import asyncio.futures
import asyncio.locks
import asyncio.log
import asyncio.proactor_events
import asyncio.protocols
import asyncio.queues
import asyncio.runners
import asyncio.selector_events
import asyncio.sslproto
import asyncio.streams
import asyncio.subprocess
import asyncio.tasks
import asyncio.transports
import asyncio.unix_events
import base64
import bdb
import bisect
import bz2
import cProfile
import calendar
import cgi
import cgitb
import chunk
import cmd
import code
import codecs
import codeop
import collections
import collections.abc
import colorsys
import compileall
import concurrent
import concurrent.futures
import concurrent.futures._base
import concurrent.futures.process
import concurrent.futures.thread
import configparser
import contextlib
import contextvars
import copy
import copyreg
import crypt
import csv
import ctypes
import ctypes._aix
import ctypes._endian
import ctypes.util
import dataclasses
import datetime
import dbm
import dbm.dumb
import decimal
import difflib
import dis
# import distutils
# import distutils.archive_util
# import distutils.ccompiler
# import distutils.cmd
# import distutils.command
# import distutils.command.bdist
# import distutils.command.bdist_rpm
# import distutils.command.build
# import distutils.command.build_clib
# import distutils.command.build_ext
# import distutils.command.build_py
# import distutils.command.install
# import distutils.command.install_data
# import distutils.command.install_egg_info
# import distutils.command.install_headers
# import distutils.command.install_lib
# import distutils.command.install_scripts
# import distutils.command.sdist
# import distutils.core
# import distutils.cygwinccompiler
# import distutils.debug
# import distutils.dep_util
# import distutils.dir_util
# import distutils.dist
# import distutils.errors
# import distutils.extension
# import distutils.fancy_getopt
# import distutils.file_util
# import distutils.filelist
# import distutils.log
# import distutils.spawn
# import distutils.sysconfig
# import distutils.text_file
# import distutils.unixccompiler
# import distutils.util
# import distutils.version
# import distutils.versionpredicate
import doctest
import email
import email._encoded_words
import email._header_value_parser
import email._parseaddr
import email._policybase
import email.base64mime
import email.charset
import email.contentmanager
import email.encoders
import email.errors
import email.feedparser
import email.generator
import email.header
import email.headerregistry
import email.iterators
import email.message
import email.mime
import email.mime.application
import email.mime.audio
import email.mime.base
import email.mime.image
import email.mime.message
import email.mime.multipart
import email.mime.nonmultipart
import email.mime.text
import email.parser
import email.policy
import email.quoprimime
import email.utils
import encodings
import encodings.aliases
import encodings.ascii
import encodings.base64_codec
import encodings.big5
import encodings.big5hkscs
import encodings.bz2_codec
import encodings.charmap
import encodings.cp037
import encodings.cp1006
import encodings.cp1026
import encodings.cp1125
import encodings.cp1140
import encodings.cp1250
import encodings.cp1251
import encodings.cp1252
import encodings.cp1253
import encodings.cp1254
import encodings.cp1255
import encodings.cp1256
import encodings.cp1257
import encodings.cp1258
import encodings.cp273
import encodings.cp424
import encodings.cp437
import encodings.cp500
import encodings.cp720
import encodings.cp737
import encodings.cp775
import encodings.cp850
import encodings.cp852
import encodings.cp855
import encodings.cp856
import encodings.cp857
import encodings.cp858
import encodings.cp860
import encodings.cp861
import encodings.cp862
import encodings.cp863
import encodings.cp864
import encodings.cp865
import encodings.cp866
import encodings.cp869
import encodings.cp874
import encodings.cp875
import encodings.cp932
import encodings.cp949
import encodings.cp950
import encodings.euc_jis_2004
import encodings.euc_jisx0213
import encodings.euc_jp
import encodings.euc_kr
import encodings.gb18030
import encodings.gb2312
import encodings.gbk
import encodings.hex_codec
import encodings.hp_roman8
import encodings.hz
import encodings.idna
import encodings.iso2022_jp
import encodings.iso2022_jp_1
import encodings.iso2022_jp_2
import encodings.iso2022_jp_2004
import encodings.iso2022_jp_3
import encodings.iso2022_jp_ext
import encodings.iso2022_kr
import encodings.iso8859_1
import encodings.iso8859_10
import encodings.iso8859_11
import encodings.iso8859_13
import encodings.iso8859_14
import encodings.iso8859_15
import encodings.iso8859_16
import encodings.iso8859_2
import encodings.iso8859_3
import encodings.iso8859_4
import encodings.iso8859_5
import encodings.iso8859_6
import encodings.iso8859_7
import encodings.iso8859_8
import encodings.iso8859_9
import encodings.johab
import encodings.koi8_r
import encodings.koi8_t
import encodings.koi8_u
import encodings.kz1048
import encodings.latin_1
import encodings.mac_arabic
import encodings.mac_croatian
import encodings.mac_cyrillic
import encodings.mac_farsi
import encodings.mac_greek
import encodings.mac_iceland
import encodings.mac_latin2
import encodings.mac_roman
import encodings.mac_romanian
import encodings.mac_turkish
import encodings.palmos
import encodings.ptcp154
import encodings.punycode
import encodings.quopri_codec
import encodings.raw_unicode_escape
import encodings.rot_13
import encodings.shift_jis
import encodings.shift_jis_2004
import encodings.shift_jisx0213
import encodings.tis_620
import encodings.undefined
import encodings.unicode_escape
import encodings.utf_16
import encodings.utf_16_be
import encodings.utf_16_le
import encodings.utf_32
import encodings.utf_32_be
import encodings.utf_32_le
import encodings.utf_7
import encodings.utf_8
import encodings.utf_8_sig
import encodings.uu_codec
import encodings.zlib_codec
import ensurepip
import ensurepip.__main__
import ensurepip._uninstall
import enum
import filecmp
import fileinput
import fnmatch
import fractions
import ftplib
import functools
import genericpath
import getopt
import getpass
import gettext
import glob
import gzip
import hashlib
import heapq
import hmac
import html
import html.entities
import html.parser
import http
import http.client
import http.cookiejar
import http.cookies
import http.server
import imaplib
import imghdr
import importlib
import importlib._bootstrap
import importlib._bootstrap_external
import importlib.abc
import importlib.machinery
import importlib.resources
import importlib.util
import inspect
import io
import ipaddress
import json
import json.decoder
import json.encoder
import json.scanner
import json.tool
import keyword
import linecache
import locale
import logging
import logging.config
import logging.handlers
import lzma
import mailbox
import mailcap
import mimetypes
import modulefinder
import multiprocessing
import multiprocessing.connection
import multiprocessing.context
import multiprocessing.dummy
import multiprocessing.dummy.connection
import multiprocessing.forkserver
import multiprocessing.heap
import multiprocessing.managers
import multiprocessing.pool
import multiprocessing.popen_fork
import multiprocessing.popen_forkserver
import multiprocessing.popen_spawn_posix
import multiprocessing.process
import multiprocessing.queues
import multiprocessing.reduction
import multiprocessing.resource_sharer
import multiprocessing.sharedctypes
import multiprocessing.spawn
import multiprocessing.synchronize
import multiprocessing.util
import netrc
import nntplib
import ntpath
import nturl2path
import numbers
import opcode
import operator
import optparse
import os
import pathlib
import pdb
import pickle
import pickletools
import pipes
import pkgutil
import platform
import plistlib
import poplib
import posixpath
import pprint
import profile
import pstats
import pty
import py_compile
import pyclbr
import pydoc
import pydoc_data
import pydoc_data.topics
import queue
import quopri
import random
import re
import reprlib
import rlcompleter
import runpy
import sched
import secrets
import selectors
import shelve
import shlex
import shutil
import signal
import site
import smtplib
import sndhdr
import socket
import socketserver
import sqlite3
import sqlite3.dbapi2
import sqlite3.dump
import sre_compile
import sre_constants
import sre_parse
import ssl
import stat
import statistics
import string
import stringprep
import struct
import subprocess
import sunau
import symtable
import sysconfig
import tabnanny
import tarfile
import telnetlib
import tempfile
import test
import textwrap
import this
import threading
import timeit
import token
import tokenize
import trace
import traceback
import tracemalloc
import tty
import types
import typing
import unittest
import unittest.case
import unittest.loader
import unittest.main
import unittest.mock
import unittest.result
import unittest.runner
import unittest.signals
import unittest.suite
import unittest.util
import urllib
import urllib.error
import urllib.parse
import urllib.request
import urllib.response
import urllib.robotparser
import uuid
import venv
import warnings
import wave
import weakref
import webbrowser
import wsgiref
import wsgiref.handlers
import wsgiref.headers
import wsgiref.simple_server
import wsgiref.util
import wsgiref.validate
import xml.dom
import xml.dom.NodeFilter
import xml.dom.domreg
import xml.dom.expatbuilder
import xml.dom.minicompat
import xml.dom.minidom
import xml.dom.pulldom
import xml.dom.xmlbuilder
import xml.etree
import xml.etree.ElementInclude
import xml.etree.ElementPath
import xml.etree.ElementTree
import xml.etree.cElementTree
import xml.parsers
import xml.parsers.expat
import xml.sax
import xml.sax._exceptions
import xml.sax.expatreader
import xml.sax.handler
import xml.sax.saxutils
import xml.sax.xmlreader
import xmlrpc
import xmlrpc.client
import xmlrpc.server
import zipapp
import zipfile

if __name__ == "__main__":
    print("Program")
