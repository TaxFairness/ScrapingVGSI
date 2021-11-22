# Scraping the VGSI website

Back in 2017, I wrote a bunch of scripts to pull data out of VGSI for Lyme, NH

In April 2021, David Robbins sent me a CSV file (txcardlookup-6Apr2021) that listed all properties by their VGSI "PID" along with Map/Lot

The `scrapevgsi.py` script retrieves PIDs ("VisionID"s) from a file, and outputs a tab-separated file that shows selected fields from the resulting page.
The script also pauses a few seconds between requests from VGSI to avoid overloading the Vision server.

To run the script, using the default file of PIDs, and outputting to a file named `TODAYS-DATE.tsv`:

```
cd ScrapingVGSI
python ./scrapevgsi.py -i ./taxcardlookup-21Nov2021.txt -o TODAYS-DATE.tsv
```

There's a `-d` debug option that eliminates the delay between requests for faster testing.

21Nov2021
Remove lines from original DAR file that are not in town's database
(as shown in the OldVsNew PDF from Oct 2021)

Progress Notes:
```
OldVsNew:

√ Lot 100/10 (LymeFiber) - Doesn't exist in VGSI - No PID

√ Lot 201/30/T - Add PID 103137

√ Lot 201/77/T - add PID 103117

√ Lot 201/77/E - Add PID 101162

√ Lot 201/80 (no unit) doesn't exist in VGSI anymore 
------------
√ Lot 401/55/1010 - Doesn't exist in VGSI - Land code 995

√ Lot 402/75 - add PID 103036

√ Lot 403/27 - add PID 103016

√ Lot 406/16 - add PID 103079

√ Lot 406/4 - Check PID 103078

√ Lot 406/4/1 - Add PID 103097

√ Lot 406/9 - Add PID 103157

√ Lot 407/102/1030 - Correct to lot 1000 in OldVsNew

√ Lot 407/17 - Check PID 103057	

√ Lot 408/22/2000 - Check PID 102976

√ Lot 409/59 - Check 102996

√ Lot 410/13/1200 - PID 103178

√ Lot 410/13/2000 - Check PID 1076

√ Lot 413/14 E - Not in VGSI (No PID)

- RK still shown on 201/35/0020

- Change LandCode 995x to 995

√ Problem loading parcel PID 71, Map 201 Lot 50 - not in VGSI or OldNew

√ Problem loading parcel PID 101522, Map 408 Lot 1.2 - Not in VGSI or OldNew

√ Problem loading parcel PID 100061, Map 201 Lot 80 - Unknown in OldNew (995)

√ Problem loading parcel PID 102642, Map 201 Lot 35.0010/1 (995)

√ Problem loading parcel PID 102765, Map 401 Lot 29.1 (Not in either)

√ Problem loading parcel PID 102643, Map 401 Lot 55.1010 (see above)

√ Problem loading parcel PID 453, Map 403 Lot 36 (Not in either)

√ Problem loading parcel PID 656, Map 407 Lot 17 (Add 103057)

√ Problem loading parcel PID 100242, Map 407 Lot 56.3 (not in either)

√ Problem loading parcel PID 854, Map 408 Lot 17 (not in either)

√ Problem loading parcel PID 1075, Map 410 Lot 13.1 (Not in either - SB lot 1200)

√ Problem loading parcel PID 1194, Map 413 Lot 21 (not in either)
```
