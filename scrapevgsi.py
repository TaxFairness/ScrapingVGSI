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

Reads a line from the input file, and returns the three comma-separated fields.
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
                return []   # hit EOF
            if line[0] != "#":
                break       # Non-comment line - break out of loop

        vals = line.split(",")
        return vals

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
tableIDs = [
    "Appr. Year",
    "Improvements",
    "Land",
    "Total",
]
saleDomIDs = [
    [ "MainContent_lblPrice", "Recent Sale Price", ],
    [ "MainContent_lblSaleDate", "Recent Sale Date" ]
    ]
saleTableIDs = [
    "Recent Sale Price",
    "Recent Sale Date",
    "Prev Sale Price",
    "Prev Sale Date",
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

    # Print the heading row, with all the column names
    output_string = ""
    for x in range(len(domIDs)):
        output_string += domIDs[x][1] + "\t"
    for x in range(len(tableIDs)):
        output_string += tableIDs[x] + "\t"
    for x in range(len(saleTableIDs)):
        output_string += saleTableIDs[x] + "\t"
    print(output_string, file=fo)

    recordCount = 0
    while True:
        recordCount += 1
        ids = infile.readNextVisionID()
        if ids == []:  # EOF
            break

        if not theArgs.debug:
            time.sleep (1+3*random.random()) # wait a few seconds before next query

        url = "http://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s"%(ids[0])

        if theArgs.debug:
            print(url, file=fe)

        try:
            page = requests.get(url)
        except:
            output_string = "%s\tCan't reach the server"%(ids[0])
            print(output_string, file=fo)
            continue

        inStr = page.text
        if inStr.find('There was an error loading the parcel') >= 0: # string is present
            output_string = "%s\tProblem loading parcel PID %s, Map %s Lot %s" % (ids[0], ids[0], ids[1], ids[2])
            print(output_string, file=fo)
            continue

        soup = BeautifulSoup(page.content, "html.parser")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # First print the random fields from the page
        output_string = ""
        for x in range(len(domIDs)):
            result = soup.find(id=domIDs[x][0])
            output_string += result.text + "\t"

        # Print the most recent appraisal date, Improvements, Land, and Total
        table = soup.find(
            lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "MainContent_grdCurrentValueAppr")
        rows = table.findAll(lambda tag: tag.name == 'tr')
        vals = rows[1].contents # contents of the row
        for x in range(1,5):
            output_string += vals[x].text + "\t"

        # Print the recent sale price and date
        for x in range(len(saleDomIDs)):
            result = soup.find(id=saleDomIDs[x][0])
            output_string += result.text + "\t"

        # Print the most recent non-zero sale price and date
        # handle case where there isn't a value for either - just insert ""
        recentSale = soup.find(id=saleDomIDs[0][0]).text
        table = soup.find(
            lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
                'id'] == "MainContent_grdSales")
        rows = table.findAll(lambda tag: tag.name == 'tr')
        prevSalesStr = ""
        for x in range(1,len(rows)):
            vals = rows[x].contents
            if vals[2].text == "$0" or vals[2].text == recentSale: # no new info
                continue
            prevSalesStr += vals[2].text + "\t" + vals[6].text + "\t"
            break
        if prevSalesStr == "":
            prevSalesStr = "\t\t"
        output_string += prevSalesStr

        # Tack on a time stamp and row counter in separate columns
        output_string += current_time + "\t%d"%(recordCount)
        print(output_string, file=fo)
        print(output_string)

if __name__ == "__main__":
    sys.exit(main())


