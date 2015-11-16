#!python
# coding: utf-8

import sys
import re
import types
import subprocess
import string
from StringIO import StringIO
from cmdlet import Pipe, PipeFunction, register_type, unregister_type

func = PipeFunction

@func.pipe
def seq(prev, sequence):
    for i in sequence:
        yield i

@func.pipe
def pair(prev, **kw):
    for i, d in enumerate(prev):
        if (i % 2) == 0:
            d_prev = d
        else:
            yield (d_prev, d)

@func.pipe
def format(prev, format_string):
    for i in prev:
        yield (format_string % i)

@func.pipe
def stdout(prev, endl='', thru=False):
    for i in prev:
        sys.stdout.write(str(i))
        if endl:
            sys.stdout.write(endl)
        if thru:
            yield i
        else:
            yield

@func.pipe
def stderr(prev, endl='', thru=False):
    for i in prev:
        sys.stderr.write(str(i))
        if endl:
            sys.stdout.write(endl)
        if thru:
            yield i
        else:
            yield

@func.pipe
def sh(prev, *args, **kw):
    cmdline = ' '.join(args)
    if not cmdline:
        if prev is not None:
            for i in prev:
                yield i
        else:
            while True:
                yield None

    process = subprocess.Popen(cmdline, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        **kw)
    endl = kw.setdefault('endl', '\n')
    if prev is not None:
        stdin_buffer = StringIO()
        for i in prev:
            stdin_buffer.write(i)
            if endl:
                stdin_buffer.write(endl)

        process.stdin.write(stdin_buffer.getvalue())
        process.stdin.flush()
        process.stdin.close()
        stdin_buffer.close()

    for line in process.stdout:
        yield line

    process.wait()

def run(cmd):
    return cmd.run()

def result(cmd):
    return cmd.result()

def register_default_types():
    register_type(types.TypeType, func.map)
    register_type(types.FunctionType, func.pipe)
    register_type(types.MethodType, func.pipe)
    register_type(types.LambdaType, func.pipe)
    register_type(types.TupleType, seq)
    register_type(types.ListType, seq)
    register_type(types.GeneratorType, seq)
    register_type(types.StringType, sh)
    register_type(types.UnicodeType, sh)

register_default_types()
