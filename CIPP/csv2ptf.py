#!/usr/bin/env python
"""Converts a CSV file to a PTF file based on the header of an example PTF file."""

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
import getpass
from datetime import datetime
from pathlib import Path

import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', required=False, default='.ptf')
    parser.add_argument('-p', '--ptf', required=True)
    parser.add_argument('csv', metavar="some.csv-file")

    args = parser.parse_args()

    ptf_template = ptf.load(args.ptf)

    records = list()
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.append(row)

    new_ptf = ptf.PTF(ptf_template.dictionary,
                      ptf_template.fieldnames,
                      records)

    new_ptf['USERNAME'] = getpass.getuser()
    new_ptf['CREATION_DATE'] = datetime.utcnow().strftime('%Y-%jT%H:%M:%S')

    ptfout_path = ''
    if args.output.startswith('.'):
        ptfout_path = Path(args.csv).with_suffix(args.output)
    else:
        ptfout_path = Path(args.output)

    new_ptf.dump(ptfout_path)


if __name__ == "__main__":
    main()
