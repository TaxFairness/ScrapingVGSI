'''
Scrape VGSI Records

Retrieve VGSI records from their server (http://gsi.vgsi.com),
then parse out interesting fields from the resulting HTML responses.

Input is a CSV file that contains a list of "VisionID"s, one per line.
Default is set in Edit Configurations...

Output is several tab-delimited files written to the current directory:

- ScrapeDataXX.tsv # ScrapeDataXX
- OwnerHistory.tsv # Ownership History
- ApprlHistory.tsv # Appraisal History
- AssmtHistory.tsv # Assessment History
- Buildings___.tsv # Buildings
'''

import sys
import argparse
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from playsound import playsound
# import random

import re
# import os
from http.client import HTTPConnection
# from requests.exceptions import HTTPError, ConnectionError

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
            if line.find("#") != -1:
                continue  # Comment line - keep looking
            else:
                break
                
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
# ownershipHistoryID = "MainContent_grdSales"

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
        if domIDs[x][1] == "Book&Page":  # add column headings for Book & Page
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


def handleOwnerHistory(theSoup, theID, pid):
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
                cellCols.append(plainValue(cell.string))
            if len(cellCols) == 4:              # When adding the Book&Page
                bnp = splitBookAndPage(cell)
                cellCols.append(bnp[0])         # add in separate Book
                cellCols.append(bnp[1])         # and Page
        if len(cellCols) == 7:                  # add in "-" for Instrument if it's missing
            cellCols.insert(6, "-")             # (sometimes it is)
        if len(cellCols) != 0:
            cellCols.insert(0, pid)     # put pid at the front
            cellCols.append(current_date)
            outputStr += "\t".join(cellCols)    # output all the columns
            outputStr += "\n"                   # and a newline
    return outputStr

'''
handleAppAssHistory

Return a string containing a set of lines that represent the Appraised or Assessed History.
Each line has a \n, when it's output, don't add another one.

Parameters:
- theSoup - the entire page
- theID - the table ID to parse
- pid - the PID associated with this property

Each table includes: Year, Improvements, Land, Total, PID, CollectedOn
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
            if cell:
                cellCols.append(plainValue(cell.text))
        if len(cellCols) == 1:
            cellCols[0] = "No Data for PID"
            cellCols.append("")
            cellCols.append("")
            cellCols.append("")
        if len(cellCols) != 0:
            cellCols.insert(0, pid)    # put pid at the front
            cellCols.append(current_date)
            outputStr += "\t".join(cellCols)    # output all the columns
            outputStr += "\n"                   # and a newline
    return outputStr
    
'''
handleBuildings

Return a string that represents the buildings on the parcel, one line per building
Parameters:
- theSoup - the entire page
- theID - Should be "" - this code knows which tables to parse
- pid - the PID associated with this property

Each building's line includes:
PID, Building Number, Year built, Living Area, Replacement Cost, Percent Good, Value less Depreciation,
Style, Model,Stories, Total BR, Total Bath, Total Half-bath, Total Rooms, Num Kitchens,
Gross floor area, Living Area,
CollectedOn

Notes:
 - must iterate through each of the buildings, replacing "**" in the domID
    with 01, 02, 03 until no such DOM element
 - Clean up random legends within data fields using plainValue()
'''

buildingIDs = [
    ["MainContent_ctl**_lblYearBuilt","Year Built"],
    ["MainContent_ctl**_lblBldArea","Living Area"],
    ["MainContent_ctl**_lblRcn","Replacement Cost"],
    ["MainContent_ctl**_lblPctGood","Percent Good"],
    ["MainContent_ctl**_lblRcnld","Value after Depreciation"]
]
buildingAttributeTable = "MainContent_ctl**_grdCns"
buildingAreaTable = "MainContent_ctl**_grdSub"
buildingAttrs = [
    "Style",
    "Model",
    "Grade",
    "Stories",
    "Total Bedrooms",
    "Total Bthrms",
    "Total Half Baths",
    "Total Rooms",
    "Num Kitchens"
]
'''
subsBuilding - takes a DOM ID (a string) with embedded "**"
and substitutes the two-digit building number
'''
def subsBuilding(domID, bldg):
    str1 = "0" + str(bldg)
    str2 = str1[-2:]
    return domID.replace("**",str2)

'''
plainValue() - Return a "plain value" string from the Vision value
Remove Dollar sign and commas
Remove selected strings (Rooms, Room, Stories, Story, etc.)
Convert 1/2 and 3/4 to .5 and .75
Convert mm/dd/yyyy to yyyy-mm-dd
'''
def plainValue(val):
    date_pattern = r"(\d{2})/(\d{2})/(\d{4})"
    retval = val
    if isinstance(retval, str):
        if val == "":                           # empty string - return ""
            return ""
        if val.find("MISSING") >= 0:            # Contains "MISSING", return it
            return retval
        if re.match(date_pattern, val):         # Matches date mm/dd/yyyy
            return re.sub(date_pattern, r"\3-\1-\2", val)
        if val[0] == "$":                       # Dollar value: remove $ & ","
            retval = val.replace("$","")        # never any cents so
            retval = retval.replace(",","")     # don't worry about ".##"
            return retval
        retval = retval.replace(" Rooms","")    # remove odd strings
        retval = retval.replace(" Room","")
        retval = retval.replace(" Stories","")
        retval = retval.replace(" Story","")
        retval = retval.replace(" Bedrooms","")
        retval = retval.replace(" Bedroom","")
        retval = retval.replace(" 1/2",".5")    # and fractions
        retval = retval.replace(" 3/4",".75")
    return retval

'''
printBuildingHeader()
Return a line containing the headings for the Buildings file
'''
def printBuildingHeader():
    hdr = "PID\tBuilding #\t"
    for x in range(len(buildingIDs)):
        hdr += "%s\t" % buildingIDs[x][1]
    for x in range(len(buildingAttrs)):
        hdr += "%s\t" % buildingAttrs[x]
    hdr += "Gross Floor Area\tLiving Area\t"
    hdr += "CollectedOn"
    return hdr


'''
The main function
'''
def handleBuildings(theSoup, theID, pid):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    retstr = ""
    buildingNumber = 1
    while True:
        anID = subsBuilding(buildingIDs[0][0], buildingNumber)
        if theSoup.find(id=anID) == None:
            break
            
        # First output the PID
        retstr += "%s\t%d\t" % (pid, buildingNumber)
        
        # Print the list of DOM items from buildingIDs
        for x in range(len(buildingIDs)):
            result = theSoup.find(id=subsBuilding(buildingIDs[x][0],buildingNumber))
            retstr += "%s\t" % plainValue(result.text)
        
        # Print the list of items from Building Attribute Table
        for x in range(len(buildingAttrs)):
            tableID = subsBuilding(buildingAttributeTable,buildingNumber)
            table = theSoup.find('table',{'id': tableID})
            theAttr = buildingAttrs[x]
            label_cell = table.find('td', text=theAttr)
            if label_cell == None:  # does the label need a ":"?
                theAttr += ":"
                label_cell = table.find('td', text=theAttr)
            if label_cell != None: #
                value_cell = label_cell.find_next_sibling('td')
                theValue = value_cell.text
            else:
                theValue = "MISSING-"+theAttr # if it's still None, then insert "MISSING"
            retstr += "%s\t" % plainValue(theValue)
        
        # Find the last row of the right-hand table
        # display the Gross Floor Area and the Living Area
        tableID = subsBuilding(buildingAreaTable, buildingNumber)
        table = theSoup.find('table', {'id': tableID})
        last_row = table.find_all('tr')[-1]
        values = []
        for cell in last_row.find_all('td'):
            values.append(cell.text.strip())
        if len(values) == 4:
            gross=values[2]
            living=values[3]
        else:
            gross = "MISSING-Gross"
            living = "Missing-Living"
        retstr += "%s\t%s\t" % (plainValue(gross), plainValue(living))
        
        retstr += "%s\n" % current_date

        # And on to the next one
        buildingNumber += 1

    return retstr
'''
splitBookAndPage - split the book and page (in BBBB/PPPP format)
    into BBBB\tPPPP\t columns
'''


def splitBookAndPage(bnp):
    ary = bnp.text.split("/")
    return ary

'''
beep - play a short beep sound
Beep .mp3 file from https://www.soundjay.com/beep-sounds-1.html
'''
def beep():
    playsound('TestData/beep-02.mp3')


'''
getNewPage() - request next PID from the infile, return the page and the PID
Delay for a while if the Vision server gives an error/refusing to return result
'''


def getNextPage(infile, fe):
    ids = infile.readNextVisionID()
    if not ids:  # EOF
        return [None, 0]
    
    # if not theArgs.debug:
    time.sleep(0.5)
        # time.sleep(10 + 5 * random.random())  # wait a few seconds before next query
    
    thePID = ids[0]
    url = "https://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s" % thePID
    
    # if theArgs.debug:
    #     print(url, file=fe)
    
    page = None
    while page is None:
    
        try:
            HTTPConnection.debuglevel = 0
            requests.packages.urllib3.disable_warnings()
            page = requests.get(url, verify=False)
            return [page, thePID]
        # See https://stackoverflow.com/questions/9054820/python-requests-exception-handling/57239688#57239688
        except requests.exceptions.RequestException as e:  # might catch all exceptions?
            beep()
            output_string = "Exception retrieving PID %s: Waiting to retry..." % (
                ids[0])
            print(output_string, file=fe)
            page = None
            time.sleep(20)


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
    
    # beep()
    
    # print(output_date)
    fi = theArgs.infile  # the argument parsing returns open file objects
    fe = theArgs.errfile
    # fo = theArgs.outfile
    fo     = open("ScrapeDataXX.tsv", "wt")  # ScrapeDataXX
    fowner = open("OwnerHistory.tsv", "wt")  # Ownership History
    fapprl = open("ApprlHistory.tsv", "wt")  # Appraisal History
    fassmt = open("AssmtHistory.tsv", "wt")  # Assessment History
    fbldgs = open("Buildings___.tsv", "wt")  # Buildings

    infile = VisionIDFile(fi)
    
    # Print the heading row, with all the column names
    output_string = displayHeading()
    print(output_string, file=fo)
    print("PID\tOwner\tSale Price\tCertificate\tBook&Page\tBook\tPage\tInstrument\tSale Date\tCollectedOn", file=fowner)
    print("PID\tApp. Year\tImprovements\tLand\tTotal\tCollectedOn", file=fapprl)
    print("PID\tAss. Year\tImprovements\tLand\tTotal\tCollectedOn", file=fassmt)
    print(printBuildingHeader(), file=fbldgs)
    
    recordCount = 0
    while True:
        recordCount += 1
        [page, thePID] = getNextPage(infile, fe)  # Get the next record from Vision
        
        if page is None:
            break
        
        inStr = page.text
        if inStr.find(
                'There was an error loading the parcel') >= 0:  # string present
            output_string = "\tProblem loading parcel PID\t%s" % (thePID)
            print(output_string, file=fo)
            continue
        
        soup = BeautifulSoup(page.content, "html.parser")
        
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # First print the random fields from the page
        output_string = ""
        for x in range(len(domIDs)):
            result = soup.find(id=domIDs[x][0])
            output_string += "%s\t" % plainValue(result.text)
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
            output_string += "%s\t" % plainValue(result.text)
        
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
            if vals[2].text == "$0" or vals[2].text == recentSale:  # no new info
                continue
            dateIx = len(vals) - 2  # sometimes five columns, sometimes 6 :-(
            prevSalesStr += "%s\t%s\t" % (plainValue(vals[2].text), plainValue(vals[dateIx].text))
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
            ass_imp = plainValue(vals[2].text)
            ass_land = plainValue(vals[3].text)
            ass_tot = plainValue(vals[4].text)
        except:
            appr = ""
        output_string += "%s\t%s\t%s\t" % (ass_imp, ass_land, ass_tot)
        # Then get Previous Assessed Improvements/Land/Total
        try:
            vals = rows[2].contents
            ass_imp = plainValue(vals[2].text)
            ass_land = plainValue(vals[3].text)
            ass_tot = plainValue(vals[4].text)
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
            appr_imp = plainValue(vals[2].text)
            appr_land = plainValue(vals[3].text)
            appr_tot = plainValue(vals[4].text)
        except:
            appr = ""
        output_string += "%s\t%s\t%s\t" % (appr_imp, appr_land, appr_tot)
        
        # Then get Previous Appraised Improvements/Land/Total
        try:
            vals = rows[2].contents
            appr_imp = plainValue(vals[2].text)
            appr_land = plainValue(vals[3].text)
            appr_tot = plainValue(vals[4].text)
        except:
            appr = ""
        output_string += "%s\t%s\t%s\t" % (appr_imp, appr_land, appr_tot)
        
        # Tack on time stamp, row counter in separate columns
        output_string += "%s\t%d" % (current_time, recordCount)
        print(output_string, file=fo)
        print(output_string)

        # Output the recent ownership history into a separate file
        histStr = handleOwnerHistory(soup, "MainContent_grdSales", thePID)
        print(histStr, file=fowner, end="")
        # Output the history of the Appraisals
        histStr = handleAppAssHistory(soup, "MainContent_grdHistoryValuesAppr", thePID)
        print(histStr, file=fapprl, end="")
        # Output the history of the Assessments
        histStr = handleAppAssHistory(soup, "MainContent_grdHistoryValuesAsmt", thePID)
        print(histStr, file=fassmt, end="")
        # Output information about each building
        histStr = handleBuildings(soup, "", thePID)
        print(histStr, file=fbldgs, end="")
        
    # And we're done
    beep()
    time.sleep(0.5)
    beep()
    time.sleep(0.5)
    beep()
    
if __name__ == "__main__":
    sys.exit(main())
