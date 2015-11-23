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
