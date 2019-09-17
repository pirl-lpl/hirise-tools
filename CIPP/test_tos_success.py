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

iof = '''C,2019-103T23:36:13.343,2.906,339.281,-3.559,1,59593a,59593a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Aram Chaos,9,C_59835359 X_48383682,422.185 0.000,59835359,IO,1.00,5/5,T-S,5Hz,10.6,2.139
XC,2019-103T23:36:13.343,2.906,339.281,-3.559,1,59593a,59593a,88.40,10.0,,,d:/ctx/ctx_itl45.nifl,X,1,1.88,,0,,Aram Chaos,9,C X C_59835359,1817.000,48383682,IO,1.70,1,,2,10.6,2.139
C,2019-103T23:44:32.030,29.663,336.087,-4.094,0,59593a,59593a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,MSP Coverage - (1-59593a),2,,422.185 0.000,59831995,IO,1.00,5/5,T-S,5Hz,10.6,0.000
H,2019-103T23:53:34.046,58.184,330.470,-3.752,3,59593a,59593a,30.00,321.0,,,N/A,X,,,,,,163582 Cratered mound in Acidalia Planitia Volcanic Processes PUB,799,,0.000,163582,IO-REQ-CTX,enable,,,0,10.6,4.114
E,2019-104T00:34:33.182,-8.038,145.005,-1.484,0,59594d,,634.00,348.0,08 50,,d:/ele/mro_relay_59594d.rel,X,019104014c,24.3,,,30_0_3 -57.5_east,RARANGE: (-24 3),,,1200.000,MRO_MSL_2019_104_01,MH-MEP,1.0,,,,,0.000
C,2019-104T01:12:17.946,-49.559,319.085,-2.114,1,59594a,59594a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Dust-raising event and streak monitoring in Argyre,6,C_59835375 X_106974484,422.185 0.000,59835375,IO,1.00,5/5,T-S,5Hz,10.6,1.573
XC,2019-104T01:12:17.946,-49.559,319.085,-2.114,1,59594a,59594a,13.45,10.0,,,d:/ctx/ctx_itl2.nifl,X,1955,1.88,,0,,Dust-raising event and streak monitoring in Argyre,6,C X C_59835375,276.500,106974484,IO,1.70,1,,0,10.6,1.573
H,2019-104T01:33:31.327,19.476,312.078,-4.305,4,59594a,59594a,30.00,321.0,,,N/A,X,,,0.582,,ESP_055321_1995:154996 r=-1 i=53 Ls=176 Prev=13d Next=316d URGENT,154998 Summit pit of Santa Fe Crater Geologic Contacts/Stratigraphy - urgent for stereo completion,14005,,0.000,154998,IO-REQ-CTX,enable,,,2,10.6,-21.075'''


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

    def test_get_suggestions(self):
        m = mock_open(read_data=iof)
        with patch('tos_success.open', m):
            with patch('ptf.open', m):
                self.assertEqual(['163582'],
                                 ts.get_suggestions('dummy/path',
                                                    ['163582', '890', '5']))
