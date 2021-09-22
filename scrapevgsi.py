'''
Scrape VGSI Records

Retrieve VGSI records from their server (http://gsi.vgsi.com),
then parse out interesting fields from the resulting HTML responses.

Input is a CSV file that contains a list of "VisionID"s in this format:

# Source: David Robbins, Lyme Planning and Zoning - 6Apr2021
# Mapping between Vision ID and the tax map/lot number
VisionID	TaxMap	Lot
123	201	86
125	201	88
127	201	90

Output is a CSV file that contains the fields selected  using the #id fields
from the HTML file. Those IDs are contained in an array of text strings.

stdin defaults to taxcardlookup-6Apr2021.csv
stdout defaults to ./output.csv

'''

import sys
import argparse
import requests
from bs4 import BeautifulSoup
import re
import os

# from collections import OrderedDict

"""
readNextVisionID(f)

Reads a line from the input file, and returns the first comma-separated field.
Ignore lines that begin with # (they're comments)
Return "" to signal EOF)

"""


class VisionIDFile:
    def __init__(self, file):
        self.theFile = file

    def readNextVisionID(self):

        while True:
            line = self.theFile.readline()
            if line == "":
                return ""   # hit EOF
            if line[0] != "#":
                break       # Non-comment line - break out of loop

        vals = line.split(",")
        return vals[0]


        # line = self.theFile.readline()
        # if line == "":
        #     return []
        # secString = re.findall("[ ]\d\d:\d\d:\d\d[ ]", line)[0]
        # ipAdrs = re.findall("SRC=(.*?)[ ]", line)[0]
        #
        # [hh, mm, ss] = secString.split(":")
        #
        # connTime = 3600 * int(hh) + 60 * int(mm) + int(ss)
        # if connTime < self.prevConnTime:
        #     return []  # got into next day's data - treat as EOF
        # self.prevConnTime = connTime
        #
        # return [connTime, ipAdrs]


'''
hhmm - format number of seconds as "hh:mm"
'''


def hhmm(secs):
    roundedsecs = secs + 30
    hh = int(roundedsecs / 3600)
    return '%02d:%02d' % (hh, (roundedsecs - hh * 3600) / 60)


'''
Main Function

Parse arguments
Scan through file
Build up dictionary for each IP address

'''


def main(argv=None):
    #try:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('rU'), default=sys.stdin)
    parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument("-e", '--errfile', nargs='?', type=argparse.FileType('w'), default=sys.stderr)
    # parser.add_argument("--notables", action="store_false", help="Don't print the tables")
    theArgs = parser.parse_args()
    #except Exception, err:
    #    return str(err)

    fi = theArgs.infile  # the argument parsing returns open file objects
    fo = theArgs.outfile
    fe = theArgs.errfile

    infile = VisionIDFile(fi)

    while True:
        id = infile.readNextVisionID()
        if id == "":  # EOF
            break

        # print id
        url = "http://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s"%(id)

        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")
        # print(page.text)



        results = (soup.find(id="MainContent_ctl01_lblYearBuilt"))
        print(results.text)
        exit()
        #
    # print >> fe, "Total addresses blacklisted: %d" % blacklistCount


if __name__ == "__main__":
    sys.exit(main())


