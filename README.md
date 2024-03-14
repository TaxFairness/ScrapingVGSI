# Scraping the Property Tax Records

A set of tools for processing data from both Vision property tax records (used in Lyme) and the AVA Fidlar deed registration system (used by Grafton County Register of Deeds - GCRoD).

## scrapevgsi.py

The `scrapevgsi.py` script retrieves PIDs ("VisionID"s) from a file, and outputs a tab-separated file that shows selected fields from the resulting page.
The script also pauses a bit between requests from VGSI to avoid overloading the Vision server.

The script reads the `./PIDs/PIDs-Sorted-ddMMMyyyy.csv` file named in **Run -> Edit Configurations...** 
The script outputs several files to the current directory.
These overwrite any files produced by previous runs.

- `ScrapeDataXX.tsv`
- `OwnerHistory.tsv`
- `Buildings___.tsv`
- `AssmtHistory.tsv`
- `ApprlHistory.tsv`

The `-d` debug option eliminates the delay between requests for faster testing.

```
cd ScrapingVGSI
python ./scrapevgsi.py -i ./taxcardlookup-21Nov2021.txt 
# or to debug...
python ./scrapevgsi.py -d -i ./taxcardlookup-short.txt  
```

### Running with PyCharm (easiest)

The PyCharm IDE has a configuration for `scrapevgsi`.
It reads a file of PIDs that has been pre-built
(see **Enumerating PIDs** below) and
outputs the named/dated files in the top level directory.  

**Optional first step** As an alternative to enumerating all the PIDs,
update the list of PIDs manually by searching VGSI for sequential PIDs at: [VGSI Site for Lyme](https://gis.vgsi.com/lymeNH/Parcel.aspx?Pid=103255)
Add them to the end of the CSV used as input.  

### Manual Processing after Scraping

After the full set of records has been scraped into `.tsv` files,
organize them by doing the following:

- Check for errors:
- Scan the ScrapeDataXX file for any "Can't reach the server" and fix those lines.
(There shouldn't be any - the `scrapevgsi` program should recover from those errors.)
- Scan that file for "Problem..." and comment out that PID from the input file
- Rerun if necessary. 

Then...

- Create a new folder named _ScrapedData-ddMMMyyy_
- Copy all five output files to that folder
- Move that folder to the _TaxFairness/RawData/ScrapedData_ folder
- (Optional) Update the `import_crunched_data.sql` file in _TaxFairness_ to import those files into a new set of tables.

### Enumerating PIDs

**Here's the process for Enumerating PIDs. It takes ~20 minutes** 

* Go to the [VGSI MBLU page.](https://gis.vgsi.com/lymeNH/Search.aspx)
* Enter each of the map numbers. They are `201` and `401 .. 422`
* Click through each of that map's pages
* Copy each of those pages. Use the Chrome extension ColumnCopy (I used version 0.5.0) to right-click and Copy Entire Table.
* Paste into a spreadsheet
* For extra credit, add a "page number" column to track each map's Page
* Save the full results as a "Raw Data" page, and protect that sheet
* Make a copy and then manipulate into a CSV file with PID, Map, Lot
* _That's it..._

```
# Map Numbers for Lyme
201 and then ...
401 .. 422
```

~~It may be possible to enumerate all PIDs from the Vision system
instead of relying on a (potentially-incomplete) hand-entered list.
The algorithm could do a search by Map, then iterate
across all the pages of the result until a 500 Server error returns.~~

_NOPE. The Vision software continually varies the "txtM" and "hdnM"
fields of the POST post that make it hard to automate.
It's easier to copy/paste the lines from all the individual web pages
from each of the ~20 maps. See the procedure above._

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
that date range. Save the file in `AVA-GCRoD/HTML/MMMMYYYY.html`

The `scrapingAVA.py` file sucks in a HTML file
and produces a tab-delimited file that includes all the records. 
**Run -> Edit configuration...** to read the proper HTML file.

The program outputs a file named `AVA_Records_YYYY-DD-MM_HH-MM-SS.tsv` in the _AVA_GCRoD_ folder.

### Processing the `.tsv` files

* Open it, and save as `.xlsx` file for ease of formatting
* Fix all the `PLAN` entries (see below)
* Add all the Transfer Tax entries (see below)
* Discard the `-` column between Type and Book&Page
* Convert all dates to YYYY-MM-DD
* Convert all prices to numeric, no decimals, no commas, no "$"
* Create a new tab in the 
_Tax Fairness/Raw Data/GCRoD-All-Data_**.XLSX** file
and paste in this data
* Append the new data to the "All Data" tab 
* Export as a `.csv` file and import into SQLite

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

### Updates
**17Aug2023** Update `scrapevgsi.py` to:

* Run (most) values through plainValue() to remove \$, ",", and fix dates.
This means that no manual processing is required on columns of the .tsv files 
* Output files no longer have timestamp.
They get organized into a separate folder with their date.
This avoids proliferation of (unneeded) output files.
* Fix line endings to avoid outputting blank lines
* Change advice: now move ScrapedData-ddMMMyyyy to _TaxFairness_
    
**Jan2023** Update to `scrapevgsi.py` to recover from retrieval errors by waiting 20 seconds and retrying.
Also reformat all columns for easy import (and remove manual processing).
Also tweak `scrapeava.py` to separate the information from difficult columns.

**11Dec2022** Retrieved full set of PIDs using procedure below.
Ran `scrapevgsi.py` without incident to produce `ScrapedData5.csv`

**21Nov2021**
Remove lines from original Town file that are not in town's database
(as shown in the OldVsNew PDF from Oct 2021)

### To Do

* _DONE_ The `merge_history.sh` script in **TaxFairness** merges the history files. ~~Come up with a way to combine the XXXX_history files.
They contain the latest information (generally, three years) from Vision.
But the information will be lost when previous years' info gets pushed off
by new years.
This probably implies some fancy SQL import that replaces existing info
new info from the same year (???).~~
