#!/usr/bin/env python3

# Copyright 2018, Ross A. Beyer (rbeyer@seti.org)
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


import os, sys, optparse, csv
from textwrap import dedent, fill


def manual(option, opt, value, parser):
    """Print a brief usage manual."""
    purpose = '''\
        This program reads a text file WTH list to extract the suggestions, and
        it compares the IDs with the records in the input IOF PTF.
    '''
    formats = '''\
        The WTH list can be a simple text file pasted from the WTH wiki page, or
        it can be a CSV file exported from a spreadsheet application. The PTF
        can be a HiRISE PTF, IPTF, or CSV file.
    '''
    print(parser.usage + "\n", file=sys.stderr)
    print(fill(dedent(purpose), 80) + "\n", file=sys.stderr)
    print(fill(dedent(formats), 80) + "\n", file=sys.stderr)
    sys.exit()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def read_file(filename):
    """Read a file, trying one of several encodings."""
    lines = []
    for encoding in [None, "latin_1", "mac_roman"]:
        try:
            with open(filename, newline='', encoding=encoding) as file:
                lines = file.read().splitlines()
        except:
            pass
        if len(lines) > 0:
            break
    return lines

def main():
    try:
        try:
            usage = "usage: tos_success.py [--help][--manual] -w <wth.txt> <iof.iptf>"
            parser = optparse.OptionParser(usage=usage)
            parser.add_option("--manual", "-m", action="callback", callback=manual,
                              help="Read the manual.")
            parser.add_option("--wth", "-w", dest="wthfile", 
                              help="File with text copied from WTH list.")

            (options, args) = parser.parse_args()

            if not args: parser.error("need iof.iptf file")

            if not options.wthfile: parser.error("need wth.txt or or wth.csv file")

        except optparse.OptionError as err:
            raise Usage(err)


        wth = {}
        wthfile = read_file(options.wthfile)
        if len(wthfile) == 0:
        	print("Unable to read " + options.wthfile + ".", file=sys.stderr)
        	return 1
        wthreader = csv.reader(wthfile)
        for row in wthreader:
            if row: wth[row[0]] = row[0]+','+','.join(row[2:])

        foundwths = 0
        iofile = read_file(args[0])
        if len(iofile) == 0:
            print("Unable to read " + args[0] + ".", file=sys.stderr)
            return 1
        iofreader = csv.reader(iofile)
        for row in iofreader:
            if len(row) > 19 and "H" in row[0]:
                for suggestion in list(wth):
                    if suggestion in row[19]:
                        foundwths += 1
                        print(wth[suggestion])

        print ("Found: "+str(foundwths)+" of "+str(len(wth)))

    except Usage as err:
        print(err.msg, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
