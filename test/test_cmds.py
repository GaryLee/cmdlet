#!python
# coding: utf-8

import sys
import os
from cmdlet import *
from cmdlet.cmds import *

script_path = os.path.dirname(os.path.abspath(__file__))
test_file_location = os.path.join(script_path, 'zen_of_python.txt')

register_default_types()

zen_of_python = [
    r'''Beautiful is better than ugly.''',
    r'''Explicit is better than implicit.''',
    r'''Simple is better than complex.''',
    r'''Complex is better than complicated.''',
    r'''Flat is better than nested.''',
    r'''Sparse is better than dense.''',
    r'''Readability counts.''',
    r'''Special cases aren't special enough to break the rules.''',
    r'''Although practicality beats purity.''',
    r'''Errors should never pass silently.''',
    r'''Unless explicitly silenced.''',
    r'''In the face of ambiguity, refuse the temptation to guess.''',
    r'''There should be one-- and preferably only one --obvious way to do it.''',
    r'''Although that way may not be obvious at first unless you're Dutch.''',
    r'''Now is better than never.''',
    r'''Although never is often better than *right* now.''',
    r'''If the implementation is hard to explain, it's a bad idea.''',
    r'''If the implementation is easy to explain, it may be a good idea.''',
    r'''Namespaces are one honking great idea -- let's do more of those!''',
]

def test_items_cmd():
    key_num = 100
    test_dict = {}
    for i in range(key_num):
        if i % 2:
            test_dict['I%d' % i] = 'VALUE%d' % i
        else:
            test_dict['i%d' % i] = 'value%d' % i

    cmd = items(test_dict)
    count = 0
    for item in cmd:
        assert test_dict[item[0]] == item[1]
        count += 1
    assert count == key_num


def test_attr_cmd():

    class TestClass(object):
        _attr_num = 5
        def __init__(self):
            for i in range(self._attr_num):
                if i % 2:
                    setattr(self, 'ATTR%d' % i, 'VALUE%d' % i)
                else:
                    setattr(self, 'attr%d' % i, 'value%d' % i)

    object_num = 100
    object_list = [TestClass() for i in range(object_num)]

    cmd = object_list | attr('attr0')
    count = 0
    for value in cmd:
        assert value == 'value0'
        count += 1
    assert count == object_num

    cmd = object_list | attrs(['attr0', 'ATTR1', 'attr2', 'ATTR3', 'attr4'])
    count = 0
    for values in cmd:
        assert values[0] == 'value0'
        assert values[1] == 'VALUE1'
        assert values[2] == 'value2'
        assert values[3] == 'VALUE3'
        assert values[4] == 'value4'
        count += 1

    attr_value_dict = dict(attr0=None, ATTR1=None, attr2=None, ATTR3=None, attr4=None, nonExistAttr=None)
    cmd = object_list | attrdict(attr_value_dict)
    count = 0
    for valuedict in cmd:
        assert valuedict['attr0'] == 'value0'
        assert valuedict['ATTR1'] == 'VALUE1'
        assert valuedict['attr2'] == 'value2'
        assert valuedict['ATTR3'] == 'VALUE3'
        assert valuedict['attr4'] == 'value4'
        count += 1
    assert count == object_num

    attr_values = ['attr0', 'ATTR1', 'attr2', 'ATTR3', 'attr4']
    cmd = object_list | attrdict(attr_values)
    count = 0
    for valuedict in cmd:
        assert valuedict['attr0'] == 'value0'
        assert valuedict['ATTR1'] == 'VALUE1'
        assert valuedict['attr2'] == 'value2'
        assert valuedict['ATTR3'] == 'VALUE3'
        assert valuedict['attr4'] == 'value4'
        count += 1
    assert count == object_num


def test_flatten_cmd():
    test_vector1 = [
        0,1,(2,3,[4,5,[6, ],7],8),9,
        [10,11,(12,[13,(14, )],15,[16,(17,[18, ])]),19],20,
        21,[22,[23,[24,[25,[26,[27,28]]]]]],29
        ]

    cmd = test_vector1 | flatten
    for i,v in enumerate(cmd):
        assert i == v

    test_vector2 = [
        0,[1,[2,[3,[4,[5,[6,[7,[8,[9,[10]]]]]]]]]]
        ]

    cmd = test_vector2 | flatten(3)
    for i,v in enumerate(cmd):
        if i <= 3:
            assert i == v
        else:
            assert v == [4, [5, [6, [7, [8, [9, [10]]]]]]]


def test_values_cmd():
    test_vector = [dict(item_i='I%d'%i, item_j='j%d'%(i*10), item_k=i*100) for i in range(20)]

    cmd1 = test_vector | values('item_j', 'item_i', 'item_k')
    for i, v in enumerate(cmd1):
        assert v[1] == ('I%d' % i)
        assert v[0] == ('j%d' % (i*10))
        assert v[2] == (i*100)

    test_vector = [['I%d'%i, 'j%d'%(i*10), i*100] for i in range(20)]
    cmd2 = test_vector | values(0, 1, 2)
    for i, v in enumerate(cmd2):
        assert v[0] == ('I%d' % i)
        assert v[1] == ('j%d' % (i*10))
        assert v[2] == (i*100)

    cmd3 = test_vector | values(2, 1)
    for i, v in enumerate(cmd3):
        assert v[0] == (i*100)
        assert v[1] == ('j%d' % (i*10))

    test_vector = [('I%d'%i, 'j%d'%(i*10), i*100) for i in range(20)]
    cmd4 = test_vector | values(0, 1, 2)
    for i, v in enumerate(cmd4):
        assert v[0] == ('I%d' % i)
        assert v[1] == ('j%d' % (i*10))
        assert v[2] == (i*100)

    cmd5 = test_vector | values(2, 1)
    for i, v in enumerate(cmd5):
        assert v[0] == (i*100)
        assert v[1] == ('j%d' % (i*10))


def test_counter_cmd():
    cmd = range(10) | counter
    assert cmd.run() == 10


def test_enum_cmd():
    test_num = 100
    test_vector = ['item%d' % i for i in range(test_num)]
    cmd1 = test_vector | enum
    for i, v in enumerate(cmd1):
        assert i == v[0] and v[1] == ('item%d' % i)

    cmd2 = test_vector | enum(start=10)
    for i, v in enumerate(cmd2, start=10):
        assert i == v[0] and v[1] == ('item%d' % (i-10))


def test_pack_cmd():
    test_vector = list(range(1, 8))
    cmd1 = test_vector | pack(3)
    assert result(cmd1) == [[1,2,3], [4,5,6]]
    cmd2 = test_vector | pack(3, rest=True)
    assert result(cmd2) == [[1,2,3], [4,5,6], [7]]
    cmd3 = test_vector | pack(3, rest=True, padding=-1)
    assert result(cmd3) == [[1,2,3], [4,5,6], [7,-1,-1]]


def test_grep_cmd():
    zen_of_python_uppercase = list(map(str.upper, zen_of_python))

    def grep_and_merge(pattern, texts, inv=False):
        results = []
        for text in texts:
            match = pattern.match(text)
            if (not inv and match) or (inv and not match):
                results.append(text)
        return '\n'.join(results)

    cmd1 = zen_of_python | grep(r'.*\s+is better than\s+.*')
    grep_result = '\n'.join(cmd1.result())
    assert grep_result == grep_and_merge(re.compile(r'.*\s+is better than\s+.*'), zen_of_python)

    cmd2 = zen_of_python | grep(r'.*\s+is better than\s+.*', inv=True)
    grep_result = '\n'.join(cmd2.result())
    assert grep_result == grep_and_merge(re.compile(r'.*\s+is better than\s+.*'), zen_of_python, inv=True)

    cmd3 = zen_of_python_uppercase | grep(r'.*\s+is better than\s+.*', flags=re.I)
    grep_result = '\n'.join(cmd3.result())
    target_result = grep_and_merge(re.compile(r'.*\s+is better than\s+.*'), zen_of_python)
    target_result = target_result.upper()
    assert grep_result == target_result

    cmd4 = zen_of_python_uppercase | grep(r'.*\s+is better than\s+.*', inv=True, flags=re.I)
    grep_result = '\n'.join(cmd4.result())
    target_result = grep_and_merge(re.compile(r'.*\s+is better than\s+.*'), zen_of_python, inv=True)
    target_result = target_result.upper()
    assert grep_result == target_result


def test_match_cmd():
    test_vector = [
        r'''name=Gary, gender=man, age=30''',
        r'''name=Mary, gender=woman, age=35''',
        r'''name=Tom, gender=man, age=55''',
        r'''name=Jack, gender=man, age=34''',
        r'''name=Kate, gender=woman, age=30''',
        r'''name=Carly, gender=woman, age=25''',
    ]
    test_vector_upper = list(map(str.upper, test_vector))

    pattern = r'''name=(?P<name>\w+)\s*,\s*gender=(?P<gender>\w+)\s*,\s*age=(?P<age>\d+).*'''
    i = 0
    cmd1 = test_vector | match(pattern, to=dict)
    for i, items in enumerate(cmd1):
        target = test_vector[i]
        match_result = '''name=%s, gender=%s, age=%s''' % (items['name'], items['gender'], items['age'])
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd1_upper = test_vector_upper | match(pattern, to=dict, flags=re.I)
    for i, items in enumerate(cmd1_upper):
        target = test_vector[i].upper()
        match_result = '''NAME=%s, GENDER=%s, AGE=%s''' % (items['name'], items['gender'], items['age'])
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd2 = test_vector | match(pattern, to=list)
    for i, items in enumerate(cmd2):
        target = test_vector[i]
        match_result = '''name=%s, gender=%s, age=%s''' % (items[0], items[1], items[2])
        assert type(items) == list
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd2_upper = test_vector_upper | match(pattern, to=list, flags=re.I)
    for i, items in enumerate(cmd2_upper):
        target = test_vector[i].upper()
        match_result = '''NAME=%s, GENDER=%s, AGE=%s''' % (items[0], items[1], items[2])
        assert type(items) == list
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd3 = test_vector | match(pattern, to=tuple)
    for i, items in enumerate(cmd3):
        target = test_vector[i]
        match_result = '''name=%s, gender=%s, age=%s''' % (items[0], items[1], items[2])
        assert type(items) == tuple
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd3_upper = test_vector_upper | match(pattern, to=tuple, flags=re.I)
    for i, items in enumerate(cmd3_upper):
        target = test_vector[i].upper()
        match_result = '''NAME=%s, GENDER=%s, AGE=%s''' % (items[0], items[1], items[2])
        assert type(items) == tuple
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd4 = test_vector | match(pattern)
    for i, items in enumerate(cmd4):
        target = test_vector[i]
        match_result = '''name=%s, gender=%s, age=%s''' % (items.group(1), items.group(2), items.group(3))
        assert target == match_result
    assert i == len(test_vector) - 1

    i = 0
    cmd4_upper = test_vector_upper | match(pattern, flags=re.I)
    for i, items in enumerate(cmd4_upper):
        target = test_vector[i].upper()
        match_result = '''NAME=%s, GENDER=%s, AGE=%s''' % (items.group(1), items.group(2), items.group(3))
        assert target == match_result
    assert i == len(test_vector) - 1

def test_resplit_cmd():
    test_vector = [
        r'''name=Gary  and gender=man   and age=30''',
        r'''name=Mary  and gender=woman and age=35''',
        r'''name=Tom   and gender=man   and age=55''',
        r'''name=Jack  and gender=man   and age=34''',
        r'''name=Kate  and gender=woman and age=30''',
        r'''name=Carly and gender=woman and age=25''',
    ]

    sep = r'\s+and\s+'
    cmd1 = test_vector | resplit(sep)
    i = 0
    for i, tokes in enumerate(cmd1):
        items = re.split(sep, test_vector[i])
        assert items == tokes
    assert i == len(test_vector) - 1

    cmd2 = test_vector | resplit(sep, maxsplit=1)
    i = 0
    for i, tokes in enumerate(cmd2):
        items = re.split(sep, test_vector[i], maxsplit=1)
        assert items == tokes
    assert i == len(test_vector) - 1

    test_vector2 = list(map(lambda s: s.replace('and', 'AND'), test_vector))
    cmd3 = test_vector2 | resplit(sep, flags=re.I)
    i = 0
    for i, tokes in enumerate(cmd3):
        items = re.split(sep, test_vector2[i], flags=re.I)
        assert items == tokes
    assert i == len(test_vector2) - 1

def test_sub_cmd():
    test_vector = [
        r'''name=Gary  and gender=man   and age=30''',
        r'''name=Mary  and gender=woman and age=35''',
        r'''name=Tom   and gender=man   and age=55''',
        r'''name=Jack  and gender=man   and age=34''',
        r'''name=Kate  and gender=woman and age=30''',
        r'''name=Carly and gender=woman and age=25''',
    ]

    pattern = r'\s+and\s+'
    repl = ', '
    cmd1 = test_vector | sub(pattern, repl)
    i = 0
    for i, s in enumerate(cmd1):
        target = re.sub(pattern, repl, test_vector[i])
        assert s == target
    assert i == len(test_vector) - 1

    test_vector2 = list(map(lambda s: s.replace('and', 'AND'), test_vector))
    cmd2 = test_vector2 | sub(pattern, repl, flags=re.I)
    i = 0
    for i, s in enumerate(cmd2):
        target = re.sub(pattern, repl, test_vector[i])
        assert s == target
    assert i == len(test_vector) - 1

    cmd3 = test_vector | sub(pattern, repl, count=1)
    i = 0
    for i, s in enumerate(cmd3):
        target = re.sub(pattern, repl, test_vector[i], count=1)
        assert s == target
    assert i == len(test_vector) - 1

def test_subn_cmd():
    test_vector = [
        r'''name=Gary  and gender=man   and age=30''',
        r'''name=Mary  and gender=woman and age=35''',
        r'''name=Tom   and gender=man   and age=55''',
        r'''name=Jack  and gender=man   and age=34''',
        r'''name=Kate  and gender=woman and age=30''',
        r'''name=Carly and gender=woman and age=25''',
    ]

    pattern = r'\s+and\s+'
    repl = ', '
    cmd1 = test_vector | subn(pattern, repl)
    i = 0
    for i, s in enumerate(cmd1):
        target = re.subn(pattern, repl, test_vector[i])
        assert s == target
    assert i == len(test_vector) - 1

    test_vector2 = list(map(lambda s: s.replace('and', 'AND'), test_vector))
    cmd2 = test_vector2 | subn(pattern, repl, flags=re.I)
    i = 0
    for i, s in enumerate(cmd2):
        target = re.subn(pattern, repl, test_vector[i])
        assert s == target
    assert i == len(test_vector) - 1

    cmd3 = test_vector | subn(pattern, repl, count=1)
    i = 0
    for i, s in enumerate(cmd3):
        target = re.subn(pattern, repl, test_vector[i], count=1)
        assert s == target
    assert i == len(test_vector) - 1


def test_wildcard_cmd():
    import fnmatch
    test_vector = [
        r'''name=Gary  and gender=man   and age=30''',
        r'''name=Mary  and gender=woman and age=35''',
        r'''name=Tom   and gender=man   and age=55''',
        r'''name=Jack  and gender=man   and age=34''',
        r'''name=Kate  and gender=woman and age=30''',
        r'''name=Carly and gender=woman and age=25''',
    ]

    pattern = '*gender=man*'
    pattern_obj = re.compile(fnmatch.translate(pattern))

    cmd1 = test_vector | wildcard(pattern)
    i = 0
    for i, s in enumerate(cmd1, 1):
        assert pattern_obj.match(s) is not None
    assert i == 3

    cmd2 = test_vector | wildcard(pattern, inv=True)
    i = 0
    for i, s in enumerate(cmd2, 1):
        assert pattern_obj.match(s) is None
    assert i == 3


def test_stdout_cmd():
    cmd1 = zen_of_python | stdout(thru=True)
    results = cmd1.result()
    assert results == zen_of_python

    cmd2 = zen_of_python | stdout(endl='\n', thru=True)
    results = cmd2.result()
    assert results == zen_of_python

    cmd3 = zen_of_python | stdout
    results = cmd3.result()
    assert results == []


def test_stderr_cmd():
    cmd1 = zen_of_python | stderr(thru=True)
    results = cmd1.result()
    assert results == zen_of_python

    cmd2 = zen_of_python | stderr(endl='\n', thru=True)
    results = cmd2.result()
    assert results == zen_of_python

    cmd3 = zen_of_python | stderr
    results = cmd3.result()
    assert results == []


def test_readline_cmd():
    files = [test_file_location, ]

    cmd1 = files | readline
    for i, v in enumerate(cmd1):
        assert v.strip() == zen_of_python[i]

    fd_list = list(map(lambda f: open(f, 'r'), files))
    cmd2 = fd_list | readline(trim=str.strip, start=2, end=5)
    i = 0
    for i, v in enumerate(cmd2, 2-1):
        assert v == zen_of_python[i]
    map(lambda x: x.close(), fd_list)
    assert i == 4

    cmd3 = readline | stdout
    try:
        cmd3.run()
    except Exception as e:
        assert e.args[0] == 'No input available for readline.'

    cmd4 = readline(test_file_location) | strip | upper
    for i, v in enumerate(cmd4):
        assert zen_of_python[i].upper() == v

    cmd5 = readline([test_file_location, test_file_location]) | strip | upper
    for i, v in enumerate(cmd5):
        if i < len(zen_of_python):
            assert zen_of_python[i].upper() == v
        else:
            assert zen_of_python[i-len(zen_of_python)].upper() == v


def test_walk_cmd():
    cmd1 = walk('.') | upper
    files = set(cmd1.result())
    files_target = set()
    for dir_path, dir_names, filenames in os.walk('.'):
        for filename in filenames:
            files_target.add(os.path.join(dir_path, filename).upper())
    assert files == files_target


def test_join_cmd():
    test_vector = 'item1 item2 item3 item4 item5'.split(' ')
    cmd1 = test_vector | join('-')
    assert cmd1.run() == 'item1-item2-item3-item4-item5'


def test_fileobj_cmd():
    from os import path, remove

    cmd1 = open(test_file_location) | rstrip | lstrip | upper
    for i, v in enumerate(cmd1):
        assert v == zen_of_python[i].upper()

    if path.exists('zen_of_python-out.txt'):
        os.remove('zen_of_python-out.txt')

    assert not path.exists('zen_of_python-out.txt')

    cmd1 = seq(zen_of_python) | upper | fileobj(open('zen_of_python-out.txt', 'w'), thru=True)
    i = 0
    for i, v in enumerate(cmd1):
        assert zen_of_python[i].upper() == v
    assert i == len(zen_of_python) - 1

def test_substitute_cmd():
    test_vector = [
        {'name': 'Gary',  'gender': 'man',   'age': 30},
        {'name': 'Mary',  'gender': 'woman', 'age': 35},
        {'name': 'Tom',   'gender': 'man',   'age': 55},
        {'name': 'Jack',  'gender': 'man',   'age': 34},
        {'name': 'Kate',  'gender': 'woman', 'age': 30},
        {'name': 'Carly', 'gender': 'woman', 'age': 25},
    ]

    template = string.Template('name=$name, age=$age')
    cmd1 = seq(test_vector) | substitute('name=$name, age=$age')
    i = 0
    for i, v in enumerate(cmd1):
        assert template.substitute(test_vector[i]) == v
    assert i == len(test_vector) - 1

    cmd2 = seq(test_vector) | substitute('name=$name, gender=$sex, age=$age')
    hasKeyError = False
    try:
        ans = cmd2.result()
    except KeyError as e:
        hasKeyError = True

    assert hasKeyError

def test_safe_substitute_cmd():
    test_vector = [
        {'name': 'Gary',  'gender': 'man',   'age': 30},
        {'name': 'Mary',  'gender': 'woman', 'age': 35},
        {'name': 'Tom',   'gender': 'man',   'age': 55},
        {'name': 'Jack',  'gender': 'man',   'age': 34},
        {'name': 'Kate',  'gender': 'woman', 'age': 30},
        {'name': 'Carly', 'gender': 'woman', 'age': 25},
    ]

    template = string.Template('name=$name, age=$age; $comment')
    cmd1 = seq(test_vector) | safe_substitute('name=$name, age=$age; $comment')
    i = 0
    for i, v in enumerate(cmd1):
        assert template.safe_substitute(test_vector[i]) == v
    assert i == len(test_vector) - 1

def test_to_str_cmd():
    cmd1 = zen_of_python | to_str(encoding='utf-8')
    for i, v in enumerate(cmd1):
        assert v == zen_of_python[i].encode('utf-8')

    cmd2 = zen_of_python | to_str
    for i, v in enumerate(cmd2):
        assert v == zen_of_python[i].encode('utf-8').decode('utf-8')
