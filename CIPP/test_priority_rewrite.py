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

import collections
import io
import unittest
from unittest.mock import patch, mock_open

import priority_rewrite as pr


hitlist = '''Instrument Set,Predict Time,Latitude,Longitude,Elevation,Observation Type,Orbit Number,Orbit Alternatives,Observation Duration,Setup Duration,Orbital Data Table,Parameters Table,Sequence Filename,Downlink Priority,Product ID,Spare 1,Spare 2,Spare 3,Spare 4,Comment,Request Priority,Coordinated Track History,Raw Data Volume,Team Database ID,Request Category,Compression,Pixel Scale,Observation Mode,Ancillary Data,LsubS,Roll Angle,
H,2019-109T03:06:32.050,18.169,336.125,-3.547,3,59659a,59659a 59725a,30,321,,,N/A,X,,,,1,,164320 Oxia Planum ExoMars Landing Site Future Exploration/Landing Sites PUB,16500,,0,164320,MH-MEP-REQ-CTX,enable,,,0,13,-4.222,HiReport
H,2019-114T06:32:07.110,18.415,335.529,-3.663,4,59725a,59725a 59659a,30,321,,,N/A,X,,,,1,,169940 Oxia Planum ExoMars Landing Site Future Exploration/Landing Sites PUB,16300,,0,169940,MH-MEP-REQ-CTX,enable,,,0,15.5,-17.764,HiReport
H,2019-112T07:39:55.229,-4.734,298.577,-4.189,3,59700a,59700a 59766a,30,321,,,N/A,X,,,,1,Seasonal: ESP_043876_1755:118228,118256 Monitor slopes in Juventae Chasma Mass Wasting Processes,15000,C,,118256,IO-REQ-CTX,enable,,,0,14.6,7.786,HiReport
H,2019-110T07:00:21.207,-12.137,289.486,-4.349,3,59740a,59740a 59674a,30,321,,,N/A,X,,,,1,,160087 East Melas Chasm floor deposits Eolian Processes,15000,,,160087,IO-REQ-CTX,enable,,,0,13.6,5.138,HiReport'''


def my_mock_open(read_data):
    # For Python 3.6, we need to add the __iter__ and __next__
    # methods to the mock_open return, since those functions are
    # used by the csv.reader functions in the tests here.
    # Pyton 3.7 and higher implement these in mock_open.
    # If we ever don't need to test for 3.6, then this
    # function can be removed, and all occurrences of
    # my_mock_open() can be replaced with mock_open().
    m = mock_open(read_data=read_data)
    m.return_value.__iter__ = lambda self: self
    m.return_value.__next__ = lambda self: next(iter(self.readline, ''))
    return m


class TestFunctions(unittest.TestCase):

    def test_get_input(self):
        m = my_mock_open(read_data=hitlist)
        with patch('priority_rewrite.open', m):
            with patch('ptf.open', m):
                targets = pr.get_input('dummy/path/to/hitlist')
                self.assertEqual(4, len(targets))

    def test_dict_write(self):
        f = io.StringIO()
        fn = ('A', 'B')
        rows = ({'A': 1, 'B': 2}, {'A': 3, 'B': 4})
        pr.dict_write(f, fn, rows)
        self.assertIn('A,B', f.getvalue())

    def test_write_output(self):
        m = my_mock_open(read_data=hitlist)
        with patch('priority_rewrite.open', m):
            with patch('ptf.open', m):
                targets = pr.get_input('dummy/path/to/hitlist')
                out_str = pr.write_output(targets, targets)
                self.assertEqual(5, len(out_str.splitlines()))

    def test_make_reset_dict(self):
        c = collections.Counter({801: 4, 700: 2})
        self.assertDictEqual({600: 800, 1000: 900},
                             pr.make_reset_dict('600:800, 1000:900', c))
        self.assertRaises(KeyError, pr.make_reset_dict, '600:800, 1000:700', c)

    def test_sort_and_filter(self):
        i = [5, 3, 0, 4, 1, 2]
        self.assertListEqual([1, 2, 3, 4, 5], pr.sort_and_filter(i))
        self.assertListEqual([0, 1, 2, 3, 4, 5],
                             pr.sort_and_filter(i, keepzero=True))

    def test_get_records_for_this_priority(self):
        r = [{'Request Priority': 800, 'Name': 'One at priority 800'},
             {'Request Priority': 800, 'Name': 'Two at Priority 800'},
             {'Request Priority': 888, 'Name': 'Oddball'}]
        self.assertEqual(2, len(pr.get_records_for_this_priority(800,
                                                                 r, {1: 2, 3: 4})))
        self.assertEqual(1, len(pr.get_records_for_this_priority(800,
                                                                 r, {888: 800, 3: 4})))

    def test_is_enough_space(self):
        self.assertTrue(pr.is_enough_space(1, None, 500))
        self.assertTrue(pr.is_enough_space(10, 14, 4))
        self.assertFalse(pr.is_enough_space(10, 14, 5))

    def test_priority_rewrite(self):
        r = [{'Request Priority': 800, 'Name': 'One at priority 800',
              'Latitude': 40},
             {'Request Priority': 800, 'Name': 'Two at Priority 800',
              'Latitude': 30},
             {'Request Priority': 888, 'Name': 'Oddball',
              'Latitude': 25}]
        self.assertEqual(collections.OrderedDict([('Request Priority', 700),
                                                  ('Name', 'One at priority 800'),
                                                  ('Latitude', 40)]),
                         pr.priority_rewrite(r, '800:700')[0])
