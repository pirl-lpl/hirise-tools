#!/usr/bin/env python
"""Takes one or more text files that contain special targets, and scans a
PTF, looking for targets with a certain priority, and modifies them based on
priorities from the special targets.

This is NOT a substitute for reviewing the PTF yourself.

The algorithm will examine each target in the PTF which has a
priority of 11000, and will see if that target is in any of the
special target text files (which can just be text copy and pasted
from the wiki). If it is and there is a priority there, the
priority is combined with 11000 as follows: the priority
is multiplied by 10, and added to 11300. So a 10 becomes 11400,
a 6 becomes 11360, a 2 becomes 11320, etc.
"""

# Copyright 2020, Ross A. Beyer (rbeyer@seti.org)
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
import logging
import os

import priority_rewrite as pr
import ptf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Will report additional information.",
    )
    parser.add_argument("-o", "--output", required=False)
    parser.add_argument(
        "-p", "--ptf", required=True, help="a .ptf or .csv file"
    )
    parser.add_argument(
        "wth", nargs="+", help="File(s) with text copied from WTH list."
    )

    args = parser.parse_args()

    logging.basicConfig(
        format="%(levelname)s: %(message)s", level=(30 - 10 * args.verbose)
    )

    ptf_in = pr.get_input(args.ptf)

    specials = {}
    for f in args.wth:
        specials.update(get_special_priorities(f))

    new_ptf_records = apply_priorities(ptf_in, 11000, specials)

    out_str = pr.write_output(ptf_in, new_ptf_records, args.output)
    if out_str:
        print(out_str)


def get_special_priorities(path: os.PathLike) -> dict:
    """Returns a dict whose keys are suggestion IDs, and
    whose values are integer priorities.

    The *path* file can be any CSV-type file, blank lines are
    ignored, the first entry on each "real" line is taken to be
    the suggesion ID, and the second item is assumed to be a
    priority and converted to an integer.
    """
    d = {}
    with open(path, newline="", encoding=ptf.guess_encoding(path)) as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                d[row[0]] = int(row[1])
    return d


def apply_priorities(records: list, basepriority: int, specials: dict):
    """For each item in *records* that has *basepriority*, its suggestion
    number is checked for in *specials*.  If present, the priority of the
    item in *records* is modified.

    The priority is modified as follows, the special priority is multiplied
    by 10 and added to *basepriority* + 300.
    """


    new_records = list()

    for r in records:
        if r["Team Database ID"] in specials:
            if basepriority == int(r["Request Priority"]):
                sp_pri = specials[r["Team Database ID"]]
                orig_pri = int(r["Request Priority"])
                if 1 <= sp_pri <= 10:
                    r["Request Priority"] = orig_pri + 300 + (sp_pri * 10 )
                else:
                    raise ValueError(
                        f"The priority from the special file ({sp_pri}) is "
                        "not an integer between 1 and 10, inclusive."
                    )
                logging.info(
                    f"{r['Team Database ID']} was {orig_pri} "
                    f"is now {r['Request Priority']}"
                )
            else:
                logging.warning(
                    f"WTH {r['Team Database ID']} has a priority "
                    f"of {r['Request Priority']}, FWIW.")

        new_records.append(r)

    return new_records


if __name__ == "__main__":
    main()
