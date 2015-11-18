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
def items(prev, dict_object):
    """Pipe wrapper for any dict object.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param dict_object: The dict object to be wrapped.
    :type dict_object: dict
    :returns: generator
    """
    for kv in dict_object.items():
        yield kv


@pipe.func
def flatten(prev, depth=sys.maxsize):
    """flatten pipe extracts nested item from previous pipe.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param depth: The deepest nested level to be extracted. 0 means no extraction.
    :type depth: integer
    :returns: generator
    """
    def inner_flatten(iterable, curr_level, max_levels):
        for i in iterable:
            if hasattr(i, '__iter__') and curr_level < max_levels:
                for j in inner_flatten(i, curr_level + 1, max_levels):
                    yield j
            else:
                yield i

    for d in prev:
        if hasattr(d, '__iter__') and depth > 0:
            for inner_d in inner_flatten(d, 1, depth):
                yield inner_d
        else:
            yield d


@pipe.func
def count(prev):
    """count pipe count how many data pass from previous pipe.

    This pipe will dropped all received data and return counting value after
    last data.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param dict_object: The dict object to be wrapped.
    :type dict_object: dict
    :returns: generator
    """
    count = 0
    for data in prev:
        count += 1
    yield count


@pipe.func
def enum(prev, start=0):
    """enum pipe wrap the built-in function *enumerate*. It passes a tuple
    to next pipe. The tuple contains a count(from start which defaults to 0)
    and the values passed from previous pipe.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param start: The start value of enumeration.
    :type start: integer
    :returns: generator
    """
    for data in enumerate(prev, start):
        yield data


@pipe.func
def pack(prev, n, **kw):
    """pack pipe takes n elements from previous generator and yield one
    list to next.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param rest: The previous iterator of pipe.
    :type prev: Pipe
    :returns: generator

    :Example:
    >>> result([1,2,3,4,5,6,7] | pack(3))
    [(1, 2, 3), (4, 5, 6)]

    .. note:: The last odd element will be dropped.
    """

    rest = kw.setdefault('rest', False)
    if kw.has_key('padding'):
        use_padding = True
        padding = kw['padding']
    else:
        use_padding = False
        padding = None

    items = []
    for i, data in enumerate(prev, 1):
        items.append(data)
        if (i % n) == 0:
            yield items
            items = []
    if len(items) != 0 and rest:
        if use_padding:
            items.extend([padding, ] * (n - i))
        yield items


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
def grep(prev, pattern, *args, **kw):
    """The pipe greps the data passed from previous generator according to
    given regular expression.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern which used to filter out data.
    :type pattern: str|unicode|re pattern object
    :param invert: If true, invert the match condition.
    :type invert: boolean
    :returns: generator
    """
    import re

    invert = False
    if kw.has_key('invert'):
        invert = kw.pop('invert')

    pattern_object = re.compile(pattern, *args, **kw)

    if not invert:
        for data in prev:
            if pattern_object.match(data):
                yield data
    else:
        for data in prev:
            if not pattern_object.match(data):
                yield data

@pipe.func
def match(prev, pattern, *args, **kw):
    """The pipe greps the data passed from previous generator according to
    given regular expression. The data passed to next pipe is a MatchObject.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern which used to filter data.
    :type pattern: str|unicode
    :returns: generator
    """
    import re

    pattern_object = re.compile(pattern, *args, **kw)

    for data in prev:
        match = pattern_object.match(data)
        if match:
            yield match

@pipe.func
def wildcard(prev, pattern, *args, **kw):
    """The pipe greps data passed from previous generator according to
    given regular expression.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The wildcard string which used to filter data.
    :type pattern: str|unicode|re pattern object
    :param invert: If true, invert the match condition.
    :type invert: boolean
    :returns: generator
    """
    import fnmatch

    invert = False
    if kw.has_key('invert'):
        invert = kw.pop('invert')

    pattern_object = re.compile(fnmatch.translate(pattern), *args, **kw)

    if not invert:
        for data in prev:
            if pattern_object.match(data):
                yield data
    else:
        for data in prev:
            if not pattern_object.match(data):
                yield data


@pipe.func
def stdout(prev, endl='', thru=True):
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
def stderr(prev, endl='', thru=True):
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
def fileobj(prev, file_handle, endl='', thru=True):
    """This pipe read/write data from/to file object which specified by
    file_handle.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param file_handle: The file object to read or write.
    :type file_handle: file object
    :param endl: The end-of-line symbol for each output.
    :type endl: str
    :param thru: If true, data will passed to next generator. If false, data
                 will be dropped.
    :type thru: bool
    :returns: generator
    """
    if prev is not None:
        for i in prev:
            file_handle.write(str(i))
            if endl:
                file_handle.write(endl)

            if thru:
                yield i
            else:
                yield
    else:
        for data in file_handle:
            yield data

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
    register_type(types.FunctionType, pipe.map)
    register_type(types.MethodType, pipe.map)
    register_type(types.TupleType, seq)
    register_type(types.ListType, seq)
    register_type(types.GeneratorType, seq)
    register_type(types.StringType, sh)
    register_type(types.UnicodeType, sh)
    register_type(types.FileType, fileobj)

register_default_types()
