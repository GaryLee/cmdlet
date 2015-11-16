#!python

import sys
if '../' not in sys.path:
    sys.path.insert(0, '../')

from cmdlet import *
from cmdlet.cmd import *

upper = pipe.map(string.upper)
lower = pipe.map(string.lower)

def test_pipe_ans():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = format('fOo%d') | upper
    cmd_lower = lower | format('%sBaR')

    cmd1 = range(test_num) | cmd_upper
    ans = cmd1.run()
    assert ans == ('FOO%d' % (test_num-1))

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    ans = cmd2.run()
    assert ans == ('foo%dBaR' % (test_num-1))


def test_pipe_result():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = format('fOo%d') | upper
    cmd_lower = lower | format('%sBaR')

    cmd1 = range(test_num) | cmd_upper
    for i, data in enumerate(cmd1.result()):
        assert data == ('FOO%d' % i)

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    for i, data in enumerate(cmd2.result()):
        assert data == ('foo%dBaR' % i)


def test_pipe_iter():
    import string

    register_default_types()
    test_num = 100

    cmd_upper = format('fOo%d') | upper
    cmd_lower = lower | format('%sBaR')

    cmd1 = range(test_num) | cmd_upper
    for i, data in enumerate(cmd1):
        assert data == ('FOO%d' % i)

    cmd2 = range(test_num) | cmd_upper | cmd_lower
    for i, data in enumerate(cmd2):
        assert data == ('foo%dBaR' % i)

    for i, data in enumerate(cmd1.iter()):
        assert data == ('FOO%d' % i)

    for i, data in enumerate(cmd2.iter()):
        assert data == ('foo%dBaR' % i)


def test_pipe_map():
    import string
    register_default_types()

    test_num = 100
    test_list = list(range(test_num))
    upper = pipe.map(string.upper)
    cmd1 = seq(test_list) | str | upper
    for i, data in enumerate(cmd1):
        assert str(i).upper() == data

    cmd2 = upper | str
    try:
        cmd2.run()
    except TypeError as e:
        assert e.message == 'A mapper must have input.'


def test_pipe_filter():
    import string
    register_default_types()

    test_num = 100
    test_list = list(range(test_num))
    upper = pipe.map(string.upper)
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
        assert e.message == 'A filter must have input.'


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
    cmd2 = test_list | count_mod_10(0)

    ans = cmd2.run()
    assert ans == (test_num // 10)

    cmd3 = count_mod_10 | str
    try:
        cmd3.run()
    except TypeError as e:
        assert e.message == 'A reducer must have input.'

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
