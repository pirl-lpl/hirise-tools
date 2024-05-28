#!/usr/bin/env python3
"""Reads a text file WTH list to extract the suggestions, and
it compares the IDs with the records in the input IOF PTF."""

# Copyright 2018-2023, Ross A. Beyer (rbeyer@seti.org)
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
import os
import sys

import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='''
The WTH list can be a simple text file pasted from the WTH wiki page,
the STaR tool, or it can be a CSV file exported from a spreadsheet application.
The PTF can be a HiRISE PTF, IPTF, or CSV file.''')
    parser.add_argument('-i', '--inverse', required=False,
                        action='store_true',
                        help='Report on suggestions NOT found in the PTF.')
    parser.add_argument("-l", "--limited", action="store_true",
                        help="Only print limited information.")
    parser.add_argument("-s", "--sorted", action="store_true",
                        help="Output sorted by suggestion number.")
    parser.add_argument('-w', '--wth', required=True,
                        help='File with text copied from WTH list.')
    parser.add_argument('ptf',
                        help='A CSV, IPTF, or PTF file with PTF records in it.')

    args = parser.parse_args()

    wth = get_wths(args.wth, args.limited)

    found_suggs = get_suggestions(args.ptf, wth.keys())

    if args.sorted:
        found_suggs.sort()

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
        print(f'Found: {len(found_suggs)} of {len(wth)}')


def get_wths(path: os.PathLike, limited=False) -> dict:
    d = {}
    with open(path, newline='',
              encoding=ptf.guess_encoding(path)) as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                if len(row) == 1:
                    d[row[0]] = row[0]
                elif len(row) <= 4:
                    # This came from the old WTH wiki page
                    d[row[0]] = ",".join(row)
                else:
                    # Guessing that this came from C&P from STaR:
                    if limited:
                        d[row[1]] = ", ".join([row[1], row[2], row[4]])
                    else:
                        d[row[1]] = ",".join(row[1:])
    return d


def get_suggestions(ptfpath: os.PathLike, wth_suggs: list) -> list:
    found = list()
    try:
        p = ptf.load(ptfpath)
        for record in p:
            s = find_suggestion(wth_suggs, record['Comment'],
                                record['Instrument Set'])
            if s is not None:
                found.append(s)

    except ValueError:
        # Wasn't a *real* PTF, probably missing a header,
        # so let's just try and parse it:
        with open(ptfpath, newline='',
                  encoding=ptf.guess_encoding(ptfpath)) as ptfile:
            ptfreader = csv.reader(ptfile)
            for row in ptfreader:
                if len(row) > 19:
                    s = find_suggestion(wth_suggs, row[19], row[0])
                    if s is not None:
                        found.append(s)
    return found


def find_suggestion(wths: list, ptf_comment: str, inst_set: str):
    if('H' in inst_set):
        comment_tokens = ptf_comment.split()
        for suggestion in wths:
            if suggestion == comment_tokens[0]:
                return suggestion
    return None


if __name__ == "__main__":
    main()
