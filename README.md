# Scraping the VGSI website

Back in 2017, I wrote a bunch of scripts to pull data out of VGSI for Lyme, NH

In April 2021, David Robbins sent me a CSV file (txcardlookup-6Apr2021) that listed all properties by their VGSI "PID" along with Map/Lot

The `scrapevgsi.py` script retrieves PIDs ("VisionID"s) from a file, and outputs a tab-separated file that shows the fields defined in the `domIDs` array. The script also delays a few seconds between requests from VGSI to avoid alerts.

To run the script, using the default file of PIDs, and outputting to a file named `TODAYS-DATE.tsv`:

```
cd ScrapingVGSI
python ./scrapevgsi.py -i ./taxcardlookup-6Apr2021.txt -o TODAYS-DATE.tsv
```

There's a `-d` debug option that eliminates the delay between requests (for faster testing).
