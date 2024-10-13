# Scraping the Property Tax Records

A set of tools for processing data from both
Vision Government Solutions Incorporated (VGSI)
property tax records (used in Lyme, NH) and the
AVA Fidlar deed registration system
(used by Grafton County Register of Deeds - GCRoD).

## scrapevgsi.py

The `scrapevgsi.py` script iterates across all pages of
the tax records.
The script outputs several files to the current directory
with data from nearly all the fields on each page.
These overwrite any files produced by previous runs.

- `ScrapeDataXX.tsv`
- `OwnerHistory.tsv`
- `Buildings___.tsv`
- `AssmtHistory.tsv`
- `ApprlHistory.tsv`

The script iterates through known PID ranges for properties,
(see `ReadNextVisionID()` for details), retrieves each page,
then uses `BeautifulSoup` to retrieve values from the page.
It also converts dates to YYYY-MM-DD format and
removes "\$" and "," from dollar amounts.
The script pauses for a few seconds between requests from VGSI
to avoid overloading the Vision server.
The `-d` debug option eliminates the delay between requests
for faster testing.

### Running with PyCharm (easiest)

The PyCharm IDE has a configuration for `scrapevgsi`.
It outputs the named/dated files in the top level directory.  

### Manual Processing after Scraping

After the full set of records has been scraped into `.tsv` files,
organize them by doing the following:

* Check for errors: Scan the ScrapeDataXX file for any "Can't reach 
  the server" and fix those lines.
  (There shouldn't be any - the `scrapevgsi` program should now
  recover from those errors.)
* Rerun if necessary. 

Then... 

* Create a new folder named _ScrapedData-ddMMMyyy_
* Copy all five output files to that folder
* Move that folder to the _TaxFairness/RawData/ScrapedData_ folder
* Review the other _ScrapedData_ folders, and rename the new one 
  to _ScrapedData##-ddMMMyyyy_ where **##** is the "next version"
* In a text editor, modify the ScrapeDataXX file:
  * Remove all the "Problem loading..." lines
  * Change all _Version?_ to the next "version" for the
    _RawData_ folder (see above)
  * Save the _ScrapeDataXX_ file

Final preparation for importing to SQLite:

* While in the text editor (above), copy the entire contents,
  and paste into a new tab (ScrapeData##) of the
  _DefinitiveData/ScrapedData.xlsx_ file.
* Copy that tab, and append to the main **All-Scraped-Data** tab
* Ensure all date/dollar fields are in the correct format
* Export the "all-data" tab to _ScrapedData.csv_,
  replacing the previous copy
* Use the _TaxFairness/mergehistory.sh_ script to merge all the
  Assessment, Appraisal, Buildings, and Owner history files.
* Update the `import_crunched_data.sql` file in
  _TaxFairness_ to import those files into a new set of tables.
* _NB: All five of these "scraped data" files are now moved into
  canonical locations, so no change to the import file
  is necessary._

### Enumerating PIDs

**No longer needed - `scrapevgsi.py` enumerates all PIDs in the sensible range**

_Here's the old process for Enumerating PIDs.
Preserved here to document the process. It used to take ~20 minutes_

* Go to the [VGSI MBLU page.](https://gis.vgsi.com/lymeNH/Search.aspx)
* Enter each of the map numbers.
  In Lyme, they are `201` and `401 .. 422`
* Click through each of that map's pages
* Copy each of those pages. Use the Chrome extension ColumnCopy (I used version 0.5.0) to right-click and Copy Entire Table.
* Paste into a spreadsheet
* For extra credit, add a "page number" column to track each map's Page
* Save the full results as a "Raw Data" page, and protect that sheet
* Make a copy and then manipulate into a CSV file with PID, Map, Lot
* _That's it..._

## Scraping AVA

The Grafton County Register of Deeds uses the Fidlar AVA software
to record deeds.
The search page at: 
[https://ava.fidlar.com/NHGrafton/AvaWeb/#/searchresults](https://ava.fidlar.com/NHGrafton/AvaWeb/#/searchresults)
seems only to return a max of 200 results.
To collect information about a broad range of dates, it is necessary to 
search across date ranges that produce fewer than 200 results.

Begin the process at the final date of interest, then keep adjusting
the beginning date to produce fewer than 200 results.

Then use the Browser's "Inspect" facility to Copy the Outer HTML,
and paste the information into a separate .html file representing
that date range. Save the file in `AVA-GCRoD/HTML/ddMMMyyyy.html`

The `scrapingAVA.py` file sucks in a HTML file
and produces a tab-delimited file that includes all the records. 
**Run -> Edit configuration...** to read the proper HTML file.

The program outputs a file named `AVA_Records_YYYY-DD-MM_HH-MM-SS.tsv` in the _AVA_GCRoD_ folder.

### Processing the `.tsv` files

* Open it, and save as `.xlsx` file for ease of formatting
* Fix all the `PLAN` entries (see below)
* Discard the `-` column between Type and Book&Page
* Convert all dates to YYYY-MM-DD
* Convert all prices to numeric, no decimals, no commas, no "$"
* Add all the Transfer Tax entries (see below)
* Create a new tab in the 
_Tax Fairness/RawData/GCRoD-All-Data_**.XLSX** file
and paste in this data
* Append the new data to the "All Data" tab 
* Export as **CSV** to _Tax Fairness/DefinitiveData/GCRoD-All-Data_**.CSV**
and import into SQLite

**Fixing "PLAN" entries:** These don't have a Book&Page entry, so the results
for those rows are shifted several columns to the left.
You must manually shift the entries to the right to produce the CSV file.

**Transfer Tax:** Examine each `DEED` record.
Find its Transfer Tax by looking at the actual deed. 
If there's a Transfer Tax, record it in the rightmost column,
otherwise enter '-' to indicate that someone has checked it.
There's (almost) always a \$25 LCHIP entry; ignore it.

### Notes on imports

* The five files **GCRoD-1.html** .. **GCRoD-5.html** were retrieved 
on 18Aug2022, each for a different date range to keep the record count
under 200. 
After processing by `scrapingAVA.py`, the tab-separated output is in
**GCRoD-N.tsv**

## History

Back in 2017, I wrote a bunch of scripts to pull data out of the Vision property record (VGSI) for Lyme, NH

In April 2021, the Town of Lyme sent me a CSV file (txcardlookup-6Apr2021)
that listed all properties by their VGSI "PID" along with Map/Lot
(There's a new way to get the PIDs - see note above about enumerating the PIDs.)

The program and process has evolved to be simpler.
The procedure above documents what needs to be done.

### To Do

* _DONE_ The `merge_history.sh` script in **TaxFairness** merges the history files. 
