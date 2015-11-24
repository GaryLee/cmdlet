#!python
# coding: utf-8

import sys
if '../' not in sys.path:
    sys.path.insert(0, '../')

from cmdlet import *
from cmdlet.cmds import *

register_default_types()


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
