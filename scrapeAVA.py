'''
Scrape AVA Records from Grafton County Register of Deeds

Input is a HTML file that contains a list of records.

Output is a TSV file that contains the fields selected  using the #id fields
from the HTML file. Those IDs are contained in an array of text strings.

'''

import sys
import argparse

import bs4.element
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random

import re
import os


def main(argv=None):
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?',
                            type=argparse.FileType('rU'), default=sys.stdin)
        parser.add_argument("-o", '--outfile', nargs='?',
                            type=argparse.FileType('w'), default=sys.stdout)
        parser.add_argument("-e", '--errfile', nargs='?',
                            type=argparse.FileType('w'), default=sys.stderr)
        parser.add_argument('-d', '--debug', action="store_true",
                            help="Enable the debug mode.")
        theArgs = parser.parse_args()
    except:
        return "Error parsing arguments"

    fi = theArgs.infile  # the argument parsing returns open file objects
    fo = theArgs.outfile
    fe = theArgs.errfile

    soup = BeautifulSoup(fi, 'html.parser')
    print(soup.prettify(), file=fo)

    xactions = soup.find_all("button", class_="font-semibold")
    # print(first_xaction.parent.parent.prettify())
    # print(list(xaction.parent.parent))

    headings = [ "ID", "Date", "Type", "-", "Book&Page", "Pages", "Party1", "Party2", "Legal", "Notes", "Return to", "Consideration", "Assoc. Docs"]
    header = "\t".join(headings)
    print(header)

    # 7 (Isset) first test case
    # 31 (Menard) has "Consideration"
    # 33 (Santaw) has "additional documents"
    # 35 (Rusch) has two additional documents
    # xaction = xactions[35]
    # print_xaction(xaction.parent.parent.parent)

    for xaction in xactions:
        print_xaction(xaction.parent.parent.parent)

def print_xaction(x):
    entire_contents = x.contents
    # print(repr(entire_contents))
    cols = x.find_all(class_="w-1/4")
    # print(len(cols))
    # print("Entire Transaction: ", len(entire))
    # print(len(entire_contents), " items in entire")
    transaction_line = print_firstcol(cols[0])
    transaction_line += "\t" + print_partycol(cols[1])
    transaction_line += "\t" + print_legalcol(cols[2])
    transaction_line += "\t" + print_finalcol(cols[3])
    print(transaction_line)

def print_firstcol(col):
    firstcol = col.contents # return a list of the contents
    # print(len(something), " items in something")
    # summary=firstcol[0].contents
    # print(len(summary), " items in summary")
    # print(summary)
    line = firstcol[2].text
    # print("ID: ",summary[2].text)
    for child in firstcol[4]:
        # print("Type: ",type(child))
        if type(child) == bs4.element.Tag:
            t = child.text
            if t == "":
                t = "-"
            line += "\t" + t
            # print(child.text)
    return line

def print_partycol(col):
    # Print Parties
    # print("==========")
    # print(repr(cols[1]))

    partycol = col # return a list of the contents
    # print("Parties: ",partycol)
    parties = partycol.find_all("label")
    # print(len(partycol))
    partynames = [ "", "", ""]
    inparty = 0
    line = ""
    for party in parties:
        if party.text == "Party 1:":
            inparty = 1
        elif party.text == "Party 2:":
            inparty = 2
        elif party.text == "Parties":
            continue
        else:
            if partynames[inparty] != "":
                partynames[inparty] = partynames[inparty] + ", "
            partynames[inparty] = partynames[inparty] + party.text.strip()
                # .replace(" ETA "," ")
        # print(partynames)
    line += partynames[1] + "\t" + partynames[2]
    # print(line)
    return line

    # Print the "legal stuff"
def print_legalcol(col):
    # print(repr(col))
    return "Lyme"

# Print the "final stuff"
# Parse out:
#   - Notes
#   - Return to
#   - Consideration
#   - Associated Documents

def print_finalcol(col):
    # print("Final Column")
    # print(repr(col))
    final = col.find_all("label")
    # print(len(final))
    finalnames = ["-", "-", "-", "-", "-"]
    whichname = 0
    for item in final:
        # print(item.text)
        if item.text == "Notes:":
            whichname = 1
        elif item.text == "Return To:":
            whichname = 2
        elif item.text == "Consideration:":
            whichname = 3
        elif item.text == "Associated Documents":
            whichname = 4
        elif item.text == "Additional":
            continue
        else:
            update_names(finalnames, whichname, item)
    final = col.find_all("a")
    for item in final:
        # print(item.text)
        update_names(finalnames, 4, item)
    # print(finalnames)
    line = finalnames[1] + "\t" + finalnames[2] + "\t" + finalnames[3] + "\t" + finalnames[4]
    return line

def update_names(finalnames, whichname, item):
    if finalnames[whichname] == "-":
        finalnames[whichname] = ""
    if whichname == 2 and finalnames[2] != "":  # Just add lawyer's name, not address
        return
    if finalnames[whichname] != "":  # add ", " if something's there
        finalnames[whichname] = finalnames[whichname] + ", "
    finalnames[whichname] = finalnames[whichname] + item.text.strip()
    # .replace(" ETA "," ")

    # print("--- and the repr() ---")
    # print(repr(x))
    # xid = x.find(class_="font-semibold")
    # print(xid.text)
    # print(repr(xid.next_sibling.next_sibling))
    # print(repr(xid.next_sibling.next_sibling.next_sibling))
    # xdetails = x.find_all("label", class_="block")
    # print(len(xdetails))
    # print(xdetails.text)
    # for y in xdetails:
    #     print(y.text)
    # print("Hi Rich!")
    # chillins = soup.find_all('div', class_='rounded-sm pb-2 bg-white')
    # print(len(chillins))
    # print(list(chillins))
    # for child in soup.contents[1].children:
    #     print(child)

# --- the remainder of this code was cut out of the scrapvgsi.py app
# # from collections import OrderedDict
#
# """
# readNextVisionID(f)
#
# Reads a line from the input file, and returns the three comma-separated fields.
# Ignore lines that begin with # (they're comments)
# Return "" to signal EOF)
#
# """
#
#
# class VisionIDFile:
#     def __init__(self, file):
#         self.theFile = file
#
#     def readNextVisionID(self):
#
#         while True:
#             line = self.theFile.readline()
#             if line == "":
#                 return []  # hit EOF
#             if line[0] != "#":
#                 break  # Non-comment line - break out of loop
#
#         vals = line.strip().split(",")
#         return vals
#
#
# # IDs of DOM elements whose values should be plucked up and displayed
# domIDs = [
#     ["MainContent_lblPid", "PID"],
#     ["MainContent_lblGenOwner", "Owner"],
#     ["MainContent_lblLocation", "Street Address"],
#     ["MainContent_lblMblu", "MBLU"],
#     ["MainContent_lblBp", "Book&Page"],
#     ["MainContent_lblGenAssessment", "Assessment"],
#     ["MainContent_lblGenAppraisal", "Appraisal"],
#     ["MainContent_lblLndAcres", "Lot Size (acres)"],
#     ["MainContent_lblUseCode", "Land Use Code"],
#     ["MainContent_lblUseCodeDescription", "Description"],
#     ["MainContent_lblZone", "Zoning District"],
#     ["MainContent_lblBldCount", "# Buildings"],
# ]
# # Don't retrieve here - use the Appraisal/Assessment tables at bottom of page
# # tableIDs = [
# #     "Appr. Year",
# #     "Improvements",
# #     "Land",
# #     "Total",
# # ]
# saleDomIDs = [
#     ["MainContent_lblPrice", "Recent Sale Price", ],
#     ["MainContent_lblSaleDate", "Recent Sale Date"]
# ]
# saleTableIDs = [
#     "Recent Sale Price",
#     "Recent Sale Date",
#     "Prev Sale Price",
#     "Prev Sale Date",
# ]
# valuationHistoryIDs = [
#     "Curr. Ass. Imp",
#     "Curr. Ass. Land",
#     "Curr. Ass. Tot",
#     "Prev. Ass. Imp",
#     "Prev. Ass. Land",
#     "Prev. Ass. Tot",
#     "Curr. App. Imp",
#     "Curr. App. Land",
#     "Curr. App. Tot",
#     "Prev. App. Imp",
#     "Prev. App. Land",
#     "Prev. App. Tot"
# ]
# '''
# Main Function
#
# Parse arguments
# Scan through file
# Build up dictionary for each IP address
#
# '''
#
#
# def main(argv=None):
#     try:
#         parser = argparse.ArgumentParser(description=__doc__)
#         parser.add_argument("-i", '--infile', nargs='?',
#                             type=argparse.FileType('rU'), default=sys.stdin)
#         parser.add_argument("-o", '--outfile', nargs='?',
#                             type=argparse.FileType('w'), default=sys.stdout)
#         parser.add_argument("-e", '--errfile', nargs='?',
#                             type=argparse.FileType('w'), default=sys.stderr)
#         parser.add_argument('-d', '--debug', action="store_true",
#                             help="Enable the debug mode.")
#         theArgs = parser.parse_args()
#     except:
#         return "Error parsing arguments"
#
#     fi = theArgs.infile  # the argument parsing returns open file objects
#     fo = theArgs.outfile
#     fe = theArgs.errfile
#
#     infile = VisionIDFile(fi)
#
#     # Print the heading row, with all the column names
#     output_string = ""
#     for x in range(len(domIDs)):
#         output_string += domIDs[x][1] + "\t"
#     # for x in range(len(tableIDs)):
#     #     output_string += tableIDs[x] + "\t"
#     for x in range(len(saleTableIDs)):
#         output_string += saleTableIDs[x] + "\t"
#     for x in range(len(valuationHistoryIDs)):
#         output_string += valuationHistoryIDs[x] + "\t"
#     print(output_string, file=fo)
#
#     recordCount = 0
#     while True:
#         recordCount += 1
#         ids = infile.readNextVisionID()
#         if ids == []:  # EOF
#             break
#
#         if not theArgs.debug:
#             time.sleep(
#                 1 + 5 * random.random())  # wait a few seconds before next query
#
#         url = "https://gis.vgsi.com/lymeNH/Parcel.aspx?pid=%s" % (ids[0])
#
#         if theArgs.debug:
#             print(url, file=fe)
#
#         try:
#             page = requests.get(url)
#         except:
#             output_string = "%s\tCan't reach the server\t\t\t%s?\t%s?" % (
#             ids[0], ids[1], ids[2])
#             print(output_string, file=fo)
#             continue
#
#         inStr = page.text
#         if inStr.find(
#                 'There was an error loading the parcel') >= 0:  # string is present
#             output_string = "%s\tProblem loading parcel PID %s, Map %s Lot %s" % (
#             ids[0], ids[0], ids[1], ids[2])
#             print(output_string, file=fo)
#             continue
#
#         soup = BeautifulSoup(page.content, "html.parser")
#
#         now = datetime.now()
#         current_time = now.strftime("%H:%M:%S")
#
#         # First print the random fields from the page
#         output_string = ""
#         for x in range(len(domIDs)):
#             result = soup.find(id=domIDs[x][0])
#             output_string += result.text + "\t"
#
#         # # Print the most recent appraisal date, Improvements, Land, and Total
#         # table = soup.find(
#         #     lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "MainContent_grdCurrentValueAppr")
#         # rows = table.findAll(lambda tag: tag.name == 'tr')
#         # vals = rows[1].contents # contents of the row
#         # for x in range(1,5):
#         #     output_string += vals[x].text + "\t"
#
#         # Print the recent sale price and date
#         for x in range(len(saleDomIDs)):
#             result = soup.find(id=saleDomIDs[x][0])
#             output_string += result.text + "\t"
#
#         # Print the most recent non-zero sale price and date
#         # handle case where there isn't a value for either - just insert ""
#         recentSale = soup.find(id=saleDomIDs[0][0]).text
#         table = soup.find(
#             lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
#                 'id'] == "MainContent_grdSales")
#         rows = table.findAll(lambda tag: tag.name == 'tr')
#         prevSalesStr = ""
#         for x in range(1, len(rows)):
#             vals = rows[x].contents
#             if vals[2].text == "$0" or vals[
#                 2].text == recentSale:  # no new info
#                 continue
#             dateIx = len(vals) - 2  # sometimes five columns, sometimes 6 :-(
#             prevSalesStr += vals[2].text + "\t" + vals[dateIx].text + "\t"
#             break
#         if prevSalesStr == "":
#             prevSalesStr = "\t\t"
#         output_string += prevSalesStr
#
#         # Grab the most recent Assessment from the Valuation History
#         table = soup.find(
#             lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
#                 'id'] == "MainContent_grdHistoryValuesAsmt")
#         rows = table.findAll(lambda tag: tag.name == 'tr')
#         # First get Current Assessed Improvements/Land/Total
#         try:
#             vals = rows[1].contents
#             ass_imp = vals[2].text
#             ass_land = vals[3].text
#             ass_tot = vals[4].text
#         except:
#             appr = ""
#         output_string += ass_imp + "\t" + ass_land + "\t" + ass_tot + "\t"
#         # Then get Previous Assessed Improvements/Land/Total
#         try:
#             vals = rows[2].contents
#             ass_imp = vals[2].text
#             ass_land = vals[3].text
#             ass_tot = vals[4].text
#         except:
#             appr = ""
#         output_string += ass_imp + "\t" + ass_land + "\t" + ass_tot + "\t"
#
#         # Grab the most recent Appraisal from the Valuation History
#         table = soup.find(
#             lambda tag: tag.name == 'table' and tag.has_attr('id') and tag[
#                 'id'] == "MainContent_grdHistoryValuesAppr")
#         rows = table.findAll(lambda tag: tag.name == 'tr')
#         # First get Current Appraised Improvements/Land/Total
#         try:
#             vals = rows[1].contents
#             appr_imp = vals[2].text
#             appr_land = vals[3].text
#             appr_tot = vals[4].text
#         except:
#             appr = ""
#         output_string += appr_imp + "\t" + appr_land + "\t" + appr_tot + "\t"
#
#         # Then get Previous Appraised Improvements/Land/Total
#         try:
#             vals = rows[2].contents
#             appr_imp = vals[2].text
#             appr_land = vals[3].text
#             appr_tot = vals[4].text
#         except:
#             appr = ""
#         output_string += appr_imp + "\t" + appr_land + "\t" + appr_tot + "\t"
#
#         # Tack on a time stamp and row counter in separate columns
#         output_string += current_time + "\t%d" % (recordCount)
#         print(output_string, file=fo)
#         print(output_string)
#

if __name__ == "__main__":
    sys.exit(main())


