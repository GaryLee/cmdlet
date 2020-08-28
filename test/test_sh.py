#!python
# coding: utf-8

import sys
import platform
from os import path
from cmdlet.cmds import *

is_py3 = sys.version_info >= (3, 0)

def test_sh_input():
    register_default_types()

    test_vector = ['this', 'is', 'a', 'shell', 'input', 'output', 'test', '!!']
    if is_py3:
        cmd=r'''python3 -c "from sys import stdout; [stdout.write('%%s\n' %% input().upper()) for x in range(%d)]" ''' % len(test_vector)
    else:
        cmd=r'''python -c "from sys import stdout; [stdout.write('%%s\n' %% raw_input().upper()) for x in range(%d)]" ''' % len(test_vector)

    result_list = result(test_vector | sh(cmd) | to_str)
    for i, item in enumerate(test_vector):
        assert item.upper() == result_list[i]

def test_sh_output():
    register_default_types()

    if platform.system() == 'Windows':
        list_file_cmd = 'dir/b test'
    else:
        list_file_cmd = '/bin/ls test'
    list_file_cmd2 = sh(list_file_cmd, trim=lambda s: s.rstrip())

    file_list = result(list_file_cmd | to_str | wildcard('*.py') | strip | lower)
    assert path.basename(__file__).lower() in file_list

    file_list = result(list_file_cmd2 | to_str | wildcard('*.py') | strip | lower)
    assert path.basename(__file__).lower() in file_list


def test_sh_without_cmd():
    register_default_types()

    cmd1 = range(30) | sh
    for i, v in enumerate(cmd1):
        assert i == v

    @pipe.func
    def stop_if_large_than(prev, thrd, init=0):
        count = init
        for i in prev:
            count += 1
            yield count
            if count >= thrd:
                break

    cmd2 = sh | stop_if_large_than(10)
    s = cmd2.run()
    assert s == 10
