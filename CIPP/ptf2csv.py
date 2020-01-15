#!/usr/bin/env python3
"""Converts a PTF to a plain CSV file with a single header line."""

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


import argparse
import csv
from pathlib import Path

import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', required=False, default='.csv')
    parser.add_argument('-l', '--links', required=False, action='store_true',
                        help='This flag will write a final element to each '
                             'output record with the HiReport URL as a '
                             'spreadsheet formula.  When this .csv file is '
                             'imported by a spreadsheet program, there '
                             'should be clickable links in those cells.')
    parser.add_argument('ptf', metavar="some.ptf-file")

    args = parser.parse_args()

    csv_path = ''
    if args.output.startswith('.'):
        csv_path = Path(args.ptf).with_suffix(args.output)
    else:
        csv_path = Path(args.output)

    ptf_in = ptf.load(args.ptf)

    if args.links:
        # Add HiReport Links
        link_key = 'HiReport URLs'
        ptf_in.fieldnames.append(link_key)
        for i, rec in enumerate(ptf_in):
            new_rec = rec
            u = 'https://hireport.lpl.arizona.edu/hireport/suggestion/'
            sugg = rec['Team Database ID']
            url = u + sugg
            f = '=HYPERLINK("{}", "HiReport {}")'.format(url, sugg)

            # If the formula is too fancy, can always fall back to
            # just the URL:
            # new_rec[link_key] = url
            new_rec[link_key] = f
            ptf_in[i] = new_rec

    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ptf_in.fieldnames)
        writer.writeheader()
        for row in ptf_in:
            writer.writerow(row)


if __name__ == "__main__":
    main()
