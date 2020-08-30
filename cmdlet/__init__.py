#!python
# coding: utf-8

"""Cmdlet module provides a pipe-like mechanism to cascade commands.

A command could be function, list, generator, etc. The commands are cascaed by
'|' symbol. This module provides basic mechanism to cascade function and
generator to Pipe object. Check cmdlet.cmd module for its applications.

.. moduleauthor:: Gary Lee <garywlee@gmail.com>

"""

from __future__ import absolute_import
from .cmdlet import *
from . import cmds

__license__ = "MIT"
__author__ = "Gary Lee <garywlee@gmail.com>"
__version__ = "0.4.2"
__docformat__ = "reStructuredText"

__all__ = [
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
