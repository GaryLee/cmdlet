#!python
# coding: utf-8

"""This module contains utilities which based on the Pipe mechanism provided
by cmdlet.
"""

import sys
import os
import io
import re
import types
import subprocess
import string
import locale
import codecs
import functools
from six import PY3, StringIO, text_type, string_types
from cmdlet import Pipe, PipeFunction, register_type, unregister_type

#: Alias of cmdlet.PipeFuncion.
pipe = PipeFunction

#: data type of file for different python version.
if PY3:
    file = io.IOBase
file_type = file
#: data type of string for different python version.
string_type = string_types
#: data type of unicode for different python version.
unicode_type = text_type

#: Check if is string or unicode
is_str_type = lambda x: isinstance(x, (string_type, unicode_type))


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
def items(prev, dict_obj):
    """Pipe wrapper for any dict object.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param dict_obj: The dict object to be wrapped.
    :type dict_obj: dict
    :returns: generator
    """
    for kv in dict_obj.items():
        yield kv


@pipe.func
def attr(prev, attr_name):
    """attr pipe can extract attribute value of object.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param attr_name: The name of attribute
    :type attr_name: str
    :returns: generator
    """
    for obj in prev:
        if hasattr(obj, attr_name):
            yield getattr(obj, attr_name)


@pipe.func
def attrs(prev, attr_names):
    """attrs pipe can extract attribute values of object.

    If attr_names is a list and its item is not a valid attribute of
    prev's object. It will be excluded from yielded dict.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param attr_names: The list of attribute names
    :type attr_names: str of list
    :returns: generator
    """
    for obj in prev:
        attr_values = []
        for name in attr_names:
            if hasattr(obj, name):
                attr_values.append(getattr(obj, name))
        yield attr_values


@pipe.func
def attrdict(prev, attr_names):
    """attrdict pipe can extract attribute values of object into a dict.

    The argument attr_names can be a list or a dict.

    If attr_names is a list and its item is not a valid attribute of
    prev's object. It will be excluded from yielded dict.

    If attr_names is dict and the key doesn't exist in prev's object.
    the value of corresponding attr_names key will be copy to yielded dict.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param attr_names: The list or dict of attribute names
    :type attr_names: str of list or dict
    :returns: generator
    """
    if isinstance(attr_names, dict):
        for obj in prev:
            attr_values = dict()
            for name in attr_names.keys():
                if hasattr(obj, name):
                    attr_values[name] = getattr(obj, name)
                else:
                    attr_values[name] = attr_names[name]
            yield attr_values
    else:
        for obj in prev:
            attr_values = dict()
            for name in attr_names:
                if hasattr(obj, name):
                    attr_values[name] = getattr(obj, name)
            yield attr_values


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
def values(prev, *keys, **kw):
    """values pipe extract value from previous pipe.

    If previous pipe send a dictionary to values pipe, keys should contains
    the key of dictionary which you want to get. If previous pipe send list or
    tuple,

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :returns: generator
    """
    d = next(prev)
    if isinstance(d, dict):
        yield [d[k] for k in keys if k in d]
        for d in prev:
            yield [d[k] for k in keys if k in d]
    else:
        yield [d[i] for i in keys if 0 <= i < len(d)]
        for d in prev:
            yield [d[i] for i in keys if 0 <= i < len(d)]

@pipe.func
def counter(prev):
    """counter pipe count how many data pass from previous pipe.

    This pipe will dropped all received data and return counting value after
    last data.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param dict_obj: The dict object to be wrapped.
    :type dict_obj: dict
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
def pack(prev, n, rest=False, **kw):
    """pack pipe takes n elements from previous generator and yield one
    list to next.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param rest: Set True to allow to output the rest part of last elements.
    :type prev: boolean
    :param padding: Specify the padding element for the rest part of last elements.
    :type prev: boolean
    :returns: generator

    :Example:
    >>> result([1,2,3,4,5,6,7] | pack(3))
    [[1, 2, 3], [4, 5, 6]]

    >>> result([1,2,3,4,5,6,7] | pack(3, rest=True))
    [[1, 2, 3], [4, 5, 6], [7,]]

    >>> result([1,2,3,4,5,6,7] | pack(3, padding=None))
    [[1, 2, 3], [4, 5, 6], [7, None, None]]
    """

    if 'padding' in kw:
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
            items.extend([padding, ] * (n - (i % n)))
        yield items


@pipe.func
def fmt(prev, format_string):
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
        print(format_string, i, format_string.format(i))
        yield format_string.format(i)

@pipe.func
def grep(prev, *patterns, **kw):
    """The pipe greps the data passed from previous generator according to
    given regular expression.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param patterns: The patterns which used to filter out data. When more than one pattern specified, the data is passed if it matches any pattern.
    :type pattern: str|unicode|re pattern object
    :param inv: If true, invert the match condition.
    :type inv: boolean
    :param kw:
    :type kw: dict
    :returns: generator
    """
    inv = False if 'inv' not in kw else kw.pop('inv')
    pattern_objs = []
    for pattern in patterns:
        pattern_objs.append(re.compile(pattern, **kw))

    for data in prev:
        match = False
        for pattern_obj in pattern_objs:
            if bool(pattern_obj.search(data)):
                match = True
                break
        if bool(inv) ^ match:
            yield data

@pipe.func
def match(prev, *patterns, **kw):
    """The pipe greps the data passed from previous generator according to
    given regular expression. The data passed to next pipe is MatchObject
    , dict or tuple which determined by 'to' in keyword argument.

    By default, match pipe yields MatchObject. Use 'to' in keyword argument
    to change the type of match result.

    If 'to' is dict, yield MatchObject.groupdict().
    If 'to' is tuple, yield MatchObject.groups().
    If 'to' is list, yield list(MatchObject.groups()).

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern which used to filter data. When more than one pattern specified, the data is passed if it matches any pattern.
    :type pattern: str|unicode
    :param to: What data type the result should be stored. dict|tuple|list
    :type to: type
    :returns: generator
    """
    inv = False if 'inv' not in kw else kw.pop('inv')
    to = 'to' in kw and kw.pop('to')
    pattern_objs = []
    for pattern in patterns:
        pattern_objs.append(re.compile(pattern, **kw))

    for data in prev:
        match = None
        for pattern_obj in pattern_objs:
            match = pattern_obj.match(data)
            if match is not None:
                break
        if bool(inv) ^ (match is not None):
            if to is dict:
                yield match.groupdict()
            elif to is tuple:
                yield tuple(match.groups())
            elif to is list:
                yield list(match.groups())
            else:
                yield match

@pipe.func
def resplit(prev, pattern, *args, **kw):
    """The resplit pipe split previous pipe input by regular expression.

    Use 'maxsplit' keyword argument to limit the number of split.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern which used to split string.
    :type pattern: str|unicode
    """
    maxsplit = 0 if 'maxsplit' not in kw else kw.pop('maxsplit')
    pattern_obj = re.compile(pattern, *args, **kw)
    for s in prev:
        yield pattern_obj.split(s, maxsplit=maxsplit)


@pipe.func
def sub(prev, pattern, repl, *args, **kw):
    """sub pipe is a wrapper of re.sub method.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern string.
    :type pattern: str|unicode
    :param repl: Check repl argument in re.sub method.
    :type repl: str|unicode|callable
    """
    count = 0 if 'count' not in kw else kw.pop('count')
    pattern_obj = re.compile(pattern, *args, **kw)
    for s in prev:
        yield pattern_obj.sub(repl, s, count=count)


@pipe.func
def subn(prev, pattern, repl, *args, **kw):
    """subn pipe is a wrapper of re.subn method.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param pattern: The pattern string.
    :type pattern: str|unicode
    :param repl: Check repl argument in re.sub method.
    :type repl: str|unicode|callable
    """
    count = 0 if 'count' not in kw else kw.pop('count')
    pattern_obj = re.compile(pattern, *args, **kw)
    for s in prev:
        yield pattern_obj.subn(repl, s, count=count)


@pipe.func
def wildcard(prev, *patterns, **kw):
    """wildcard pipe greps data passed from previous generator
    according to given regular expression.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param patterns: The wildcard string which used to filter data. When more than one pattern specified, the data is passed if it matches any pattern.
    :type pattern: str|unicode|re pattern object
    :param inv: If true, invert the match condition.
    :type inv: boolean
    :returns: generator
    """
    import fnmatch

    inv = 'inv' in kw and kw.pop('inv')
    pattern_objs = []
    for pattern in patterns:
        pattern_objs.append(re.compile(fnmatch.translate(pattern), **kw))
    
    for data in prev:
        is_match = False
        for pattern_obj in pattern_objs:
            if pattern_obj.match(data):
                is_match = True
                break
        if bool(inv) ^ is_match:
            yield data

@pipe.func
def stdout(prev, endl='\n', thru=False):
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
        sys.stdout.write(str(i) + endl)
        if thru:
            yield i

@pipe.func
def stderr(prev, endl='\n', thru=False):
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
        sys.stderr.write(str(i) + endl)
        if thru:
            yield i

@pipe.func
def readline(prev, filename=None, mode='r', trim=None, start=1, end=sys.maxsize):
    """This pipe get filenames or file object from previous pipe and read the
    content of file. Then, send the content of file line by line to next pipe.

    The start and end parameters are used to limit the range of reading from file.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param filename: The files to be read. If None, use previous pipe input as filenames.
    :type filename: None|str|unicode|list|tuple
    :param mode: The mode to open file. default is 'r'
    :type mode: str
    :param trim: The function to trim the line before send to next pipe.
    :type trim: function object.
    :param start: if star is specified, only line number larger or equal to start will be sent.
    :type start: integer
    :param end: The last line number to read.
    :type end: integer
    :returns: generator
    """
    if trim is None:
        trim = lambda s: s.rstrip()
    if prev is None:
        if filename is None:
            raise Exception('No input available for readline.')
        elif is_str_type(filename):
            file_list = [filename, ]
        else:
            file_list = filename
    else:
        file_list = prev

    for fn in file_list:
        if isinstance(fn, file_type):
            fd = fn
        else:
            fd = open(fn, mode)

        try:
            if start <= 1 and end == sys.maxsize:
                for line in fd:
                    yield trim(line)
            else:
                for line_no, line in enumerate(fd, 1):
                    if line_no < start:
                        continue
                    yield trim(line)
                    if line_no >= end:
                        break
        finally:
            if fd != fn:
                fd.close()

@pipe.func
def fileobj(prev, file_handle, endl='', thru=False):
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
            file_handle.write(str(i)+endl)
            if thru:
                yield i
    else:
        for data in file_handle:
            yield data

@pipe.func
def sh(prev, *args, **kw):
    """sh pipe executes shell command specified by args. If previous pipe exists,
    read data from it and write it to stdin of shell process. The stdout of
    shell process will be passed to next pipe object line by line.

    Optional keyword arguments:
    - trim: Pass a function into sh pipe. It is used to trim the output from shell process. 
        The default trim function is str.rstrip. Therefore, any space characters in tail of
        shell process output line will be removed.
    - endl: Append the specified to each input line from previous pipe.
    - returncode: Set the expected returncode. It the returncode of process doesn't not equal to this value. A
        subprocess.CalledProcessError will be raised.
    - decode: The codecs to be used to decode the output of shell.

    For example:

    py_files = result(sh('ls') | strip | wildcard('*.py'))

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param args: The command line arguments. It will be joined by space character.
    :type args: list of string.
    :param kw: arguments for subprocess.Popen.
    :type kw: dictionary of options.
    :returns: generator
    """
    endl = '\n' if 'endl' not in kw else kw.pop('endl')
    returncode = None if 'returncode' not in kw else kw.pop('returncode')
    if PY3:
        decode = functools.partial(codecs.decode, encoding=locale.getdefaultlocale()[1]) if 'decode' not in kw else kw.pop('decode')
    else:
        decode = (lambda ln: codecs.decode(ln, locale.getdefaultlocale()[1])) if 'decode' not in kw else kw.pop('decode')
    trim = (lambda s: s.rstrip()) if 'trim' not in kw else kw.pop('trim')

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
    if prev is not None:
        stdin_buffer = StringIO()
        for i in prev:
            stdin_buffer.write(i)
            if endl:
                stdin_buffer.write(endl)
        if PY3:
            process.stdin.write(stdin_buffer.getvalue().encode('utf-8'))
        else:
            process.stdin.write(stdin_buffer.getvalue())
        process.stdin.flush()
        process.stdin.close()
        stdin_buffer.close()

    for line in process.stdout:
        yield trim(decode(line))
            
    process.wait()
    if returncode is not None and returncode != process.returncode:
        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmdline)

@pipe.func
def execmd(prev, *args, **kw):
    """execmd pipe executes shell command specified by previous pipe. 

    For example:

    py_files = result(readline("dir_list.txt", trim=str.strip) | fmt("ls {}") | execmd )

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param kw: arguments for subprocess.Popen.
    :type kw: dictionary of options.
    :returns: generator
    """
    returncode = None if 'returncode' not in kw else kw.pop('returncode')
    if PY3:
        decode = functools.partial(codecs.decode, encoding=locale.getdefaultlocale()[1]) if 'decode' not in kw else kw.pop('decode')
    else:
        decode = (lambda ln: codecs.decode(ln, locale.getdefaultlocale()[1])) if 'decode' not in kw else kw.pop('decode')

    trim = (lambda s: s.rstrip()) if 'trim' not in kw else kw.pop('trim')

    for cmdline in prev:
        process = subprocess.Popen(cmdline, shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            **kw)
        for line in process.stdout:
            yield trim(decode(line))
        process.wait()
        if returncode is not None and returncode != process.returncode:
            raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmdline)

@pipe.func
def walk(prev, inital_path, *args, **kw):
    """This pipe wrap os.walk and yield absolute path one by one.

    :param prev: The previous iterator of pipe.
    :type prev: Pipe
    :param args: The end-of-line symbol for each output.
    :type args: list of string.
    :param kw: The end-of-line symbol for each output.
    :type kw: dictionary of options. Add 'endl' in kw to specify end-of-line symbol.
    :returns: generator
    """
    for dir_path, dir_names, filenames in os.walk(inital_path):
        for filename in filenames:
            yield os.path.join(dir_path, filename)


#: alias of str.upper
upper = pipe.map(lambda s, *args, **kw: s.upper(*args, **kw))
#: alias of str.lower
lower = pipe.map(lambda s, *args, **kw: s.lower(*args, **kw))
#: alias of str.capwords
capwords = pipe.map(lambda s, *args, **kw: s.capwords(*args, **kw))
#: alias of str.capitalize
capitalize = pipe.map(lambda s, *args, **kw: s.capitalize(*args, **kw))
#: alias of str.lstrip
lstrip = pipe.map(lambda s, *args, **kw: s.lstrip(*args, **kw))
#: alias of str.rstrip
rstrip = pipe.map(lambda s, *args, **kw: s.rstrip(*args, **kw))
#: alias of str.strip
strip = pipe.map(lambda s, *args, **kw: s.strip(*args, **kw))
#: alias of str.expandtabs
expandtabs = pipe.map(lambda s, *args, **kw: s.expandtabs(*args, **kw))
#: alias of str.strip
strip = pipe.map(lambda s, *args, **kw: s.strip(*args, **kw))
#: alias of str.find
find = pipe.map(lambda s, *args, **kw: s.find(*args, **kw))
#: alias of str.rfind
rfind = pipe.map(lambda s, *args, **kw: s.rfind(*args, **kw))
#: alias of str.count
count = pipe.map(lambda s, *args, **kw: s.count(*args, **kw))
#: alias of str.split
split = pipe.map(lambda s, *args, **kw: s.split(*args, **kw))
#: alias of str.rsplit
rsplit = pipe.map(lambda s, *args, **kw: s.rsplit(*args, **kw))
#: alias of str.swapcase
swapcase = pipe.map(lambda s, *args, **kw: s.swapcase(*args, **kw))
#: alias of str.translate
translate = pipe.map(lambda s, *args, **kw: s.translate(*args, **kw))
#: alias of str.ljust
ljust = pipe.map(lambda s, *args, **kw: s.ljust(*args, **kw))
#: alias of str.rjust
rjust = pipe.map(lambda s, *args, **kw: s.rjust(*args, **kw))
#: alias of str.center
center = pipe.map(lambda s, *args, **kw: s.center(*args, **kw))
#: alias of str.zfill
zfill = pipe.map(lambda s, *args, **kw: s.zfill(*args, **kw))
#: alias of str.replace
replace = pipe.map(lambda s, *args, **kw: s.replace(*args, **kw))

@pipe.func
def join(prev, sep, *args, **kw):
    '''alias of str.join'''
    yield sep.join(prev, *args, **kw)

@pipe.func
def substitute(prev, *args, **kw):
    '''alias of string.Template.substitute'''
    template_obj = string.Template(*args, **kw)
    for data in prev:
        yield template_obj.substitute(data)

@pipe.func
def safe_substitute(prev, *args, **kw):
    '''alias of string.Template.safe_substitute'''
    template_obj = string.Template(*args, **kw)
    for data in prev:
        yield template_obj.safe_substitute(data)

@pipe.func
def to_str(prev, encoding=None):
    """Convert data from previous pipe with specified encoding."""
    first = next(prev)
    if isinstance(first, str):
        if encoding is None:
            yield first
            for s in prev:
                yield s
        else:
            yield first.encode(encoding)
            for s in prev:
                yield s.encode(encoding)
    else:
        if encoding is None:
            encoding = sys.stdout.encoding or 'utf-8'
        yield first.decode(encoding)
        for s in prev:
            yield s.decode(encoding)

def register_default_types():
    """Regiser all default type-to-pipe convertors."""
    register_type(type, pipe.map)
    register_type(types.FunctionType, pipe.map)
    register_type(types.MethodType, pipe.map)
    register_type(tuple, seq)
    register_type(list, seq)
    register_type(types.GeneratorType, seq)
    register_type(string_type, sh)
    register_type(unicode_type, sh)
    register_type(file_type, fileobj)

    if PY3:
        register_type(range, seq)
        register_type(map, seq)

register_default_types()
