#!python
# coding: utf-8

import sys

from cmdlet import *
from cmdlet.cmds import *

upper = pipe.map(str.upper)
lower = pipe.map(str.lower)

def test_pipe_ans():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = fmt('fOo{}') | upper
    cmd_lower = lower | fmt('{}BaR')

    cmd1 = range(test_num) | cmd_upper
    ans = cmd1.run()
    assert ans == ('FOO{}'.format(test_num-1))

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    ans = cmd2.run()
    assert ans == ('foo{}BaR'.format(test_num-1))


def test_pipe_result():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = fmt('fOo{}') | upper
    cmd_lower = lower | fmt('{}BaR')

    cmd1 = range(test_num) | cmd_upper
    for i, data in enumerate(cmd1.result()):
        assert data == ('FOO{}'.format(i))

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    for i, data in enumerate(cmd2.result()):
        assert data == ('foo{}BaR'.format(i))


def test_pipe_iter():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = fmt('fOo{}') | upper
    cmd_lower = lower | fmt('{}BaR')

    cmd1 = range(test_num) | cmd_upper
    for i, data in enumerate(cmd1):
        assert data == ('FOO{}'.format(i))

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    for i, data in enumerate(cmd2):
        assert data == ('foo{}BaR'.format(i))

    for i, data in enumerate(cmd1.iter()):
        assert data == ('FOO{}'.format(i))

    for i, data in enumerate(cmd2.iter()):
        assert data == ('foo{}BaR'.format(i))


def test_pipe_map():
    import string
    register_default_types()

    test_num = 100
    test_list = list(range(test_num))
    upper = pipe.map(str.upper)
    cmd1 = seq(test_list) | str | upper
    for i, data in enumerate(cmd1):
        assert str(i).upper() == data

    cmd2 = upper | str
    try:
        cmd2.run()
    except TypeError as e:
        assert e.args[0] == 'A mapper must have input.'


def test_pipe_filter():
    import string
    register_default_types()

    test_num = 100
    test_list = list(range(test_num))
    upper = pipe.map(str.upper)
    less_or_equal_3 = pipe.filter(lambda x: x <= 3)
    cmd1 = seq(test_list) | less_or_equal_3 | str | upper
    for i, data in enumerate(cmd1):
        assert str(i).upper() == data

    last = cmd1.run()
    assert last == '3'

    cmd2 = less_or_equal_3 | str
    try:
        cmd2.run()
    except TypeError as e:
        assert e.args[0] == 'A filter must have input.'


def test_pipe_reduce():
    import string
    register_default_types()

    @pipe.reduce
    def count_mod_10(accu, data):
        return accu + (1 if (data % 10) == 0 else 0)

    test_num = 100
    test_list = list(range(test_num))
    cmd1 = test_list | count_mod_10(init=0)

    ans = cmd1.run()
    assert ans == (test_num // 10)

    test_num = 100
    test_list = list(range(test_num))
    cmd2 = test_list | count_mod_10(init=0)

    ans = cmd2.run()
    assert ans == (test_num // 10)

    cmd3 = count_mod_10 | str
    try:
        cmd3.run()
    except TypeError as e:
        assert e.args[0] == 'A reducer must have input.'

def test_pipe_stopper():
    register_default_types()

    @pipe.stopper
    def stop_if_count_larger_than(data, thrd=sys.maxsize):
        return data > thrd

    test_num = 100
    test_list = list(range(test_num))
    stop_thrd = 20
    cmd1 = test_list | stop_if_count_larger_than(thrd=stop_thrd)
    ans = cmd1.run()
    assert ans == stop_thrd

    cmd2 = stop_if_count_larger_than | str
    try:
        cmd2.run()
    except TypeError as e:
        assert e.args[0] == 'A stopper must have input.'

def test_pipe_chain():
    import string
    register_default_types()

    @pipe.reduce
    def count(accu, data, **kw):
        return accu + 1

    @pipe.filter
    def low_pass(data, threshold):
        return data <= threshold

    count_low_pass = low_pass(10) | count(init=0)

    ans = run(range(1,100) | count_low_pass)
    assert ans == 10

    ans = run(range(1,100) | count_low_pass(20))
    assert ans == 20


def test_pipe_type_registration():

    unregister_all_types()
    test_list = ['abc','def','ghi','jkl','mno','pqr','stu','vex','yz']

    exception_catched = False
    try:
        cmd1 = test_list | upper
        cmd1.run()
    except UnregisteredPipeType:
        exception_catched = True

    assert exception_catched

    exception_catched = False
    try:
        cmd2 = sh | test_list | upper
        cmd2.run()
    except UnregisteredPipeType:
        exception_catched = True

    assert exception_catched

    if not has_registered_type(list):
        register_type(list, seq)

    cmd3 = sh | test_list | upper
    for i, data in enumerate(cmd3):
        assert data == test_list[i].upper()

    cmd_list = seq(test_list)
    cmd4 = sh | cmd_list | cmd3
    cmd5 = sh | cmd_list | cmd3

    for i, data in enumerate(cmd4):
        assert data == test_list[i].upper()

    for i, data in enumerate(cmd5):
        assert data == test_list[i].upper()

    unregister_type(list)
    unregister_type(list)
    assert not has_registered_type(list)
