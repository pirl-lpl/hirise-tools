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
import io
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

    reset = make_reset_dict(reset_str, count)

    for k in count.keys():
        if k in reset:
            count[reset[k]] = count[k]
            del count[k]

    ordered_p = sort_and_filter(count.keys(), keepzero)

    new_records = list()
    for i, pri in enumerate(ordered_p):
        try:
            next_pri = ordered_p[i + 1]
        except IndexError:
            next_pri = None

        pri_records = get_records_for_this_priority(pri, records, reset)
        pri_records.sort(key=lambda x: abs(float(x['Latitude'])), reverse=True)

        if is_enough_space(pri, next_pri, count[pri]):
            for j, r in enumerate(pri_records):
                d = collections.OrderedDict(r)
                d['Request priority'] = pri + j
                new_records.append(d)
        else:
            logging.warning('Starting at {} we need {} spots, but the next '
                            'priority is {}.'.format(pri,
                                                     count[pri],
                                                     next_pri))
            logging.warning('\tLeaving these {} as identical priority '
                            '{}.'.format(count[pri], pri))
            for r in pri_records:
                d = collections.OrderedDict(r)
                new_records.append(d)
    return new_records


def make_reset_dict(s: str, priorities: collections.Counter) -> dict:
    reset = dict()
    if s:
        for elem in s.split(','):
            (k, v) = elem.split(':')
            reset.setdefault(int(k), int(v))
        for v in reset.values():
            if v in priorities:
                raise KeyError(f'The reset priority, {v} already exists as a '
                               'priority group in this file.')
    return reset


def sort_and_filter(iterable, keepzero=False) -> list:
    if keepzero:
        return sorted(iterable)
    else:
        return sorted(filter(lambda x: x > 0, iterable))


def get_records_for_this_priority(pri: int, records: list, reset: dict) -> list:
    out_records = list()
    if pri in reset.values():
        for (k, v) in reset.items():
            if pri == v:
                pri = k
    out_records = list(filter(lambda x: int(x['Request priority']) == pri,
                              records))
    return out_records


def is_enough_space(priority: int, next_priority: int, span: int) -> bool:
    if next_priority is None:
        return True
    if span <= (next_priority - priority):
        return True
    else:
        return False


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
        new_ptf = ptf.PTF(seq.dictionary, seq.fieldnames, records)
        new_ptf['USERNAME'] = getpass.getuser()
        new_ptf['CREATION_DATE'] = datetime.utcnow().strftime('%Y-%jT%H:%M:%S')
        if output:
            new_ptf.dump(output)
        else:
            out_string = new_ptf.dumps()
    else:
        if output is None:
            csvfile = io.StringIO()
            dict_write(csvfile, fieldnames, records)
            out_string = csvfile.getvalue()

        else:
            with open(output, 'w') as csvfile:
                dict_write(csvfile, fieldnames, records)

    return out_string


def dict_write(filelike, fieldnames, records):
    writer = csv.DictWriter(filelike, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)


if __name__ == "__main__":
    main()
