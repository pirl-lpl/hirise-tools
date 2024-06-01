#!/usr/bin/env python
"""Scans a PTF, grouping records by orbit, and attempts to deconflict
observations in that orbit.

This is NOT a substitute for reviewing the PTF yourself.

The algorithm will examine each orbit (based on the PTF Orbit Number
field, ignoring any Orbit Alternatives), and will guarantee that
at most, only the user-specified number of observations will remain
as positive priorities after it runs, all other records will be set
to negative priorities (allowing inspection afterwards).

For each orbit, the algorithm will begin with the highest
prioritized observation, and deprioritize any observations within
the latitude exclusion range in either direction, then find the
next highest, and so on.  When faced with observations that have
the same priority, it will give preference to the observation
that is closest to the equator.

The "half-width" of the latitude exclusion zone is 40 degrees for
SPORC stereo-2s and above (14600), then 30 degrees for priorities
from there through the 2nd half stereos (13000), then 20 degrees
through the easier-to-get WTHs, stereo 1s, HiKERs, and high priority
non-WTH targets (10000), and then 15 degrees for priorities below that.
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
#
# TODO: write in a mechanism that allows the user to optimize for more
#   observations per orbit, rather than strictly giving the highest priority
#   plus the lowest latitude the top spot.  Doing so may 'exclude' two other
#   observations, and if one had the same priority, but didn't 'exclude' the
#   other, you might be able to fit more observations on an orbit.
#
# TODO: may also want something other than abs(latitude) to be a driver,
#   possibly time since coming out of eclipse or something.  Lots of
#   possibilities.
#
# TODO: If we really want to get fancy, implement a way to have a
#   user-specified half_widths list.

import argparse
import copy
import logging
import sys

from itertools import groupby

import priority_rewrite as pr

logger = logging.getLogger(__name__)


class SPORCError(Exception):

    def __init__(self, errmsg, rec):
        super().__init__(self, errmsg)
        self.record = rec


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-o", "--output", required=False)
    parser.add_argument(
        "-a", "--high_alt",
        nargs="?",
        default=None,  # -a not given on command line
        const=-1,  # -a given, but no value provided
        type=int,
        help="Allow high-latitude observations with more than three Orbit "
             "Alternatives to remain, even if they would otherwise be "
             "deprioritized.  By default, the priority will not be altered, "
             "but if a non-negative integer is given, that is the priority "
             "that will be overwritten, typically 1 or 5 are good choices here."
    )
    parser.add_argument(
        "-r", "--high_roll",
        nargs="?",
        default=None,
        const=8.8,
        type=float,
        help="If specified, prioritized observations with a high roll "
             "(default %(default)s) can allow a single lower priority "
             "observation with a similar latitude to remain prioritized."
    )
    parser.add_argument(
        "-l", "--logfile",
        required=False,
        help="The log file to write log messages to in addition "
             "to the terminal.",
    )
    parser.add_argument(
        "--per_orbit",
        required=False,
        default=4,
        type=int,
        help="The max number of observations to keep in an orbit.",
    )
    parser.add_argument(
        "-n",
        "--dry_run",
        required=False,
        action="store_true",
        help="Perform the rearranging but do not write out results.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Will report information."
    )
    parser.add_argument("in_file", help="a .ptf or .csv file")

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO

    logger.setLevel(log_level)

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if args.logfile is not None:
        fh = logging.FileHandler(args.logfile)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    ptf_in = pr.get_input(args.in_file)

    # half-widths are a list of two-tuples, the first position is a
    # priority value, and the second is a latitude half-width.
    # the final two-tuple should be (0, 0).
    half_widths = ((17000, 40), (14600, 30), (13000, 20), (10000, 15), (0, 0))

    new_ptf_records = prioritize_by_orbit(
        ptf_in,
        half_widths,
        args.per_orbit,
        high_alt=args.high_alt,
        high_roll=args.high_roll
    )

    # This sorting ignores the 'a' or 'd' markers on Orbits.
    new_ptf_records.sort(key=lambda x: int(x["Orbit Number"][:-1]))

    if args.dry_run:
        pass
    else:
        out_str = pr.write_output(ptf_in, new_ptf_records, args.output)
        if out_str:
            print(out_str)


class Intervals(object):
    """Manages the intervals described by the latitude exclusion zones.
    """

    def __init__(self, half_widths=None):
        self.intervals = list()  # a list of two-tuples
        if half_widths is None:
            self.half_widths = ((sys.maxsize, 40), (0, 0))
        else:
            if half_widths[-1][0] != 0:
                half_widths.append((0, 0))

            self.half_widths = half_widths

    def __str__(self):
        return str(self.intervals)

    def __repr__(self):
        return "{!s}({!s}])".format(type(self).__name__, self.half_widths)

    def add(self, point: float, priority=None):
        """Adds an interval centered on *point* whose boundaries
        are derived from the *priority* value.
        """
        p = float(point)
        hw = self.get_half_width(priority)
        new_interval = ((p - hw), (p + hw))
        intervals = self.intervals + [new_interval]

        # This interval merging logic is from
        # https://codereview.stackexchange.com/questions/69242/merging-overlapping-intervals
        sorted_by_lower_bound = sorted(intervals, key=lambda x: x[0])
        merged = list()

        for higher in sorted_by_lower_bound:
            if not merged:
                merged.append(higher)
            else:
                lower = merged[-1]
                # test for intersection between lower and higher:
                # we know via sorting that lower[0] <= higher[0]
                if higher[0] <= lower[1]:
                    upper_bound = max(lower[1], higher[1])
                    # replace by merged interval:
                    merged[-1] = (lower[0], upper_bound)
                else:
                    merged.append(higher)

        self.intervals = merged
        return

    def get_half_width(self, priority=None):
        """Returns the half-width given the *priority* value.

        If *priority* is not given, the first half-width in this
        object's half_widths will be used.
        """
        if priority is None:
            return self.half_widths[0][1]
        else:
            for i in range(len(self.half_widths) - 1):
                if (
                    self.half_widths[i][0]
                    > priority
                    >= self.half_widths[i + 1][0]
                ):
                    return self.half_widths[i][1]

            raise ValueError(
                f"The priority ({priority}) is not in the range "
                f"({self.half_widths[-1][0]}, {self.half_widths[0][0]})."
            )

    def is_in(self, point: float):
        """Returns True if the given value is within (inclusive) the
        boundaries of one of this object's intervals.  False otherwise.
        """
        p = float(point)
        for i in self.intervals:
            if i[0] <= p <= i[1]:
                return True
        else:
            return False


def prioritize_by_orbit(
    records: list, half_widths, observations=4, high_alt=None, high_roll=None,
) -> list:
    """Rewrites priorities by orbit."""

    while True:
        records_new = copy.deepcopy(records)
        out_records = list()
        try:
            out_records = list()
            sorted_by_o = sorted(records_new, key=lambda x: int(x["Orbit Number"][:-1]))
            for orbit, g in groupby(
                sorted_by_o, key=lambda x: int(x["Orbit Number"][:-1])
            ):
                # We create new_records, so that we can later examine which
                # observations have already been prioritized for *this* orbit.
                new_records = list()
                exclude = Intervals(half_widths)
                high_roll_exclude = Intervals(half_widths)
                obs_count = 0
                by_orbit = list(g)
                by_orbit.sort(key=lambda x: int(x["Request Priority"]), reverse=True)
                for pri, pri_g in groupby(
                    by_orbit, key=lambda x: int(x["Request Priority"])
                ):
                    recs = list(pri_g)
                    if pri < 0:
                        new_records += recs
                        continue
                    if len(recs) != 1:
                        # need to prioritize these by latitude
                        recs = pr.priority_rewrite(recs, keepzero=True)

                    for r in sorted(
                        recs, key=lambda x: int(x["Request Priority"]), reverse=True
                    ):
                        if obs_count < observations and not exclude.is_in(
                            r["Latitude"]
                        ):
                            exclude.add(r["Latitude"], int(r["Request Priority"]))
                            obs_count += 1
                            r["Request Priority"] = pri
                        else:
                            kept = False
                            if (
                                high_alt is not None and
                                abs(float(r["Latitude"])) > 65 and
                                len(r["Orbit Alternatives"].split()) > 3
                            ):
                                ha_pri = pri if high_alt < 0 else high_alt
                                r["Request Priority"] = ha_pri
                                logger.info(
                                    f"{r['Team Database ID']} would have been "
                                    f"observation #{observations} in orbit "
                                    f"{orbit} or would have been excluded on "
                                    f"the basis of existing intervals "
                                    f"{exclude}, but was higher than 65 "
                                    f"latitude and had more than 3 Alternative "
                                    f"orbits."
                                )
                                kept = True

                            if(
                                high_roll is not None and
                                abs(float(r["Roll Angle"])) < 5.0
                            ):
                                for nr in new_records:
                                    if (
                                        int(nr["Request Priority"]) > 0 and
                                        abs(
                                            float(r["Latitude"]) -
                                            float(nr["Latitude"])
                                        ) < 5.0 and
                                        not high_roll_exclude.is_in(
                                            r["Latitude"]
                                        ) and
                                        abs(float(nr["Roll Angle"])) > high_roll
                                    ):
                                        high_roll_exclude.add(
                                            r["Latitude"],
                                            int(r["Request Priority"])
                                        )
                                        r["Request Priority"] = pri
                                        logger.info(
                                            f"{r['Team Database ID']} would "
                                            f"have been deprioritized in orbit "
                                            f"{orbit}, but has a similar "
                                            f"latitude as a prioritized "
                                            f"observation "
                                            f"({nr['Team Database ID']}) with "
                                            f"a high roll (> {high_roll})."
                                        )
                                        kept = True
                                        break

                            if not kept:
                                r["Request Priority"] = -1 * pri
                                if obs_count >= observations:
                                    logger.info(
                                        f"{r['Team Database ID']} would have been "
                                        f"observation #{observations} in orbit "
                                        f"{orbit} and was given priority "
                                        f"{r['Request Priority']}."
                                    )
                                else:
                                    logger.info(
                                        f"{r['Team Database ID']} (latitude: "
                                        f"{r['Latitude']}) is in the intervals "
                                        f"{exclude} in orbit "
                                        f"{orbit}, priority: "
                                        f"{r['Request Priority']}."
                                    )

                                if r["Spare 4"].startswith("SPORC"):
                                    # If we're knocking out one half of a SPORC,
                                    # that needs to remove the other half, which
                                    # could have a ripple in this process, so we
                                    # need to interrupt
                                    raise SPORCError(
                                        (
                                            f"{r['Team Database ID']} is a SPORC that "
                                            f"could not be acquired"
                                        ),
                                        rec=r
                                    )

                        new_records.append(r)

                out_records += new_records

            return out_records

        except SPORCError as err:
            spnum, other_half = (err.record["Spare 4"].split()[0]).split(":")
            logger.info(
                f"{r['Team Database ID']} is part of {spnum}"
            )
            for i, r in enumerate(records):
                if int(r["Request Priority"]) > 0 and (
                    r["Team Database ID"] == err.record["Team Database ID"] or
                    r["Team Database ID"] == other_half
                ):
                    r["Request Priority"] = -1 * int(r["Request Priority"])
                    logger.info(
                        f"{r['Team Database ID']} is {spnum} and was given "
                        f"priority {r['Request Priority']}."
                    )
                    records[i] = r

            logger.info(
                "Re-prioritizing from the top with this now-missing SPORC."
            )


if __name__ == "__main__":
    main()
