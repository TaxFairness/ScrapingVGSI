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

Output is a TSV file that contains the fields selected  using the #id fields
from the HTML file. Those IDs are contained in an array of text strings.

'''

import sys
import argparse
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random

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

# IDs of DOM elements whose values should be plucked up and displayed
domIDs =  [
    [ "MainContent_lblPid", "PID" ],
    [ "MainContent_lblLocation", "Street Address" ],
    [ "MainContent_lblMblu",  "MBLU" ],
    [ "MainContent_lblGenAssessment", "Assessment" ],
    [ "MainContent_lblGenAppraisal", "Appraisal" ],
    [ "MainContent_lblLndAcres", "Lot Size (acres)" ],
    [ "MainContent_lblUseCode", "Land Use Code" ],
    [ "MainContent_lblUseCodeDescription", "Description" ],
    [ "MainContent_lblZone", "Zoning District" ],
    [ "MainContent_lblBldCount", "# Buildings" ],
    ]

'''
Main Function

Parse arguments
Scan through file
Build up dictionary for each IP address

'''


def main(argv=None):
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('rU'), default=sys.stdin)
        parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        parser.add_argument("-e", '--errfile', nargs='?', type=argparse.FileType('w'), default=sys.stderr)
        parser.add_argument('-d', '--debug', action="store_true", help="Enable the debug mode.")
        theArgs = parser.parse_args()
    except:
        return "Error parsing arguments"

    fi = theArgs.infile  # the argument parsing returns open file objects
    fo = theArgs.outfile
    fe = theArgs.errfile

    infile = VisionIDFile(fi)

    output_string = ""
    for x in range(len(domIDs)):
        output_string += domIDs[x][1] + "\t"
    print(output_string, file=fo)

    while True:
        id = infile.readNextVisionID()
        if id == "":  # EOF
            break

        if not theArgs.debug:
            time.sleep (1+3*random.random()) # wait a few seconds before next query

        url = "http://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s"%(id)

        if theArgs.debug:
            print(url, file=fe)

        try:
            page = requests.get(url)
        except:
            output_string = "%s\tCan't reach the server"%(id)
            print(output_string, file=fo)
            continue

        inStr = page.text
        if inStr.find('There was an error loading the parcel') >= 0: # string is present
            output_string = "%s\tProblem loading parcel" % (id)
            print(output_string, file=fo)
            continue

        soup = BeautifulSoup(page.content, "html.parser")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        output_string = ""
        for x in range(len(domIDs)):
            result = soup.find(id=domIDs[x][0])
            output_string += result.text + "\t"
        output_string += current_time
        print(output_string, file=fo)
        print(output_string)

if __name__ == "__main__":
    sys.exit(main())


