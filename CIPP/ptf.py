#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import collections.abc
import csv
import io
import os

header_order = ('FILE_TYPE', 'START_TIME', 'STOP_TIME', 'USERNAME',
                'CREATION_DATE', 'SCLK_SCET', 'OPTG', 'ROLL_LIMITS',
                'SPK',
                'XZONE')

fieldnames = ('Instrument Set', 'Predict Time', 'Latitude', 'Longitude',
              'Elevation', 'Observation Type', 'Orbit Number',
              'Orbit Alternatives', 'Observation Duration',
              'Setup Duration', 'Orbital Data Table', 'Parameters Table',
              'Sequence Filename', 'Downlink Priority', 'Product ID',
              'Spare 1', 'Spare 2', 'Spare 3', 'Spare 4', 'Comment',
              'Request Priority', 'Coordinated Track History',
              'Raw Data Volume', 'Team Database ID',
              'Request Category', 'Compression', 'Pixel Scale',
              'Observation Mode', 'Ancillary Data', 'LsubS', 'Roll Angle')


class PTF(collections.abc.Sequence):
    """Represents a Payload Target File's (PTF's) data as a list of dicts.

       The resulting ptf object primarily behaves like a list, where
       that list represents the rows of the ptf file.  Each of those
       rows is a ``dict`` which contains the elements of each row,
       referenced by their column names.

       The ptf object also has some dictionary-like capabilities, in
       order to get at the values listed in the ptf in the commented
       section before the records.
    """

    def __init__(self, *args):
        self.dictionary = dict()
        self.comments = None
        self.fieldnames = list()
        self.ptf_recs = list()
        if len(args) == 1:
            (self.dictionary,
             self.comments,
             self.fieldnames,
             self.ptf_recs) = self.parse(args[0])
        elif len(args) == 2:
            self.dictionary = dict(args[0])
            self.fieldnames = header_order
            self.ptf_recs = list(args[1])
        elif len(args) == 3:
            self.dictionary = dict(args[0])
            self.fieldnames = list(args[1])
            self.ptf_recs = list(args[2])
        elif len(args) == 4:
            self.dictionary = dict(args[0])
            self.comments = str(args[1])
            self.fieldnames = list(args[2])
            self.ptf_recs = list(args[3])
        else:
            IndexError('accepts 1 to 4 arguments')

    def __str__(self):
        return(str(self.dictionary))

    # def __repr__(self):
    #     return (f'{self.__class__.__name__}(\'{self.histfile}\')')

    def __len__(self):
        return len(self.ptf_recs)

    def __getitem__(self, key):
        try:
            return self.dictionary[key]
        except KeyError:
            return self.ptf_recs[key]

    def __setitem__(self, key, value):
        self.dictionary[key] = value
        return

    def __iter__(self):
        return self.ptf_recs.__iter__()

    def __contains__(self, item):
        if item in self.dictionary:
            return True
        else:
            return(item in self.ptf_recs)

    def keys(self):
        '''Gets the keys from the initial portion of the ptf file.

           These will be items like 'FILE_TYPE', 'START_TIME', 'ROLL_LIMITS', etc.
        '''
        return self.dictionary.keys()

    def values(self):
        '''Gets the values from the initial portion of the ptf file.'''
        return self.dictionary.values()

    @staticmethod
    def parse(ptf_str: str) -> tuple:
        '''Takes a string, and parses the output.

           A three-element namedtuple is returned: the first element
           is a *dictionary* of the name:value information at the
           top of the file, the second element is a *list* of the
           of the fields that decorate the top of the ptf rows, and
           the third element is a *list* of collections.OrderedDict
           that represent each row of the ptf records.

           The contents of a PTF file look like this::

            # FILE_TYPE: HIRISE PTF
            # START_TIME: 2019-103T23:26:49.419
            # STOP_TIME: 2019-117T20:27:25.780
            # USERNAME: kblock
            # CREATION_DATE: 2019-088T02:30:37.716
            # SCLK_SCET:
            # OPTG:
            # ROLL_LIMITS:
            # SPK:
            # SPK:
            ##
            # PTF_Viewer:       org.uahirise.hirise.plan.ptf.PTF_Viewer (1.69 2015/06/11 00:10:03)
            # HiPlan version:   5.0.1.1
            # Java version:     1.8.0_162
            # OS version:       Mac OS X / x86_64 / 10.13.3
            #
            # Instrument Set,Predict Time,Latitude,Longitude,Elevation,Observation Type,Orbit Number,Orbit Alternatives,Observation Duration,Setup Duration,Orbital Data Table,Parameters Table,Sequence Filename,Downlink Priority,Product ID,Spare 1,Spare 2,Spare 3,Spare 4,Comment,Request Priority,Coordinated Track History,Raw Data Volume,Team Database ID,Request Category,Compression,Pixel Scale,Observation Mode,Ancillary Data,Ls,Roll Angle
            # 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
            # Instrument set,Predict time,Latitude,Longitude,Elevation,Observation type,Orbit number,Orbit alternatives,Observation duration,Setup duration,Orbital data table,Parameters table,Sequence filename,Downlink priority,Product ID,Spare 1,Spare 2,Spare 3,Spare 4,Comment,Request priority,Coordinated track history,Raw data volume,Team database ID,Request category,Compression,Pixel scale,Observation mode,Ancillary data,LsubS,Roll angle
            H,2019-109T03:06:32.050,18.169,336.125,-3.547,3,59659a,59659a 59725a,30.00,321.0,,,N/A,X,,,,1,,164320 Oxia Planum ExoMars Landing Site Future Exploration/Landing Sites PUB,16500,,0.000,164320,MH-MEP-REQ-CTX,enable,,,0,13.0,-4.222
            [... more comma-separated lines like above ...]

           But this function sees it like this::

                # k: v
                # k: v
                # k: v
                [... other lines like this ...]
                # k: v
                # k: v
                ##
                # comments
                # comments
                #
                # x,x,x,x,x
                # x,x,x,x,x
                # h,h,h,h,h
                n,n,n,n,n
                [... more comma-separated lines like above ...]

           Where each of the letters above is a string value that the parser
           reads.

           First, it takes all of the ``k`` and ``v`` elements and saves them
           as the keys and values in the returned dictionary.

           Anything below the ``##`` line, but that isn't the ``h`` or ``x``
           elements are put into a comments string.

           Second, the ``h`` elements are returned as the list of
           fieldnames.

           It ignores the two lines of ``x`` elements, as they're redundant.

           Third, it reads the lines with ``n`` and stores each row as a
           dictionary whose keys are the ``h`` values and whose values are
           the ``n`` values.
        '''
        d = dict().fromkeys(header_order)
        d['SPK'] = list()
        c = ''
        fieldnames = []
        ptf_rows = []
        lines = collections.deque(ptf_str.splitlines())
        ft = lines.popleft().lstrip('#').strip()
        if ft.startswith('FILE_TYPE:'):
            (k, v) = ft.split(':')
            d[k] = v.strip()
        else:
            raise ValueError('This file does not start with FILE_TYPE.')
        line = lines.popleft()
        while not line.startswith('##'):
            if line.startswith('#'):
                (k, v) = line.split(':', maxsplit=1)
                if k.lstrip('#').strip() == 'SPK' and v.strip():
                    d['SPK'].append(v.strip())
                else:
                    d[k.lstrip('#').strip()] = v.strip()
            else:
                raise ValueError('Insufficient header elements for a PTF.')
            line = lines.popleft()

        line = lines.popleft()
        while line.startswith('#'):
            c += line.lstrip('#').strip() + '\n'
            line = lines.popleft()
        lines.appendleft(line)

        my_fieldnames = None
        for comment_line in c.splitlines():
            if fieldnames[0] in comment_line:
                my_fieldnames = comment_line.split(',')

        if my_fieldnames is None:
            my_fieldnames = fieldnames

        reader = csv.DictReader(lines, fieldnames=my_fieldnames)

        for row in reader:
            ptf_rows.append(row)

        return(d, c, my_fieldnames, ptf_rows)

    def dumps(self) -> str:
        s = io.StringIO()
        return(self._dump_it(s).getvalue())

    def dump(self, p: os.PathLike) -> None:
        with open(p, mode='w') as f:
            f.write(self.dumps())

    def _dump_it(self, f: io.TextIOBase) -> io.TextIOBase:
        for k in header_order[:-2]:
            f.write('# {}: {}\n'.format(k, self[k]))
        if len(self['SPK']) > 0:
            for spk in self['SPK']:
                f.write(f'# SPK: {spk}\n')
        else:
            f.write(f'# SPK:\n')
        if self['XZONE'] is not None:
            f.write('# XZONE: {}\n'.format(self['XZONE']))
        f.write('##\n')
        f.write('# Written by a Python PTF class, suspicious.\n#\n')
        if self.comments:
            c = self.comments.splitlines()
            for line in c:
                f.write('# ' + line + '\n')
            f.write('#\n')
        f.write('# ' + ','.join(list(map(lambda x: x.title(), self.fieldnames))) + '\n')
        f.write('# ' + ','.join(map(str, list(range(1, len(self.fieldnames) + 1)))) + '\n')
        f.write('# ' + ','.join(list(map(lambda x: x.capitalize(), self.fieldnames))) + '\n')
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                extrasaction='ignore',
                                restval='')
        for record in self.ptf_recs:
            writer.writerow(record)
        return f


def loads(ptf_str: str) -> PTF:
    return PTF(ptf_str)


def load(ptf_path: os.PathLike) -> PTF:
    with open(ptf_path, 'r',
              encoding=guess_encoding(f)) as f:
        ptf_str = f.read()

    return loads(ptf_str)


def guess_encoding(path):
    """Sample a file, seeing if the platform-dependent encoding works, and
       trying latin_1 if it doesn't.

       A more robust solution would be to use the chardet library,
       but we want to try and keep this dependency-free."""

    try:
        e = None
        with open(path, newline='', encoding=e) as f:
            f.readline()
        return e
    except UnicodeDecodeError:
        e = 'latin_1'
        with open(path, newline='', encoding=e) as f:
            f.readline()
        return e
