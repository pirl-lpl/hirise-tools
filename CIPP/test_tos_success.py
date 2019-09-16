#!/usr/bin/env python
"""This module has tests for the priority_rewrite functions."""

# Copyright 2019, Ross A. Beyer (rbeyer@seti.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0 #
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import patch, mock_open

import tos_success as ts


class TestFunctions(unittest.TestCase):

    def test_get_wths(self):
        m = mock_open(read_data='''1234, WTH priority, This, has, commas
567,
890''')
        with patch('tos_success.open', m):
            with patch('ptf.open', m):
                self.assertDictEqual({'1234': '1234, This, has, commas',
                                      '567': '567,',
                                      '890': '890'},
                                     ts.get_wths('dummy/path'))

    def test_find_suggestion(self):
        w = {'1234': '1234, This, has, commas',
             '567': '567,',
             '890': '890'}
        self.assertTrue('1234', ts.find_suggestion(w, '1234', 'H'))
        self.assertIsNone(ts.find_suggestion(w, '1234', 'X'))
        self.assertIsNone(ts.find_suggestion(w, '777', 'H'))
