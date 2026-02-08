#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utils package - Re-export root utils functions to avoid import conflicts
"""

import sys
import os

# Import functions from root-level utils.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Load root utils.py module
from importlib.machinery import SourceFileLoader
_root_utils = SourceFileLoader('_root_utils', os.path.join(parent_dir, 'utils.py')).load_module()

# Re-export all functions
hexdump = _root_utils.hexdump
ascii_to_list = _root_utils.ascii_to_list
asciihex_to_list = _root_utils.asciihex_to_list
pad_asciihex = _root_utils.pad_asciihex
swap_nibbles = _root_utils.swap_nibbles
list_to_int = _root_utils.list_to_int
int_to_list = _root_utils.int_to_list
id_to_str = _root_utils.id_to_str

__all__ = [
    'hexdump',
    'ascii_to_list',
    'asciihex_to_list',
    'pad_asciihex',
    'swap_nibbles',
    'list_to_int',
    'int_to_list',
    'id_to_str',
]
