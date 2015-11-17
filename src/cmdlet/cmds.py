#!python
# coding: utf-8

"""This module contains utilities which based on the Pipe mechanism provided
by cmdlet.
"""

import sys
import re
import types
import subprocess
import string
from StringIO import StringIO
from cmdlet import Pipe, PipeFunction, register_type, unregister_type

#: Alias of cmdlet.PipeFuncion.
pipe = PipeFunction

def run(cmd):
    """Run pipe object and return its last result.

    :param cmd: The Pipe object to be executed.
    :type cmd: Pipe
    :returns: The last result.

    .. seealso::
        :py:meth:`cmdlet.Pipe.run`
    """
    return cmd.run()


def result(cmd):
    """Run pipe object and return its result in a list.

    :param cmd: The Pipe object to be executed.
    :type cmd: Pipe
    :returns: The list which contains the result of pipe.

    .. seealso::
        :py:meth:`cmdlet.Pipe.result`
    """
    return cmd.result()


@pipe.func
def seq(prev, sequence):
    """Pipe wrapper for any iterable object.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param sequence: The iterable object to be wrapped.
    :type sequence: iterator
    :returns: generator
    """
    for i in sequence:
        yield i


@pipe.func
def pair(prev, **kw):
    """The pipe takes two elements from previous generator and yield one
    tuple pair to next.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :returns: generator

    :Example:
    >>> result([1,2,3,4,5,6,7] | pair)
    [(1, 2), (3, 4), (5, 6)]

    .. note:: The last odd element will be dropped.
    """
    for i, d in enumerate(prev):
        if (i % 2) == 0:
            d_prev = d
        else:
            yield (d_prev, d)


@pipe.func
def format(prev, format_string):
    """The pipe formats the data passed from previous generator according to
    given format_string argument.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param format_string: format string which used to format the data from
                          previous iterator.
    :type sequence: str
    :returns: generator
    """
    for i in prev:
        yield (format_string % i)


@pipe.func
def stdout(prev, endl='', thru=False):
    """This pipe read data from previous iterator and write it to stdout.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param endl: The end-of-line symbol for each output.
    :type endl: str
    :param thru: If true, data will passed to next generator. If false, data
                 will be dropped.
    :type thru: bool
    :returns: generator
    """
    for i in prev:
        sys.stdout.write(str(i))
        if endl:
            sys.stdout.write(endl)
        if thru:
            yield i
        else:
            yield


@pipe.func
def stderr(prev, endl='', thru=False):
    """This pipe read data from previous iterator and write it to stderr.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param endl: The end-of-line symbol for each output.
    :type endl: str
    :param thru: If true, data will passed to next generator. If false, data
                 will be dropped.
    :type thru: bool
    :returns: generator
    """
    for i in prev:
        sys.stderr.write(str(i))
        if endl:
            sys.stderr.write(endl)
        if thru:
            yield i
        else:
            yield


@pipe.func
def sh(prev, *args, **kw):
    """This pipe read data from previous iterator and write it to stderr.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param args: The end-of-line symbol for each output.
    :type args: list of string.
    :param kw: The end-of-line symbol for each output.
    :type kw: dictionary of options. Add 'endl' in kw to specify end-of-line symbol.
    :returns: generator
    """
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

def register_default_types():
    """Regiser all default type-to-pipe convertors."""
    register_type(types.TypeType, pipe.map)
    register_type(types.FunctionType, pipe.func)
    register_type(types.MethodType, pipe.func)
    register_type(types.TupleType, seq)
    register_type(types.ListType, seq)
    register_type(types.GeneratorType, seq)
    register_type(types.StringType, sh)
    register_type(types.UnicodeType, sh)

register_default_types()
