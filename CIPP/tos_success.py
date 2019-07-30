#!/usr/bin/env python3
"""Reads a text file WTH list to extract the suggestions, and
it compares the IDs with the records in the input IOF PTF."""

# Copyright 2018,2019, Ross A. Beyer (rbeyer@seti.org)
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

# This program is very specifically for HiRISE CIPP statistics, to determine how
# many desired suggestions made it through the TOS process.  It has not been
# thoroughly tested and is likely to fail for you.  To create the wth.txt CSV
# file, just go to the WTH list, copy the text from the MEPs or the WTHs, or the
# HiKERs or whatever, and copy them into a text file.

import argparse
import csv
import optparse
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='''
The WTH list can be a simple text file pasted from the WTH wiki page, or
it can be a CSV file exported from a spreadsheet application. The PTF
can be a HiRISE PTF, IPTF, or CSV file.''')
    parser.add_argument('-w', '--wth', required=True,
                        help='File with text copied from WTH list.')
    parser.add_argument('iof',
                        help='A CSV, IPTF, or PTF file with PTF records in it.')

    args = parser.parse_args()

    wth = {}
    with open(args.wth, newline='',
              encoding=guess_encoding(args.wth)) as wthfile:
        wthreader = csv.reader(wthfile)
        for row in wthreader:
            if row:
                wth[row[0]] = row[0] + ',' + ','.join(row[2:])

    foundwths = 0
    with open(args.iof, newline='',
              encoding=guess_encoding(args.iof)) as iofile:
        iofreader = csv.reader(iofile)
        for row in iofreader:
            if len(row) > 19 and "H" in row[0]:
                for suggestion in list(wth):
                    if suggestion in row[19]:
                        foundwths += 1
                        print(wth[suggestion])

    print(f'Found: {foundwths} of {len(wth)}')


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


if __name__ == "__main__":
    main()
