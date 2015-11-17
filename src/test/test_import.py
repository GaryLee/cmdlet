#!python

def test_cmdlet_import():
    import sys
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    import_names = [
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

    from cmdlet import *
    for name in import_names:
        assert name in locals()

def test_cmd_import():
    import sys
    if '../' not in sys.path:
        sys.path.insert(0, '../')

    import_names = [
        'Pipe',
        'PipeFunction',
        'register_type',
        'unregister_type',
        'run',
        'result',
        'seq',
        'pair',
        'format',
        'stdout',
        'stderr',
        'sh'
    ]

    from cmdlet.cmds import *
    for name in import_names:
        assert name in locals()
