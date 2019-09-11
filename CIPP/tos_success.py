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

import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='''
The WTH list can be a simple text file pasted from the WTH wiki page, or
it can be a CSV file exported from a spreadsheet application. The PTF
can be a HiRISE PTF, IPTF, or CSV file.''')
    parser.add_argument('-i', '--inverse', required=False,
                        action='store_true',
                        help='Report on suggestions NOT found in the PTF.')
    parser.add_argument('-w', '--wth', required=True,
                        help='File with text copied from WTH list.')
    parser.add_argument('ptf',
                        help='A CSV, IPTF, or PTF file with PTF records in it.')

    args = parser.parse_args()

    wth = get_wths(args.wth)

    found_suggs = list()

    try:
        ptf = ptf.load(args.ptf)
        for record in ptf:
            t = find_suggestion(wth.keys(), record['Spare 4'],
                                record['Instrument Set'])
            if t is not None:
                found_suggs.append(record['Spare 4'])

            # if 'H' in record['Instrument Set']:
            #     if record['Spare 4'] in wth:
            #         found_suggs.append(record['Spare 4'])
    except ValueError:
        # Wasn't a *real* PTF, probably missing a header,
        # so let's just try and parse it:
        with open(args.ptf, newline='',
                  encoding=ptf.guess_encoding(args.ptf)) as ptfile:
            ptfreader = csv.reader(ptfile)
            for row in ptfreader:
                if len(row) > 19:
                    t = find_suggestion(wth.keys(), row[19],
                                        row[0])
                    if t is not None:
                        found_suggs.append(row[19])
                # if len(row) > 19 and "H" in row[0]:
                #     for suggestion in wth.keys():
                #         if suggestion in row[19]:
                #             found_suggs.append(suggestion)

    if args.inverse:
        not_found = 0
        for w in wth.keys():
            if w not in found_suggs:
                print('Did not find {}'.format(wth[w]))
                not_found += 1

        if not_found == 0:
            print('All of the suggestions were found in the PTF.')
        else:
            print(f'Did not find {not_found} of {len(wth)}')
    else:
        for w in found_suggs:
            print(wth[w])
        print(f'Found: {len(found_sugss)} of {len(wth)}')


def get_wths(path: os.PathLike) -> dict:
    d = {}
    with open(path, newline='',
              encoding=ptf.guess_encoding(path)) as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                d[row[0]] = row[0] + ',' + ','.join(row[2:])
    return d


def find_suggestion(wths: list, suggestion: str, inst_set: str):
    if 'H' in inst_set:
        if suggestion in wths:
            return suggestion
        else:
            return None


if __name__ == "__main__":
    main()
