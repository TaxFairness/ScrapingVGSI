'''
Scrape AVA Records from Grafton County Register of Deeds

Input is a HTML file that contains a list of records. Create this file
by doing a search on the AVA site at Grafton County, then Inspect Element
and Copy Outer HTML on the entire <html> tag.

Output is a TSV file that contains the fields selected using the #id fields
from the HTML file. Those IDs are contained in an array of text strings.
'''

import sys
import argparse

import bs4.element
# import requests
from bs4 import BeautifulSoup

# import time
from datetime import datetime

# import random
#
# import re
# import os

fi = None
fo = None
fe = None


def main(argv=None):
	try:
		parser = argparse.ArgumentParser(description=__doc__)
		parser.add_argument("-i", '--infile', nargs='?',
							type=argparse.FileType('r'), default=sys.stdin)
		# parser.add_argument("-o", '--outfile', nargs='?',
		# 					type=argparse.FileType('w'), default=sys.stdout)
		parser.add_argument("-e", '--errfile', nargs='?',
							type=argparse.FileType('w'), default=sys.stderr)
		parser.add_argument('-d', '--debug', action="store_true",
							help="Enable the debug mode.")
		theArgs = parser.parse_args()
	except:
		return "Error parsing arguments"
	
	output_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	
	global fi
	fi = theArgs.infile  # the argument parsing returns open file objects
	global fo
	# fo = theArgs.outfile
	fo = open("AVA_Records_%s.tsv" % output_date, "wt")
	global fe
	fe = theArgs.errfile
	
	# Print the header line
	# NB: GCRoD does not display Transfer Tax as a scrapable value.
	# Print a blank column and search GCRoD manually for "DEEED"
	# Enter the Transfer Tax recorded or use "-" where there is none
	# Ignore LCHIP tax - it's the same on virtually all properties
	headings = ["ID", "Date&Time", "Date", "Time", "Type", "Don't_Keep",
				"Book&Page",
				"Book", "Page", "Pages", "Party1",
				"Party2", "Legal", "Notes", "Return to", "Consideration",
				"Assoc. Docs", "Transfer Tax", "CollectedOn"]
	header = "\t".join(headings)
	print(header, file=fo)

	# Parse the HTML
	soup = BeautifulSoup(fi, 'html.parser')
	# print the "prettified" file to stderr
	#print(soup.prettify(), file=fe)
	
	# Find the transactions - Pre-Jan2024, find the parent^3 of the <button>
	# xactions = soup.find_all("button", class_="font-semibold")
	# print(first_xaction.parent.parent.prettify())
	# print(list(xaction.parent.parent))
	# for xaction in xactions:
	# 	print_xaction(xaction.parent.parent.parent)

	# Post Jan2024, Vision created new CSS classes, easier to find
	transactions = soup.find_all("div", class_="resultRowDetailContainer")
	
	for transaction in transactions:
		# foo = transaction.prettify()
		# print(transaction.prettify(), file=fe)
		print_transaction(transaction)

'''
print_transaction() outputs each transaction.
Each transaction consists of four columns of data displayed on the page
Column 1:
- Record number (clickable button to display record)
- Date & Time mm/dd/yyyy hh:mm:ss AM/PM
- Type e.g. "DEED", "DISCHARGE", "MORTGAGE", "EASEMENT", etc.
- Book & Page B:#### P:####
- Page Count: #
Column 2: Parties
- Party 1: (multiple lines)
- Party 2: (multiple lines)
Column 3: Legals
- Frequently only contains "LYME"
Column 4: Additional
- Notes:
- Return To:
- Consideration:

'''
def print_transaction(x):
	collectDate = datetime.now().strftime("%Y-%m-%d")
	entire_contents = x.contents
	# print(repr(entire_contents))
	# cols = x.find_all(class_="w-1/4") # pre-Jan2024, columns were tagged with the w-1/4 class
	
	cols = x.find_all(recursive=False)
	transaction_line = print_firstcol(cols[0])
	transaction_line += "\t" + print_partycol(cols[1])
	transaction_line += "\t" + print_legalcol(cols[2])
	transaction_line += "\t" + print_finalcol(cols[3])
	transaction_line += "\t" + "" + "\t" + collectDate
	print(transaction_line, file=fo)


'''
Print the "first column" containing
- Transaction ID (within button)
- Date&Time (remainder are bs.Element.tag's)
- Transaction Type
- "-"
- Book&Page
- Page Count
(It's really annoying to find the correct offsets - it seems to change 
from day to day - or run to run? The "3" and "5" below are just magic for this run)
'''


def print_firstcol(col):
	firstcolcontents = col.contents  # return a list of the contents
	# print(len(something), " items in something")
	# summary=firstcol[0].contents
	# print(len(summary), " items in summary")
	# print(summary)
	# ct = len(firstcol)
	# print(firstcol[ct-2])
	# line = "Col1"
	line = firstcolcontents[-2].text  # Get the transactionID (second to last?)
	# print("ID: ",summary[2].text)
	for child in firstcolcontents[-1]:  # Get the last element (?)
		# print("Type: ",type(child))
		if type(child) == bs4.element.Tag:
			t = child.text
			if t == "":
				t = "-"
			line += "\t" + t
			if "/" in t:  # also split mm/dd/yyyy hh:mm:ss AM
				ary = t.split(" ")
				line += "\t" + ary[0] + "\t" + "-"
			if "B:" in t:  # also split on B:123 P:456
				ary = t.split(" ")
				line += "\t" + ary[0][2:] + "\t" + ary[1][2:]
	# print(child.text)
	return line


def print_partycol(col):
	# Print Parties
	# print("==========")
	# print(repr(cols[1]))
	
	partycol = col  # return a list of the contents
	# print("Parties: ",partycol)
	parties = partycol.find_all("label")
	# print(len(partycol))
	partynames = ["", "", ""]
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
	line = finalnames[1] + "\t" + finalnames[2] + "\t" + finalnames[3] + "\t" + \
		   finalnames[4]
	return line


def update_names(finalnames, whichname, item):
	if finalnames[whichname] == "-":
		finalnames[whichname] = ""
	if whichname == 2 and finalnames[
		2] != "":  # Just add lawyer's name, not address
		return
	if finalnames[whichname] != "":  # add ", " if something's there
		finalnames[whichname] = finalnames[whichname] + ", "
	finalnames[whichname] = finalnames[whichname] + item.text.strip()

if __name__ == "__main__":
	sys.exit(main())
