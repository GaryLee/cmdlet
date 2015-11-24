#!python
# coding: utf-8

def test_sh_input():
    import sys
    import platform
    from os import path
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    from cmdlet.cmds import *

    register_default_types()

    test_vector = ['this', 'is', 'a', 'shell', 'input', 'output', 'test', '!!']
    cmd=r'''python -c "from sys import stdout; [stdout.write('%%s\n' %% raw_input().upper()) for x in range(%d)]" ''' % len(test_vector)

    result_list = result(test_vector | sh(cmd))
    for i, item in enumerate(test_vector):
        assert item.upper() == result_list[i]

def test_sh_output():
    import sys
    import platform
    from os import path
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    from cmdlet.cmds import *

    register_default_types()

    if platform.system() == 'Windows':
        list_file_cmd = 'dir/b'
    else:
        list_file_cmd = '/bin/ls'

    file_list = result(list_file_cmd | wildcard('*.py') | strip | lower)
    assert path.basename(__file__).lower() in file_list

def test_sh_without_cmd():
    import sys
    import platform
    from os import path
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    from cmdlet.cmds import *
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
