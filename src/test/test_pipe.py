#!python

import sys
if '../' not in sys.path:
    sys.path.insert(0, '../')

from cmdlet.cmd import *

upper = pipe.map(string.upper)
lower = pipe.map(string.lower)

def test_pipe_ans():
    import string

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
