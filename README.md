# Scraping the VGSI website

Back in 2017, I wrote a bunch of scripts to pull data out of VGSI for Lyme, NH

In April 2021, David Robbins sent me a CSV file (txcardlookup-6Apr2021) that listed all properties by their VGSI "PID" along with Map/Lot

The `scrapevgsi.py` script retrieves PIDs ("VisionID"s) from a file, and outputs a tab-separated file that shows selected fields from the resulting page.
The script also pauses a few seconds between requests from VGSI to avoid overloading the Vision server.

To run the script, using the default file of PIDs, and outputting to a file named `TODAYS-DATE.tsv`:

```
cd ScrapingVGSI
python ./scrapevgsi.py -i ./taxcardlookup-21Nov2021.txt -o TODAYS-DATE.tsv 
# or to debug...
python ./scrapevgsi.py -d -o TODAYS-DATE.tsv -i ./taxcardlookup-short.txt 
```

There's a `-d` debug option that eliminates the delay between requests for faster testing.

**21Nov2021**
Remove lines from original DAR file that are not in town's database
(as shown in the OldVsNew PDF from Oct 2021)

**24Feb2022**
To convert the "scraped data" `.tsv` output file into a form suitable for input to SQLite, do the following:

- Open the .tsv file, let all fields be "General"
- Look for "Can't reach the server" and fix those lines
- Format the MBLU field into its component fields: Map, Lot, Unit
- Format all "$" values as numbers, no commas, zero decimal places
- Format all dates as YYYY-DD-MM
- Save as `<filename>.csv`


# Scraping AVA

The Grafton County Register of Deeds uses the AVA software
to record deeds.
The search page at: https://ava.fidlar.com/NHGrafton/AvaWeb/#/searchresults
seems only to return a max of 200 results.
To collect information about a broad range of dates, it is necessary to 
search across date ranges that produce fewer than 200 results.
Begin the process at the final date of interest, then keep adjusting
the beginning date to produce fewer than 200 results.

Then use the Browser's "Inspect" facility to Copy the Outer HTML,
and paste the information into a separte .html file representing
that date range.

The `scrapingAVA.py` file sucks in each of those files
and produces a tab-delimited file that includes all the records. 

The five files **GCRoD-1.html** .. **GCRoD-5.html** were retrieved 
on 18Aug2022, each for a different date range to keep the record count
under 200. 
After processing by `scrapingAVA.py`, the tab-separated output is in
**GCRoD-N.tsv**

NB: The "PLAN" entries don't have a Book&Page entry, so the results
for those rows are shifted one column to the left.
I manually shifted the (three) rows over to produce the CSV file.
Result file is **GCRoD Transactions-2019-2021.csv**
