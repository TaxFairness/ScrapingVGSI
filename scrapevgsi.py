'''
Scrape VGSI Records

Retrieve VGSI records from their server (http://gsi.vgsi.com),
then parse out interesting fields from the resulting HTML responses.

Input is a CSV file that contains a list of "VisionID"s in this format:

# Source: David Robbins, Lyme Planning and Zoning - 6Apr2021
# Mapping between Vision ID and the tax map/lot number
VisionID    TaxMap    Lot
123    201    86
125    201    88
127    201    90

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

# import re
# import os

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
                return []  # hit EOF
            if line[0] != "#":
                break  # Non-comment line - break out of loop
        
        vals = line.strip().split(",")
        return vals


# IDs of DOM elements whose values should be plucked up and displayed
domIDs = [
    ["MainContent_lblPid", "PID"],
    ["MainContent_lblGenOwner", "Owner"],
    ["MainContent_lblLocation", "Street Address"],
    ["MainContent_lblMblu", "MBLU"],
    ["MainContent_lblBp", "Book&Page"],
    ["MainContent_lblGenAssessment", "Assessment"],
    ["MainContent_lblGenAppraisal", "Appraisal"],
    ["MainContent_lblLndAcres", "Lot Size (acres)"],
    ["MainContent_lblUseCode", "Land Use Code"],
    ["MainContent_lblUseCodeDescription", "Description"],
    ["MainContent_lblZone", "Zoning District"],
    ["MainContent_lblBldCount", "# Buildings"],
]
# Don't retrieve here - use the Appraisal/Assessment tables at bottom of page
# tableIDs = [
#     "Appr. Year",
#     "Improvements",
#     "Land",
#     "Total",
# ]
saleDomIDs = [
    ["MainContent_lblPrice", "Recent Sale Price", ],
    ["MainContent_lblSaleDate", "Recent Sale Date"]
]
saleTableIDs = [
    "Recent Sale Price",
    "Recent Sale Date",
    "Prev Sale Price",
    "Prev Sale Date",
]
valuationHistoryIDs = [
    "Curr. Ass. Imp",
    "Curr. Ass. Land",
    "Curr. Ass. Tot",
    "Prev. Ass. Imp",
    "Prev. Ass. Land",
    "Prev. Ass. Tot",
    "Curr. App. Imp",
    "Curr. App. Land",
    "Curr. App. Tot",
    "Prev. App. Imp",
    "Prev. App. Land",
    "Prev. App. Tot"
]
ownershipHistoryID = "MainContent_grdSales"

'''
displayHeading

Return a string containing all the headings for the output file
'''
def displayHeading():
    # Print the heading row, with all the column names
    output_string = ""
    for x in range(len(domIDs)):
        output_string += domIDs[x][1] + "\t"
        if domIDs[x][1] == "MBLU":
            output_string += "Map\tLot\tUnit\tSub\t"
        if domIDs[x][1] == "Book&Page":
            output_string += "Book\tPage\t"
    # for x in range(len(tableIDs)):
    #     output_string += tableIDs[x] + "\t"
    for x in range(len(saleTableIDs)):
        output_string += saleTableIDs[x] + "\t"
    for x in range(len(valuationHistoryIDs)):
        output_string += valuationHistoryIDs[x] + "\t"
    output_string += "Time\tRecord#\tCollectedOn"
    return output_string

'''
handleOwnershipHistory

Return a string containing a set of lines that represent the Ownership History.
Includes: Owner, Sale Price, Certificate, Book&Page, Instrument, Sale Date
'''
def handleOwnershipHistory(theSoup, pid):
    historyTable = theSoup.find(id=ownershipHistoryID)
    htRows = historyTable.find_all('tr')
    outputStr = ""
    for row in htRows:
        cells = row.findChildren('td')
        cellCols = []
        for cell in cells:
            if cell != []:
                cellCols.append(cell.string)
        if len(cellCols) == 5:
            cellCols.insert(4,"-")
        if len(cellCols) != 0:
            outputStr += "\t".join(cellCols) + "\t" + pid + "\n"
    return outputStr

'''
Main Function

Parse arguments
Scan through file
Build up dictionary for each IP address

'''


def main(argv=None):
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?',
                            type=argparse.FileType('rU'), default=sys.stdin)
        # parser.add_argument("-o", '--outfile', nargs='?',
        #                     type=argparse.FileType('w'), default=sys.stdout)
        parser.add_argument("-e", '--errfile', nargs='?',
                            type=argparse.FileType('w'), default=sys.stderr)
        parser.add_argument('-d', '--debug', action="store_true",
                            help="Enable the debug mode.")
        theArgs = parser.parse_args()
    except:
        return "Error parsing arguments"

    output_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # print(output_date)
    fi = theArgs.infile  # the argument parsing returns open file objects
    fe = theArgs.errfile
    # fo = theArgs.outfile
    fo = open("ScrapedData_%s.tsv"%output_date, "wt")
    fh = open("OwnershipHistory_%s.tsv"%output_date, "wt") # Ownership History
    
    infile = VisionIDFile(fi)
    
    # Print the heading row, with all the column names
    output_string = displayHeading()
    print(output_string, file=fo)
    print("Owner\tSale Price\tCertificate\tBook&Page\tInstrument\tSale Date\tPID\n",file=fh)
    
    from http.client import HTTPConnection
    
    recordCount = 0
    while True:
        recordCount += 1
        ids = infile.readNextVisionID()
        if ids == []:  # EOF
            break
        
        if not theArgs.debug:
            time.sleep(
                10 + 5 * random.random())  # wait a few seconds before next query
        
        url = "https://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s" % (ids[0])
        
        if theArgs.debug:
            print(url, file=fe)
        
        try:
            HTTPConnection.debuglevel = 0
            requests.packages.urllib3.disable_warnings()
            page = requests.get(url, verify=False)
            from requests.exceptions import HTTPError
        except HTTPError as e:
            print(e.response.text)
            output_string = "%s\tCan't reach the server\t\t\t%s?\t%s?" % (
                ids[0], ids[1], ids[2])
            print(output_string, file=fo)
            continue
        
        inStr = page.text
        if inStr.find(
                'There was an error loading the parcel') >= 0:  # string present
            output_string = \
                "%s\tProblem loading parcel PID %s, Map %s Lot %s" % (
                ids[0], ids[0], ids[1], ids[2])
            print(output_string, file=fo)
            continue
        
        soup = BeautifulSoup(page.content, "html.parser")
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        
        # First print the random fields from the page
        output_string = ""
        for x in range(len(domIDs)):
            result = soup.find(id=domIDs[x][0])
            output_string += result.text + "\t"
            if domIDs[x][0] == "MainContent_lblBp": # also split Book&Page
                ary = result.text.split("/")
                output_string += ary[0] + "\t" + ary[1] + "\t"
            if domIDs[x][0] == "MainContent_lblMblu":  # also split MBLU
                ary = result.text.split("/")
                output_string += ary[0].strip() + "\t" + ary[1].strip() + "\t" + ary[2].strip() + "\t" + ary[3].strip() + "\t"

        # # Print the most recent appraisal date, Improvements, Land, and Total
        # table = soup.find(
        #     lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "MainContent_grdCurrentValueAppr")
        # rows = table.findAll(lambda tag: tag.name == 'tr')
        # vals = rows[1].contents # contents of the row
        # for x in range(1,5):
        #     output_string += vals[x].text + "\t"
        
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
        for x in range(1, len(rows)):
            vals = rows[x].contents
            if vals[2].text == "$0" or vals[
                2].text == recentSale:  # no new info
                continue
            dateIx = len(vals) - 2  # sometimes five columns, sometimes 6 :-(
            prevSalesStr += vals[2].text + "\t" + vals[dateIx].text + "\t"
            break
        if prevSalesStr == "":
            prevSalesStr = "\t\t"
        output_string += prevSalesStr
        
        # Grab the most recent Assessment from the Valuation History
        table = soup.find(
            lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
                'id'] == "MainContent_grdHistoryValuesAsmt")
        rows = table.findAll(lambda tag: tag.name == 'tr')
        ass_imp = ""
        ass_land = ""
        ass_tot = ""
        # First get Current Assessed Improvements/Land/Total
        try:
            vals = rows[1].contents
            ass_imp = vals[2].text
            ass_land = vals[3].text
            ass_tot = vals[4].text
        except:
            appr = ""
        output_string += ass_imp + "\t" + ass_land + "\t" + ass_tot + "\t"
        # Then get Previous Assessed Improvements/Land/Total
        try:
            vals = rows[2].contents
            ass_imp = vals[2].text
            ass_land = vals[3].text
            ass_tot = vals[4].text
        except:
            appr = ""
        output_string += ass_imp + "\t" + ass_land + "\t" + ass_tot + "\t"
        
        # Grab the most recent Appraisal from the Valuation History
        table = soup.find(
            lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
                'id'] == "MainContent_grdHistoryValuesAppr")
        rows = table.findAll(lambda tag: tag.name == 'tr')
        # First get Current Appraised Improvements/Land/Total
        appr_imp = ""
        appr_land = ""
        appr_tot = ""
        try:
            vals = rows[1].contents
            appr_imp = vals[2].text
            appr_land = vals[3].text
            appr_tot = vals[4].text
        except:
            appr = ""
        output_string += appr_imp + "\t" + appr_land + "\t" + appr_tot + "\t"
        
        # Then get Previous Appraised Improvements/Land/Total
        try:
            vals = rows[2].contents
            appr_imp = vals[2].text
            appr_land = vals[3].text
            appr_tot = vals[4].text
        except:
            appr = ""
        output_string += appr_imp + "\t" + appr_land + "\t" + appr_tot + "\t"
        
        # Tack on time stamp, row counter, current_date in separate columns
        
        output_string += "%s\t%d\t%s" % (current_time, recordCount, current_date)
        print(output_string, file=fo)
        print(output_string)

        # and output the recent ownership history into a separate file
        histStr = handleOwnershipHistory(soup, ids[0])
        print(histStr, file=fh)

if __name__ == "__main__":
    sys.exit(main())
