#!python
# coding: utf-8

def test_cmdlet_import():
    import sys

    match_names = [
        'Pipe',
        'PipeFunction',
        'UnregisteredPipeType',
        'register_type',
        'unregister_type',
        'unregister_all_types',
        'has_registered_type',
        'get_item_creator',
        'cmds',
    ]

    import cmdlet
    import_names = dir(cmdlet)
    for name in match_names:
        assert name in import_names

def test_cmds_import():
    import sys
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    match_names = ['Pipe', 'PipeFunction', 'StringIO', 'count', 'enum',
        'fileobj', 'flatten', 'fmt', 'grep', 'items', 'match', 'pack',
        'pipe', 'register_default_types', 'register_type', 'result', 'run',
        'seq', 'sh', 'stderr', 'stdout', 'unregister_type', 'wildcard']

    import cmdlet.cmds as cmds
    import_names = dir(cmds)
    for name in match_names:
        assert name in import_names

