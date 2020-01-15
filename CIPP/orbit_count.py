#!/usr/bin/env python
"""Scans a PTF evaluating the state of priorities and performing counts."""

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
import logging
from collections import Counter
from itertools import groupby

import priority_rewrite as pr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('in_file', help="a .ptf or .csv file")

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s')

    ptf_in = pr.get_input(args.in_file)

    print('\n'.join(format_report(orbit_count(ptf_in))))


def orbit_count(records: list) -> str:
    reports = list()

    sorted_by_o = sorted(records,
                         key=lambda x: int(x['Orbit Number'][:-1]))
    for orbit, g in groupby(sorted_by_o,
                            key=lambda x: int(x['Orbit Number'][:-1])):
        report_dict = {'orbit': orbit, 'pos': 0, 'neg': 0}

        for rec in g:
            if int(rec['Request Priority']) > 0:
                report_dict['pos'] += 1
            else:
                report_dict['neg'] += 1

        reports.append(report_dict)

    return reports


def format_report(records: list) -> list:
    formatted_lines = list()

    # Prepare header and set widths
    header = {'orbit': 'Orbit ({})'.format(len(records)),
              'pos': '# obs', 'neg': '# negative obs'}
    o_width = len(header['orbit'])
    p_width = len(header['pos'])
    n_width = len(header['neg'])
    rules = {'orbit': '-' * o_width,
             'pos': '-' * p_width,
             'neg': '-' * n_width}

    # Accumulate counts and fuss with removing zeros from output.
    pos_counts = Counter()
    neg_count = 0
    str_reports = list()
    for r in records:
        str_d = {'orbit': str(r['orbit']), 'pos': '', 'neg': ''}
        pos_counts.update((r['pos'],))
        neg_count += r['neg']
        for pn in ('pos', 'neg'):
            if r[pn] == 0:
                str_d[pn] = ''
            else:
                str_d[pn] = str(r[pn])
        str_reports.append(str_d)

    # The meat of formatting each line of the report:
    lines_to_format = [header, rules] + str_reports
    for d in lines_to_format:
        o_str = '{orb:<{width}}'.format(orb=d['orbit'], width=o_width)
        p_str = '{pos:^{width}}'.format(pos=d['pos'], width=p_width)
        n_str = '{neg:<{width}}'.format(neg=d['neg'], width=n_width)
        formatted_lines.append(f'{o_str} {p_str} {n_str}')

    # Summary line at the bottom:
    count_summ = '{label:-^{width}}'.format(label='Counts', width=o_width)
    count_summ += ' {} {}'.format(rules['pos'], rules['neg'])
    formatted_lines.append(count_summ)
    pos_count = sum(k * v for k, v in pos_counts.items())
    t_sum = '{sum:^#{o_width}}'.format(sum=pos_count + neg_count,
                                       o_width=o_width)
    t_pos = f'{pos_count:^#{p_width}}'
    t_neg = f'{neg_count:<#{n_width}}'
    formatted_lines.append('{}={}+ {}'.format(t_sum, t_pos, t_neg))
    formatted_lines.append('')

    num_of_obs = list()
    num_of_orbs = list()
    for k in sorted(list(pos_counts.keys()), reverse=True):
        width = len(str(pos_counts[k]))
        if width < 3:
            width = 3
        num_of_obs.append(f'{k:^#{width}}')
        num_of_orbs.append(f'{pos_counts[k]:^#{width}}')

    # formatted_lines.append('Orbit Count Histogram {}'.format(' '.join()))
    formatted_lines.append('# of Observations: {}'.format(' '.join(num_of_obs)))
    formatted_lines.append('# of Orbits      : {}'.format(' '.join(num_of_orbs)))
    formatted_lines.append('')

    # Set up the empty orbit report
    empty_orbits = find_empty_orbits(records)
    formatted_lines.append('Empty Orbits')
    formatted_lines.append('------------')

    return formatted_lines + list(map(str, empty_orbits))


def find_empty_orbits(records: list) -> list:
    orbs = list(map(lambda x: x['orbit'], records))
    return sorted(set(range(orbs[0], orbs[-1])) - set(orbs))


if __name__ == "__main__":
    main()
