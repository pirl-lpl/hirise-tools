#!/usr/bin/env python
"""Scans a PTF looking for any records that have identical Request Priority
fields, and attempts to assign them unique priorities based on latitude."""

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
import collections
import getpass
import logging
import os
from datetime import datetime

import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', required=False)
    parser.add_argument('-r', '--reset', required=False, help='A set of '
                        'comma-delimited, colon-separated pairs for making '
                        'a priority group start at a different value.')
    parser.add_argument('-k', '--keepzero', required=False,
                        action='store_true', help='Retain priorities <= 0, '
                        'default is to omit them in the output.')
    parser.add_argument('-n', '--dry_run', required=False,
                        action='store_true', help='Perform the rearranging '
                        'but do not write out results.')
    parser.add_argument('in_file', help="a .ptf or .csv file")

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s')

    ptf_in = get_input(args.in_file)

    new_ptf_records = priority_rewrite(ptf_in, args.reset, args.keepzero)

    new_ptf_records.sort(key=lambda x: int(x['Request priority']), reverse=True)

    if args.dry_run:
        pass
    else:
        out_str = write_output(ptf_in, new_ptf_records, args.output)
        if out_str:
            print(out_str)


def priority_rewrite(records, reset_str=None, keepzero=False) -> list:
    '''Rewrites identical priorities based on Latitude.
    '''
    count = collections.Counter()
    for r in records:
        count[int(r['Request priority'])] += 1

    reset = dict()
    if reset_str:
        for elem in reset_str.split(','):
            (k, v) = elem.split(':')
            reset.setdefault(int(k), int(v))
        for v in reset.values():
            if v in count:
                raise KeyError(f'The reset priority, {v} already exists as a '
                               'priority group in this file.')

    for k in count.keys():
        if k in reset:
            c = count[k]
            del count[k]
            count[reset[k]] = c

    new_records = list()
    if keepzero:
        ordered_p = sorted(count.keys())
    else:
        ordered_p = sorted(filter(lambda x: x > 0, count.keys()))

    for i, pri in enumerate(ordered_p):
        try:
            next_pri = ordered_p[i + 1]
        except IndexError:
            next_pri = pri + count[pri] + 1

        if pri in reset.values():
            for (k, v) in reset.items():
                if pri == v:
                    old_pri = k
            pri_records = list(filter(lambda x: int(x['Request priority']) == old_pri,
                                      records))
        else:
            pri_records = list(filter(lambda x: int(x['Request priority']) == pri,
                                      records))
        pri_records.sort(key=lambda x: abs(float(x['Latitude'])), reverse=True)

        span = next_pri - pri
        if count[pri] > span:
            logging.warning('Starting at {} we need {} spots, but the next '
                            'priority is {}.'.format(pri,
                                                     count[pri],
                                                     next_pri))
            logging.warning('\tLeaving these {} as identical priority '
                            '{}.'.format(count[pri], pri))
            for r in pri_records:
                d = collections.OrderedDict(r)
                new_records.append(d)
        else:
            for j, r in enumerate(pri_records):
                d = collections.OrderedDict(r)
                d['Request priority'] = pri + j
                new_records.append(d)
    return new_records


def get_input(p: os.PathLike) -> collections.abc.Sequence:
    seq = list()
    try:
        seq = ptf.load(p)
    except ValueError:
        with open(p) as csvfile:
            reader = csv.DictReader(csvfile)
            seq = list()
            for row in reader:
                seq.append(row)

    return seq


def write_output(seq, records, output=None) -> str:
    out_string = None
    fieldnames = list()
    if hasattr(seq, 'fieldnames'):
        fieldnames = seq.fieldnames
    else:
        fieldnames = seq[0].keys()

    if isinstance(seq, ptf.PTF):
        new_ptf = ptf.ptf(seq.dictionary, seq.fieldnames, records)
        new_ptf['USERNAME'] = getpass.getuser()
        new_ptf['CREATION_DATE'] = datetime.utcnow().strftime('%Y-%jT%H:%M:%S')
        if output:
            new_ptf.dump(output)
        else:
            out_string = new_ptf.dumps()
    else:
        if output:
            with open(output, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in records:
                    writer.writerow(row)
        else:
            print(str(fieldnames))
            for row in records:
                print(row)

    return out_string


if __name__ == "__main__":
    main()
