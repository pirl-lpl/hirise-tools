#!/usr/bin/env python
"""This module has tests for the PTF functions."""

# Copyright 2019, Ross A. Beyer (rbeyer@seti.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import patch, mock_open

import ptf

ptf_str = '''#FILE_TYPE: IPTF
#START_TIME: 2019-103T23:36:13.343
#STOP_TIME: 2019-117T22:19:32.551
#USERNAME: redfield
#SPK: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/spk_psp_rec59468_59462_60238_p-v1.mttbin
#SPK: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/de421.bsp
#CREATION_DATE: 2019-095T18:29:23
#SCLK_SCET: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/MRO_SCLKSCET.00081.65536.tsc
#ROLL_LIMITS: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/rl_325a_1_190414_ROLL_v2
#OPTG: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/optg_psp_rec59468_59462_60238_p-v1
#XZONE: /EXPORT/DATA/0.0-MRO-OPS/post/rm325/2play/iof/ez_325a_1_190414_v2.excl
##
# JMARS version:	Mon Oct 22 13:55:42 MST 2018
# Java version: 	1.5.0_16-b02
# OS version:   	Linux / amd64 / 2.6.32-358.el6.x86_64
C,2019-103T23:36:13.343,2.906,339.281,-3.559,1,59593a,59593a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Aram Chaos,9,C_59835359 X_48383682,422.185 0.000,59835359,IO,1.00,5/5,T-S,5Hz,10.6,2.139
XC,2019-103T23:36:13.343,2.906,339.281,-3.559,1,59593a,59593a,88.40,10.0,,,d:/ctx/ctx_itl45.nifl,X,1,1.88,,0,,Aram Chaos,9,C X C_59835359,1817.000,48383682,IO,1.70,1,,2,10.6,2.139
C,2019-103T23:44:32.030,29.663,336.087,-4.094,0,59593a,59593a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,MSP Coverage - (1-59593a),2,,422.185 0.000,59831995,IO,1.00,5/5,T-S,5Hz,10.6,0.000
H,2019-103T23:53:34.046,58.184,330.470,-3.752,3,59593a,59593a,30.00,321.0,,,N/A,X,,,,,,163582 Cratered mound in Acidalia Planitia Volcanic Processes PUB,799,,0.000,163582,IO-REQ-CTX,enable,,,0,10.6,4.114
E,2019-104T00:34:33.182,-8.038,145.005,-1.484,0,59594d,,634.00,348.0,08 50,,d:/ele/mro_relay_59594d.rel,X,019104014c,24.3,,,30_0_3 -57.5_east,RARANGE: (-24 3),,,1200.000,MRO_MSL_2019_104_01,MH-MEP,1.0,,,,,0.000
C,2019-104T01:12:17.946,-49.559,319.085,-2.114,1,59594a,59594a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Dust-raising event and streak monitoring in Argyre,6,C_59835375 X_106974484,422.185 0.000,59835375,IO,1.00,5/5,T-S,5Hz,10.6,1.573
XC,2019-104T01:12:17.946,-49.559,319.085,-2.114,1,59594a,59594a,13.45,10.0,,,d:/ctx/ctx_itl2.nifl,X,1955,1.88,,0,,Dust-raising event and streak monitoring in Argyre,6,C X C_59835375,276.500,106974484,IO,1.70,1,,0,10.6,1.573
H,2019-104T01:33:31.327,19.476,312.078,-4.305,4,59594a,59594a,30.00,321.0,,,N/A,X,,,0.582,,ESP_055321_1995:154996 r=-1 i=53 Ls=176 Prev=13d Next=316d URGENT,154998 Summit pit of Santa Fe Crater Geologic Contacts/Stratigraphy - urgent for stereo completion,14005,,0.000,154998,IO-REQ-CTX,enable,,,2,10.6,-21.075
O,2019-104T02:23:05.138,4.000,119.149,,0,59594d,59594d,563.00,0.0,,,,X,,,,,,MCS EZ MSL(night_west) orbit 59594d DOY 104 109 EL 3.05 1.07 DEQX 118.66,,,,,ATM-EZ,1.0,,,,10.6
C,2019-104T03:10:41.683,-29.482,288.644,4.115,1,59595a,59595a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Terrain west of Aniak Crater,9,C_59835353 X_106971887,422.185 0.000,59835353,IO,1.00,5/5,T-S,5Hz,10.6,2.834
XC,2019-104T03:10:41.683,-29.482,288.644,4.115,1,59595a,59595a,17.30,10.0,,,d:/ctx/ctx_itl4.nifl,X,1963,1.88,,0,,Terrain west of Aniak Crater,9,C X C_59835353,355.500,106971887,IO,1.70,1,,0,10.6,2.834
C,2019-104T03:17:03.952,-8.734,286.236,-4.393,0,59595a,59595a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,MSP Coverage - (1-59595a),2,,422.185 0.000,59832037,IO,1.00,5/5,T-S,5Hz,10.6,0.000
C,2019-104T05:22:09.101,32.945,254.036,2.656,1,59596a,59596a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - 162490 Dust Devil Track Monitoring Eolian Processes,856,C_59835013 H_162490,422.185 0.000,59835013,IO-REQ-CTX,1.00,5/5,T-S,5Hz,10.7,-3.984
HC,2019-104T05:22:09.101,32.945,254.036,2.656,3,59596a,59596a,30.00,321.0,,,N/A,X,,,,,,162490 Dust Devil Track Monitoring Eolian Processes,856,C C_59835013,0.000,162490,IO-REQ-CTX,enable,,,0,10.7,-3.984
C,2019-104T06:50:35.239,-43.942,235.665,3.099,1,59597a,59597a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Icaria Fossae,10,C_59835220 X_48383733,422.185 0.000,59835220,IO,1.00,5/5,T-S,5Hz,10.7,8.013
XC,2019-104T06:50:35.239,-43.942,235.665,3.099,1,59597a,59597a,24.98,10.0,,,d:/ctx/ctx_itl16.nifl,X,5108,1.88,,0,,Icaria Fossae,10,C X C_59835220,513.500,48383733,IO,1.70,1,,1,10.7,8.013
C,2019-104T07:06:22.201,7.373,229.695,1.317,0,59597a,59597a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,MSP Coverage - (1-59597a),2,,422.185 0.000,59832049,IO,1.00,5/5,T-S,5Hz,10.7,0.000
X,2019-104T08:46:10.151,-32.675,209.192,0.463,2,59598a,59598a,42.28,10.0,,,d:/ctx/ctx_itl8.nifl,X,5146,1.88,,0,,Crater south of the Sirenum Fossae,15,,869.000,48384572,IO,1.70,1,,1,10.8,-18.755
C,2019-104T10:31:58.450,-53.783,182.550,2.298,1,59599a,59599a,92.77,40.0,,,0,X,,84351.0,,15418,Type=FRS,olivine-rich crater wall in Terra Sirenum-54,3,H X,100.247 0.000,59833612,IO-REQ-CTX,1.00,1/1,T-S,5Hz,10.8,8.056
C,2019-104T10:57:09.330,27.851,173.118,-3.707,1,59599a,59599a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - 143258 Flow margin in Phlegra Dorsa region Volcanic Processes,14608,C_59835121 H_143258,422.185 0.000,59835121,IO-REQ-CTX,1.00,5/5,T-S,5Hz,10.8,-6.317
HC,2019-104T10:57:09.330,27.851,173.118,-3.707,3,59599a,59599a,30.00,321.0,,,N/A,X,,,0.059,,SPORC003:143256 r=8 i=38,143258 Flow margin in Phlegra Dorsa region Volcanic Processes,14608,X C_59835121,0.000,143258,IO-REQ-CTX,enable,,,2,10.8,-6.317
C,2019-104T12:25:51.885,-48.415,155.226,1.760,0,59600a,59600a,193.00,2.0,,,0,X,,0.0,,,Type=MSV,Gale Region Mapping Fill 180 - 59600a,5,,422.185 0.000,59676447,IO,1.00,5/5,T-S,5Hz,10.8,0.000
E,2019-104T12:40:53.133,0.147,146.881,-2.507,2,59600a,,572.00,348.0,08 50,,d:/ele/mro_relay_59600a.rel,X,019104034c,14.3,,,5_b_5 63.9_east,,,,1200.000,MRO_MSL_2019_104_03,MH-MEP,1.0,,,,,20.849
C,2019-104T14:21:45.077,-36.667,125.270,1.334,1,59601a,59601a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - 159560 Gully monitoring Mass Wasting Processes,11033,C_59833871 H_159560,422.185 0.000,59833871,IO-REQ-CTX,1.00,5/5,T-S,5Hz,10.9,8.648
HC,2019-104T14:21:45.077,-36.667,125.270,1.334,3,59601a,59601a,30.00,321.0,,,N/A,X,,,,3,,159560 Gully monitoring Mass Wasting Processes,11033,H C H_159560 C_59833871,0.000,159560,IO-REQ-CTX,enable,,,0,10.9,8.648
C,2019-104T14:32:47.694,-0.717,121.456,0.830,0,59601a,59601a,193.00,2.0,,,0,X,,0.0,,,Type=MSV,Gale Region Mapping Fill 180 - 59601a,5,,422.185 0.000,59677539,IO,1.00,5/5,T-S,5Hz,10.9,0.000
C,2019-104T14:35:47.849,8.997,120.273,-1.849,0,59601a,59601a,73.00,2.0,,,0,X,,0.0,,,Type=MSV,Gale Region Mapping Fill 60 - 59601a,5,,141.905 0.000,59677589,IO,1.00,5/5,T-S,5Hz,10.9,0.000
C,2019-104T14:57:13.953,76.748,104.099,-2.371,1,59601a,59601a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - 170772 Dunes dubbed Romo Seasonal Processes,11010,C_59834598 H_170772,422.185 0.000,59834598,IO-REQ-CTX,1.00,5/5,T-S,5Hz,10.9,0.055
HC,2019-104T14:57:13.953,76.748,104.099,-2.371,3,59601a,59601a,30.00,321.0,,,N/A,X,,,,1,Seasonal:,170772 Dunes dubbed Romo Seasonal Processes,11010,H C H_170772 C_59834598,0.000,170772,IO-REQ-CTX,enable,,,0,10.9,0.055
C,2019-104T16:11:55.936,-43.214,98.963,-0.375,1,59602a,59602a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - CTX stereo with F17_042499_1368_XN_43S261W,3,C_59835216 X_48383781,422.185 0.000,59835216,IO,1.00,5/5,T-S,5Hz,10.9,8.546
XC,2019-104T16:11:55.936,-43.214,98.963,-0.375,1,59602a,59602a,19.22,10.0,,,d:/ctx/ctx_itl22.nifl,X,5242,1.88,,0,,CTX stereo with F17_042499_1368_XN_43S261W,3,C X C_59835216,395.000,48383781,IO,1.70,1,,1,10.9,8.546'''


class TestVariables(unittest.TestCase):

    def test_header_order(self):
        ho = ('FILE_TYPE', 'START_TIME', 'STOP_TIME', 'USERNAME',
              'CREATION_DATE', 'SCLK_SCET', 'OPTG', 'ROLL_LIMITS',
              'SPK', 'XZONE')
        self.assertTupleEqual(ho, ptf.header_order)

    def test_fieldnames(self):
        fn = ('Instrument Set', 'Predict Time', 'Latitude', 'Longitude',
              'Elevation', 'Observation Type', 'Orbit Number',
              'Orbit Alternatives', 'Observation Duration',
              'Setup Duration', 'Orbital Data Table', 'Parameters Table',
              'Sequence Filename', 'Downlink Priority', 'Product ID',
              'Spare 1', 'Spare 2', 'Spare 3', 'Spare 4', 'Comment',
              'Request Priority', 'Coordinated Track History',
              'Raw Data Volume', 'Team Database ID',
              'Request Category', 'Compression', 'Pixel Scale',
              'Observation Mode', 'Ancillary Data', 'LsubS', 'Roll Angle')
        self.assertTupleEqual(fn, ptf.fieldnames)


class TestPTF(unittest.TestCase):

    def setUp(self):
        self.header = {'FILE_TYPE': 'HIRISE PTF',
                       'START_TIME': '2019-103T23:26:49.419',
                       'STOP_TIME': '2019-117T20:27:25.780'}
        self.comments = '''HiPlan version:   5.0.1.1
Java version:     1.8.0_162
OS version:       Mac OS X / x86_64 / 10.13.3

Instrument Set,Predict Time,Latitude,Longitude,Elevation,Observation Type,Orbit Number,Orbit Alternatives,Observation Duration,Setup Duration,Orbital Data Table,Parameters Table,Sequence Filename,Downlink Priority,Product ID,Spare 1,Spare 2,Spare 3,Spare 4,Comment,Request Priority,Coordinated Track History,Raw Data Volume,Team Database ID,Request Category,Compression,Pixel Scale,Observation Mode,Ancillary Data,Ls,Roll Angle
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
Instrument set,Predict time,Latitude,Longitude,Elevation,Observation type,Orbit number,Orbit alternatives,Observation duration,Setup duration,Orbital data table,Parameters table,Sequence filename,Downlink priority,Product ID,Spare 1,Spare 2,Spare 3,Spare 4,Comment,Request priority,Coordinated track history,Raw data volume,Team database ID,Request category,Compression,Pixel scale,Observation mode,Ancillary data,LsubS,Roll angle'''
        self.fieldnames = ['Instrument Set', 'Predict Time', 'Latitude', 'Longitude']
        self.records = [{'Instrument Set': 'H',
                         'Predict Time': '2019-109T03:06:32.050',
                         'Latitude': '18.169',
                         'Longitude': '336.125'},
                        {'Instrument Set': 'H',
                         'Predict Time': '2019-117T03:45:31.198',
                         'Latitude': '24.2',
                         'Longitude': '42.745'}]

    def test_init(self):
        two = ptf.PTF(self.header, self.records)
        self.assertEqual(str(self.header), str(two))

        three = ptf.PTF(self.header, self.fieldnames, self.records)
        self.assertEqual(2, len(three))

        four = ptf.PTF(self.header, self.comments, self.fieldnames, self.records)
        self.assertEqual(['FILE_TYPE', 'START_TIME', 'STOP_TIME'],
                         list(four.keys()))

        one = ptf.PTF(ptf_str)
        self.assertEqual(31, len(one))

        self.assertRaises(IndexError, ptf.PTF)


class TestFunctions(unittest.TestCase):

    def test_parse(self):
        self.assertRaises(ValueError, ptf.parse,
                          'This text does not have a valid PTF header.')

        ptf_str_no_header = '''#FILE_TYPE: IPTF
#START_TIME: 2019-103T23:36:13.343
#STOP_TIME: 2019-117T22:19:32.551
#USERNAME: Tester
##
# generic comments:	foo bar
H,2019-103T23:53:34.046,58.184,330.470,-3.752,3,59593a,59593a,30.00,321.0,,,N/A,X,,,,,,163582 Cratered mound in Acidalia Planitia Volcanic Processes PUB,799,,0.000,163582,IO-REQ-CTX,enable,,,0,10.6,4.114
C,2019-104T01:12:17.946,-49.559,319.085,-2.114,1,59594a,59594a,180.00,13.0,,,0,X,,0.0,,,Type=MSV,COORD Target - Dust-raising event and streak monitoring in Argyre,6,C_59835375 X_106974484,422.185 0.000,59835375,IO,1.00,5/5,T-S,5Hz,10.6,1.573
H,2019-104T01:33:31.327,19.476,312.078,-4.305,4,59594a,59594a,30.00,321.0,,,N/A,X,,,0.582,,ESP_055321_1995:154996 r=-1 i=53 Ls=176 Prev=13d Next=316d URGENT,154998 Summit pit of Santa Fe Crater Geologic Contacts/Stratigraphy - urgent for stereo completion,14005,,0.000,154998,IO-REQ-CTX,enable,,,2,10.6,-21.075'''

        (d, c, f, r) = ptf.parse(ptf_str_no_header)
        self.assertEquals(ptf.fieldnames, f)

    def test_load(self):
        loaded = ptf.loads(ptf_str)
        self.assertEqual(31, len(loaded))

        m = mock_open(read_data=ptf_str)
        with patch('ptf.open', m):
            loaded = ptf.load('path/to/ptf')
            self.assertEqual(31, len(loaded))

    def test_guess_encoding(self):
        m = mock_open(read_data='Regular text')
        with patch('ptf.open', m):
            self.assertIsNone(ptf.guess_encoding('path/to/some/file'))

        # I can't satisfactorily test this.  I *think* that the argument
        # provided to read_data is converted into a string, via str(), so
        # that the mocked open function is actually always returning a UTF
        # string, which means that I can't test for the exception this way.
        # The only way may be testing via an actual 'real' file.
        #
        # mo = mock_open(read_data='Latin-1 text'.encode(encoding='latin_1'))
        # with patch('ptf.open', mo):
        #     self.assertEqual('latin_1', ptf.guess_encoding('path/to/some/file'))

    def test_dump(self):
        p = ptf.loads(ptf_str)
        # print(p.dumps())
