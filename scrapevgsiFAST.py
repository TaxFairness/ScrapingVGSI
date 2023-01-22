'''
Scrape VGSI Records

Retrieve VGSI records from their server (http://gsi.vgsi.com),
then parse out interesting fields from the resulting HTML responses.

Input is a CSV file that contains a list of "VisionID"s in this format:

Output is a TSV file that contains the fields selected  using the #id fields
from the HTML file. Those IDs are contained in an array of text strings.
'''

import sys
import argparse
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import beepy as beep

# import re
import os
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError

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
        output_string += "%s\t" % domIDs[x][1]
        if domIDs[x][1] == "MBLU":  # add column headings for expanded MBLU
            output_string += "Map\tLot\tUnit\tSub\t"
        if domIDs[x][1] == "Book&Page": # add column headings for Book & Page
            output_string += "Book\tPage\t"
    # for x in range(len(tableIDs)):
    #     output_string += tableIDs[x] + "\t"
    for x in range(len(saleTableIDs)):
        output_string += "%s\t" % saleTableIDs[x]
    for x in range(len(valuationHistoryIDs)):
        output_string += "%s\t" % valuationHistoryIDs[x]
    output_string += "CollectedOn\tRecord#"
    return output_string

'''
handleOwnerHistory

Return a string containing a set of lines that represent the Ownership History.
Includes: Owner, Sale Price, Certificate, Book&Page, Instrument, Sale Date
'''
def handleOwnerHistory(theSoup, pid):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    historyTable = theSoup.find(id=ownershipHistoryID)
    htRows = historyTable.find_all('tr')
    outputStr = ""
    for row in htRows:                          # for each row of the history table
        cells = row.findChildren('td')          # get the cells into an array
        cellCols = []
        for cell in cells:
            if cell != []:
                cellCols.append(cell.string)
            if len(cellCols) == 4:              # When adding the Book&Page
                bnp = splitBookAndPage(cell)
                cellCols.append(bnp[0])         # add in separate Book
                cellCols.append(bnp[1])         # and Page
        if len(cellCols) == 7:                  # add in "-" for Instrument if it's missing
            cellCols.insert(6,"-")              # (sometimes it is)
        if len(cellCols) != 0:
            cellCols.append(pid)                # put pid on the end
            cellCols.append(current_date)
            outputStr += "\t".join(cellCols)    # output all the columns
            outputStr += "\n"                   # and a newline
    return outputStr

'''
handleAppAssHistory

Return a string containing a set of lines that represent the Appraised or Assessed History.
Parameters:
- theSoup - the entire page
- theID - the table ID to parse
- pid - the PID associated with this property

Each table includes: Year, Improvements, Land, Total, CollectedOn
'''
def handleAppAssHistory(theSoup, theID, pid):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    historyTable = theSoup.find(id=theID)
    htRows = historyTable.find_all('tr')
    outputStr = ""
    for row in htRows:                          # for each row of the history table
        cells = row.findChildren('td')          # get the cells into an array
        cellCols = []
        for cell in cells:
            if cell != []:
                cellCols.append(cell.string)
        if len(cellCols) != 0:
            cellCols.append(pid)                # put pid on the end
            cellCols.append(current_date)
            outputStr += "\t".join(cellCols)    # output all the columns
            outputStr += "\n"                   # and a newline
    return outputStr

'''
splitBookAndPage - split the book and page (in BBBB/PPPP format)
    into BBBB\tPPPP\t columns
'''
def splitBookAndPage(bnp):
    ary = bnp.text.split("/")
    return ary

'''
beep - claimed to work on macOS
https://stackoverflow.com/a/24634221/1827982
'''
def beep():
    os.system("printf '\a'")  # or '\7'


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
    fo = open("FASTScrapedData_%s.tsv"%output_date, "wt")
    fowner = open("FASTOwnerHistory_%s.tsv"%output_date, "wt") # Ownership History
    fapprl = open("FASTApprlHistory_%s.tsv"%output_date, "wt") # Appraisal History
    fassmt = open("FASTAssmtHistory_%s.tsv"%output_date, "wt") # Assessment History

    infile = VisionIDFile(fi)
    
    # Print the heading row, with all the column names
    output_string = displayHeading()
    print(output_string, file=fo)
    print("Owner\tSale Price\tCertificate\tBook&Page\tBook\tPage\tInstrument\tSale Date\tPID\tCollectedOn\n",file=fowner)
    print("Ass. Year\tImprovements\tLand\tTotal\tPID\tCollectedOn\n",file=fapprl)
    print("App. Year\tImprovements\tLand\tTotal\tPID\tCollectedOn\n",file=fassmt)

    beep()
    
    from http.client import HTTPConnection
    
    recordCount = 0
    while True:
        recordCount += 1
        ids = infile.readNextVisionID()
        if ids == []:  # EOF
            break
        
        # if not theArgs.debug:
        time.sleep(0.5)  # wait 2 seconds before next query
            
        thePID = ids[0]
        url = "https://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s" % (thePID)
        
        if theArgs.debug:
            print(url, file=fe)
        
        try:
            HTTPConnection.debuglevel = 0
            requests.packages.urllib3.disable_warnings()
            page = requests.get(url, verify=False)
        except ConnectionError as e:
            beep()
            # print(e.response.text)
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
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # First print the random fields from the page
        output_string = ""
        for x in range(len(domIDs)):
            result = soup.find(id=domIDs[x][0])
            output_string += "%s\t" % result.text
            if domIDs[x][0] == "MainContent_lblBp": # split Book&Page
                ary = splitBookAndPage(result)
                output_string += "%s\t%s\t" % (ary[0], ary[1])
            if domIDs[x][0] == "MainContent_lblMblu":  # also split MBLU
                ary = result.text.split("/")
                output_string += "%s\t%s\t%s\t%s\t" % (ary[0].strip(), ary[1].strip(), ary[2].strip(), ary[3].strip())

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
            output_string += "%s\t" % result.text
        
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
            prevSalesStr += "%s\t%s\t" % (vals[2].text, vals[dateIx].text)
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
        output_string += "%s\t%s\t%s\t" % (ass_imp, ass_land, ass_tot)
        # Then get Previous Assessed Improvements/Land/Total
        try:
            vals = rows[2].contents
            ass_imp = vals[2].text
            ass_land = vals[3].text
            ass_tot = vals[4].text
        except:
            appr = ""
        output_string += "%s\t%s\t%s\t" % (ass_imp, ass_land, ass_tot)
        
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
        output_string += "%s\t%s\t%s\t" % (appr_imp, appr_land, appr_tot)
        
        # Then get Previous Appraised Improvements/Land/Total
        try:
            vals = rows[2].contents
            appr_imp = vals[2].text
            appr_land = vals[3].text
            appr_tot = vals[4].text
        except:
            appr = ""
        output_string += "%s\t%s\t%s\t" % (appr_imp, appr_land, appr_tot)
        
        # Tack on time stamp, row counter in separate columns
        output_string += "%s\t%d" % (current_time, recordCount)
        print(output_string, file=fo)
        print(output_string)

        # Output the recent ownership history into a separate file
        histStr = handleOwnerHistory(soup, thePID)
        print(histStr, file=fowner)
        # Output the history of the Appraisals
        histStr = handleAppAssHistory(soup, "MainContent_grdHistoryValuesAppr" ,thePID)
        print(histStr, file=fapprl)
        # Output the history of the Assessments
        histStr = handleAppAssHistory(soup, "MainContent_grdHistoryValuesAsmt" ,thePID)
        print(histStr, file=fassmt)


if __name__ == "__main__":
    sys.exit(main())
