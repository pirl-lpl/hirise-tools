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

# This program is very specifically for HiRISE CIPP statistics, to determine how many 
# desired suggestions made it through the TOS process.  It has not been thoroughly 
# tested and is likely to fail for you.  To create the wth.csv file, just go to the WTH list,
# copy the text from the MEPs or the WTHs, or the HiKERs or whatever, and copy them into a
# text file.


import os, sys, optparse, csv
from textwrap import dedent, fill


def manual(option, opt, value, parser):
    usage = '''\
        This program reads a text file WTH list to extract the suggestions, and
        it compares the IDs with the records in the input IOF PTF.
    '''
    print(parser.usage + "\n", file=sys.stderr)
    print(fill(dedent(usage), 80), file=sys.stderr)
    sys.exit()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main():
    try:
        try:
            usage = "usage: tos_success.py [--help][--manual] -w <wth.csv> <iof.csv>"
            parser = optparse.OptionParser(usage=usage)
            parser.add_option("--manual", "-m", action="callback", callback=manual,
                              help="Read the manual.")
            parser.add_option("--wth", "-w", dest="wthfile", 
                              help="File with text copied from WTH list.")

            (options, args) = parser.parse_args()

            if not args: parser.error("need iof.csv file")

            if not options.wthfile: parser.error("need wth.csv file")


        except optparse.OptionError as err:
            raise Usage(err)

        wth = {}
        with open( options.wthfile, newline='' ) as csvfile:
            wthreader = csv.reader( csvfile )
            for row in wthreader:
                if row: wth[row[0]] = row[0]+','+','.join(row[2:])

        foundwths = 0
        with open( args[0], newline='' ) as iofile:
            iofreader = csv.reader( iofile )
            for row in iofreader:
                if len(row) > 19 and "H" in row[0]:
                    for suggestion in list(wth):
                        if suggestion in row[19]:
                            foundwths += 1
                            #print( row[19] )
                            print(wth[suggestion])

        print ("Found: "+str(foundwths)+" of "+str(len(wth)))

    except Usage as err:
        print(err.msg, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
