# Scraping the Vision Property Record (VGSI) website

Back in 2017, I wrote a bunch of scripts to pull data out of the Vision property record (VGSI) for Lyme, NH

In April 2021, the Town of Lyme sent me a CSV file (txcardlookup-6Apr2021)
that listed all properties by their VGSI "PID" along with Map/Lot
(See note below about enumerating the PIDs.)

The `scrapevgsi.py` script retrieves PIDs ("VisionID"s) from a file, and outputs a tab-separated file that shows selected fields from the resulting page.
The script also pauses a few seconds between requests from VGSI to avoid overloading the Vision server.

To run the script, using the default file of PIDs, and outputting to a file named `TODAYS-DATE.tsv`:

```
cd ScrapingVGSI
python ./scrapevgsi.py -i ./taxcardlookup-21Nov2021.txt -o TODAYS-DATE.tsv 
# or to debug...
python ./scrapevgsi.py -d -i ./taxcardlookup-short.txt -o TODAYS-DATE.tsv 
```

The `-d` debug option eliminates the delay between requests for faster testing.

## Manual Processing after Scraping

After the full set of records has been scraped into a `.tsv` file,
convert the "scraped data" file into a form suitable for input to SQLite by doing the following:

- Open the .tsv file, let all fields be "General"
- Look for any "Can't reach the server" and fix those lines
- Format the MBLU field into its component fields: Map, Lot, Unit using Excel "Text to Columns" to split on "/" and " ". Remove leading zeroes.
- Format the Book&Page field into its components. Remove leading zeroes.
- Format all "\$" values as numbers, no `$`, no commas, zero decimal places
- Format all dates as YYYY-DD-MM
- Save as `<filename>.csv`

## Updates
**11Dec2022** Retrieved full set of PIDs using procedure below.
Ran `scrapevgsi.py` without incident to produce `ScrapedData5.csv`

**21Nov2021**
Remove lines from original Town file that are not in town's database
(as shown in the OldVsNew PDF from Oct 2021)

#### Enumerating PIDs

**Here's the process for Enumerating PIDs. It takes ~20 minutes** 

* Go to the [VGSI MBLU page.](https://gis.vgsi.com/lymeNH/Search.aspx)
* Enter each of the map numbers
* Click through each of that map's pages
* Copy each of those pages. Start to the left of **Address** 
and drag across the last row.
Do _not_ copy the page numbers - they screw up the columns of the .xlsx
* Paste into a spreadsheet
* For extra credit, add a "page number" to track each map's Page
* Save the full results as a "Raw Data" page, and protect that sheet
* Make a copy and then manipulate into a CSV file with PID, Map, Lot
* _That's it..._

```
201 ... then skip to...
401 ... the rest are in sequence...
402
403
404
405
406
407
408
409
410
411
412
413
414
415
416
417
418
419
420
421
422

```

~~It may be possible to enumerate all PIDs from the Vision system
instead of relying on a (potentially-incomplete) hand-entered list.
The algorithm could do a search by Map, then iterate
across all the pages of the result until a 500 Server error returns.~~

_NOPE. The Vision software continually varies the "txtM" and "hdnM"
fields of the POST post that make it hard to automate.
It's easier to copy/paste the lines from all the individual web pages
from each of the ~20 maps. See the procedure above._

The URL below requests map 408, page 4 as a table.
The final field of each row is the PID.
Variable fields are separated by "&" and are:

* ___EVENTARGUMENT	"Page$4"_ `__EVENTARGUMENT=Page%244` 
* _ctl00$MainContent$txtM	"408"_ `ctl00%24MainContent%24txtM=408`
* _ctl00$MainContent$hdnM	"408"_ `ctl00%24MainContent%24hdnM=408`

```
curl -vv -X POST https://gis.vgsi.com/lymeNH/Search.aspx -d "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=qKed3GMONzu23V9MIUjVJ%2BwK%2FKL%2FACMOHnR%2FxXQB39kDH20syEg3li0SN2zs5alnWEOf2ey6Ig8wUo6tWuaw8ZuXQqMw%2Bp2U1zFilwFJF7oZoD4sKqbz97IGo245Tz1XK7RBn7rheq8LkScf8ABCgy70tNIESYLysMqyOyx%2Bl643ll0OA120qFIODlLBKtEOaAA6ijqqWPh2Izxb4fQ4zfUDp7us1sI2%2BJ29p5%2FmTT9bh6B48kgoZSS2D1jn4yNpi1xj44BGSDsJd4vPdGY8Fv1AfZZzqOOzGCgfv0A1d2xpXsq2Bl%2Fx72iJablqT1oCJOiAuTQ6WeMOR9eO7uicIXLYAaMHJ01BvQaHaYwbEHB5nG4RulcZ4LeCwD%2FUqMAZIZDsw5XO1%2Bqv2T93s0MMF%2BC5Jp1ODqFSejv44vYGPWP4SCMUOglMqDGHtW1KoOZxWf8osYHo%2BcXiTQWW2%2Fmw71Jq%2FIHZ9FzVrJZHHNWV9k%2FKIgpqITXBnaUoVoTvQkGk5zdl1VUm9Mi1JmXy47ZCFCeS0PcmeiMj2Jj7IIh3W83GK4%2FFjRqRbqSF7ZovXbVlGg3FMivj4KVMa3iyfy0Ao8UP66NcTqd3CtSl0C8fD%2BIX%2F7KMDYRBG%2BbVHIxunWaHDsOiHSchEY7Vws3BvQQcgqVjrGgqGKE%2Bpb1snF%2FUsVM8%2By26u3%2FyLLEY320IsnVWcZDyrvhyDMxZmeh4pr1F0St5FSfQ50tGmwf%2B%2FcZ0%2Fo%2BjIkB1saXkJdFVEklTgKERKpLo9SF9xzqQ2qAiipwrxBe0LaP14jMJAr%2BKJtudOCbpAIyU%2BOOUy%2Bb6BIQJjKXbd3uqXEjJSbg1Fe8LZK7AX1BvXjPwrEIPocjUdVxwWCknUOttASCr%2BwkqkdhqEnLGG4YO0yiVS3zHBTcRkaba22NNPrG%2FxNi7hY37DNXTKqveFkknVS5zgxtzAdZdws5Lz5Vz6tHshR6BNcdZEiRfo1F9l6d5TrmSw8%2BKe7ol3261all9CelvgrjRXgk572j5afX23dGrhTRq%2Bu3VFhBkYdMt3b%2BPMcrIQjsWBByzNs9SQDWRZMi95093URD8kEAFDM3B4ohOftc60x2sTakoBd2WcGg7VndZ4R4RJdmQxu0DB4vPhnZLMMkapOusNVv%2BFdVbfmw8kvLX4kEG%2BdxpemcGmvAHlaBJPlDxYWsJedQ9Xu%2B3ghf5ly2EVTJqR4hr1xafNrp6A7RIfjRdP6trXkUFETtxr65ga3e7tuVRVtBEXA9QnH5N85BIsSwZjYt2iQDBuPt1kG3GHYATpTTIQwH5ZGVz%2F57mWJmEQZR3yxQza1ULyIOn2OykWVDfJHHT0OOuolzHg63LpyEglne%2FvHBDcVmAQdqIPET7OVQr7433hb%2B3BHS0rTncELg9oOgWSFAiKFajnW%2BzzzfveTBfHd06q%2FYyk9SKfyNNHJ1qUAKdjl5N1rDUwEzocXwv6InDJ%2FX7toHIlfLL0fXsn9gbp0fsVgmcvisc4EiUFFdKAeVKX15i5HEdKYLibneFFmX6rNWaUfbFG%2BEGwJGimw0hoJsviDMDMsZ%2FYU7vCpbs9J%2BzpqMGZtJNOjYyRrvk%2B79Dnom4jSmsKztbAB4FztbSMkHrHgKOwP29mhb5otMPz0NHdtlYbSujJfe3OMQqWDmTdMh5p5H59NSV9ADmfH1D2FHRhmMk65ONhUejNOMmHgfVi330YOI6683tqHq05YBJX47wd2sR6RqNouyja6YRyCxeVVnOYiDT1bYGTLEoe0mc0LYWDX3JmhaehHy9qFTvs9zNXwpBdrmnSvO7FeSqey1ocwtYq7fU4XLdxqM6Boqi8PxYupfQWCSXIHNkkxGxsmyHqGcYqvMORHBcveOOhIU6BsqSHq2nfIIbnuUC57F7S0fiv%2B2Fj5fQ8mPMic3GCPfcGMAow2SsfPzFbR06A1VEzVLrsScMt2kQoiP85xGWPAidMmvqHhXoOHaAq2ehQUyp1SONa8PwQxtQhhZjaNzjCYzCeEsawDtVvkLhu6po9mThe%2FcSozVc1vyo%2Brmxz8jnQLXasWedF3l%2Bxqbuz9z6OK97Ll2w8Vj0cAEm9EUnniWrnD43Hg1NkXps5hYFvgFtsnPoVliELg2MIlsgVKol6PeYZEFDU8%2B418iH2buLtsurrDiHrKxNwKpPa4C04%2BrQgjXuGZbrZldY3sKcucROlA%2FDTyV7xmFouQA4AzqWj%2FzZuaXpQDgBmrWbWpRMI%2FDiIgB6CrdsEOIy5heGe9e%2Bux%2BD%2FZONSb%2Bzoq%2F0K%2FUwDAHHeol%2FLmHIxSLFvrTWoxh%2B8VovrBoQkYfNG%2FnVT1CNuZqsjnOJCaGG%2FgY%2Bqzy0daVLpe1M7EGKa%2Fc0kVqWO7OPeUZARq1Q602dW%2FPlMnOHkYtExQ5ybMe75VTNz7BPKgy2hNy9uOsrH%2BPC6qcXuW5ido%2FuezUrW7v5j%2BUIirutDk%2FQMYaN2C157B4MgblIrXRngI1gNf1Blr8XEweXPaqYrTQUFV2U2L%2F%2B9582cQa7PjC56Ka0hr84u5prU8DNDzTis3tjottuR%2FaKKWSwjj%2FallPZ%2F0RBPU26BsDykdA8OKEog8hWjbPADfXJgBxjrpslT6DfOyWVdak%2FF99i8xvm0hi1Jljh0JsgJhB9WTLn2T5qEzYWSOo6l13O4M7sOAlQWm7PFwsO8c9mco0OGjL2LHCJGk9FCEpddIfWyM3tdyEUo53uGeR8SclyOKyD4nxjsiwGHmjg%2BqWiLYX2JPXQHjyHPK7Tj3hVWWJxFOucHxTR%2F1GtEpFja%2F2FP%2BykAPsRPMKQg4RxBBz6kBxAs5WRiCR7nxe2MWV3DaGoLzmnng7WybFiC%2BKu35M6VHOnC8Xj1Vd85pHHWQTSb%2FwFmEQMjloF2iap7MApXoY3Cw6So%2FwwZVLk7oxGMRz0vDMPoEa9cvld8CgbqqBy3x5%2BzIiTXsTxjvEWptx7IVIC3pLMxr27Ag3icDK23iNqGsJDT9hNzN6ULgh5KAfiX7d0mKm7RlG3JqIxN1mwfz7jkC17He12niSYdrtHm2rFWQt2IyVUGJnUoEs9KXq3nv1dTFtN4eSAHDoqX4HD2uD2swRADDlumI%2BSJwvU4QV3YIrhj%2FsGdKOr4yqyxKXO6gKiFHkPJ1dkvzlvgbMIFNMeIDpSdOrEj3o1speLHVOZ2AU%2BLVOwY0GXHfTIpp4OMjBoVaL4wpb6AYYROuQpErpeNDabt2U4orPrCKIqsgXI0FHbUeB0GSV2%2FpayiDDkRkSM4T26GApHWqBdQAb74or5UsuzqjmisFLeIsFV4Z2RBLobvIFKOYMvN43RRkW2zjxOQ1INn%2F4xgL3aA6DztX%2BmsPNWLVRLnmj%2FO1MaiCJYVy9nIPmlNgE7VEZTg7%2B85vkBbJP5QIC5EZeCW5zr1cwSa2noqQFXep8gzSKrjOUqSlqKwVt3QbVD7CQB%2Fb6MmkT3n9sUCSftkTCECv35GMF4qiRqbOhkj4qMCI%2BbrfttDUpA3GR2o9AVfhqZKfDE4toc1kadeAlLj7d0W776xU22QGM9CjPNyK0y%2Fl9ozvf%2BcIxpXoT1s5nD8%2F422LhbDnjsBZoNtY6vqmAHCo2P4dnOSSdej8x6H0TXmah1yasbGMotGSRw%2FbF3fzRBKcXtWB5FvxZ%2FXR%2BGZTMuJmB%2B1Od%2F9HWakPlS%2FVey4cvsd7ol8vWy%2FShHKdeWfgvWjojyiScrH5y8wdOJMeHzAC4j5GATRjc1fJ6N7OH1t4hj0dWgaL1muMTJLa3Bz3u3nJEMCxQokOWHByWtvqI6YqdCU4xe9%2Fpcm5LUprOfL5srjJS4Ixcs0iJiIetii9yedFrRyCRjBLoJxXhecWle6OH9wTJLEPNh2CJ%2B0EPCjXZlDtNWsxqKDAJqUbCrqlKZNRh0SHnwLBE7OXsv8yayHzS3CsElTM76q%2FrDsIy9eSg05A48oZ9QRjd7QGKxzLHjv%2B2PMos6jSABGjBaJAjrj3AcLScVr%2FhVvOyiPiTNejtHw6YuEbQjy%2F7L%2Bj9nMY3VbZda6ONkyq5yjcO3Nb31YzPK5sAfF2TpHhCOrfLVDS74Ksa2qaS66Whfx1vslJj3mfiKBE1%2Bwfd28Sa1TznHcSbHxNLhednu2oKmqH2fezC%2FdSOaUQil%2FxsfwNoHG01pHe%2Fhl8d5Nh%2FULFTZpBlmnVKVSKPaG%2Byeeg1FAEnFNDsl7lxyioL%2Bq2OWeHFv0KZ0uPQOqnslJ6YJZ2CxUINi4Kz96bnlh4%2BH7%2FGJCS4vFhcSgQabMDliteQce6xXlC3z%2BVP7LmdL0Pd5KznhN%2BTNW7YqLDGLjy%2FbysXIIBOEM3kHEXRezTSLrgmWa312x6xEd8VbbUTNaL5OmtOiRNyb7tk3uVlUYanGufUhGLxAhZOtswWqfnhJsefryZTmZwpavqaOE6Ji4sYccqyYu9nXh25uVs83Yw4%2Fo%2B7Rdo7N9VJVLcCQKVGrMjGdFHzI9Zq1bamFGuf7V8D%2FjnXrD%2FaTfjOj%2BqGk%2BZzPzroE%2BzRxtdrq29yHkmTm5NU8qWnO10KMgM1woUjDIraBzzP8q%2BETUkrxrKm3B63AAZjxd%2BisLjd7rle6l9N8s85L8WcgXvHZ1IdT0avoLpJu0xagNO4NWODbJ4dtdoQkpe5JxKMWdCoUoDLXx%2FYS%2BGca9jLT%2BlMgz55Vng51YIVIwy4B8CPXg2STBW4y38AUmx59bajz3OAa0doSPAx4TgFjWspirvNAWlhdCWaJm41L5U8S15z%2BwlJKz09Yc%2F4amNbhvet94hZBcOre962ErytmvRxehssbxjVbUHmtjnT%2B2i%2B04dxAM5KqvgsTwsac0HplFT3q68jrcaSDlb2Gz9qHW6k%2FzS8uZb8kEqlScrFkfsZw72YQ651CXs8nu7IOkghJdsAP2AiBAQV3qZJH0w3vGETxne7a5nDEf%2FjNj939VdieQSRIJMqxQcIF55LNWJL8AsXZYyXI99rq6p6E0m6Anm3wgo0YNlTXZqP6l67xuasmYnKulDeztiMhxPPoq0k48FRzecM908We8VssPuRrWW2XX%2BuKO4hDqycNwK80AQRNZ32HOtmNXZ%2FTds4uR6tb4zrCscBe82rouTaE3xsmHRZ%2B3SGuKwX8M3I6FIRfNzqowBh1wh9xyh%2FpTPTFZNCSf0n37Nrk1lhAZ5Www8Wf3PDfdEA9znLx5iciFE0gNNrPG66r2GPyfgZbMuSyOmL3pV7ChNsk1PmaEnXNBwAQ%2F%2B3WxtAdhpzVL1UbStOvMGlPDUh%2FC0fgYx7Oi5IG71Wfktq5c5QDE8ckPOd2adsaRcQvfb6yXqxWHJNYMmvjoijX%2FATfNZTf0STGOI6ivaXbS6prL67bCB6W13WwKbxF83xKq2cJX4YKBlLMXWd91hy9mlx2GqjNNkEBB8lEcvLej0i6D0cz8t6l6bNvDXS7sDWSVkoVRRkGDHqVTFhxMQ95%2F5FyIN%2B0eE%2FKbmeO9C0OB9X4MxD9AV8ds675TiVpTyrZ6dE9vRczuS%2FIZgh585PyE9AdLOFyvdd%2Bc54c6pTF4RTsn0V29%2Bgc98QZdWmps5zNnoRi%2FnFpdBFEyCxI69rTBClvA%2F8MjUUT4%2F2oPBcxRmxjL4U%2F5jgfyxqfsfdStFcp848bJKiJVUzb4FgQNJiVnhPQmPDCQvmqywWavz%2FrlXRwBRX771KROI50Eq57rFzrNgty8y4zjAdTBM2P0Tib%2Fj3FHfMPd%2BQ9YIHlykveLgCrbRrGQFlfE48Q4FiruBmKP%2FSmwS%2FHghMnQHwV2jnBYXNl16W2LFw%2BKcHXDiuWVeOJ5L%2BtCNwC1xrV7wHM2joshu%2BA8P3MS9PJ%2FBkRw7Ai%2BFzzT%2FAcB7MVjht0oPW2sVnXYHCTVeMdLiHoKsG8V2ShL1KcemSIMrdfw37pIySNN0D5kshuAzPZz2Rf%2BVxhRvMj417%2F5OtTiWhARsu4kyB0HwI4l2BdcpfcQUwpTplkbgrXRbGgQWV550cCgsRg8NH2Lz6u24t8WY4zNgEr4KQ%2F%2Bkp5Sh%2BWnP31YYHeA%2B5VBm5glm6Blqfz5rx16MxSTU2VGBTpWPKxGfTgplT%2F1SxBUfJCpGetm71Ier7XON29U9YFkwTylf%2FgAa4ScnJRthdIuetgkZEgxDHn82mwGrKJVm3xfrsmeslX%2BUC75krb8qBq%2BmZpGKozESKyTf9G1li7LSzOznrUOyxupOYXCwPkKQJavFtnj5i9FZFLqcbm%2BDKSgNhLATqE9vyNJmyXUGp72V8N5wghxkXYQ5X0HvJa0uoqL20tg6VyKEMYbvE3e5ztUtMUaHXnPNt%2BildIGUFB%2BwESWDdGbihtEIVgU9%2BfbxETRLxMa3Xk5UnM1ASpBaeJns9Xw1kF%2Bz6jl6my9jYevxqFpPcJVvAY%2BSu2aLNG7bkPux6%2BcoJH8QjiMcbteN61flCVnr70HYkG3yvV6hz7TCsqXLbtlq%2B4wWA57mMuYHzZYR6Kct5xTqFJeB0Ec26s0letyW7%2FU%2BlELNwBOeueovIg%2BuiG2iL26%2FrCp8teXj%2BsyvE5Y1ByQtoL0DyN7fiFSBr9Coiq45WNJ2WAYWs3H0E9CdTofeajfhTr%2FonJQe2%2F103OhU5mXQwdm%2FfNA6qBwicAROBcYO%2FeY%2Fc6gKoAt%2Frs9BuKCGgVtCtEEMxlJYVH3cXLKfeQ4ie0T6EHlRrQXxUadZNa99h%2B6wcLUSaBoyq6h1EqhIpwcH9gX60lu7J%2Bo5t8NvhZWq%2BTN4r9DhRQO31pqYJ45g%3D%3D&__VIEWSTATEGENERATOR=47FAFF47&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION=oP76MGTpVWooOPn%2FxW6pcRiCrPKkBkufMJI%2BdOyUlKwMAUEOF%2FmyduHFhVJzMwxnsht8kJA19NEGkBo25Ltn7KOcry2iOCAnjp3JWEm6OqkSmwaTGkn30phbuobEa%2FuQ%2BHK3KAL5HaOALQ1FlRs%2BAZ8047OSUE%2BcaXg30WuKuZRTkpyuyZ2ZlQheRz7LAJ9Qy7GMelR9jjfgANRCFD4agnt4rrKmJhHx96QW3AOrFgPPXv%2ByK091TFSVPl5TJDsMJFb19mw%2FE8841snAm1fd8sB6M6PI99SnqYOzD08rC7DPQeAAMcjB9oU3cpAqzqaGKWE7LdhBmcMgnYVBsVlAd40LDjqnN0ZKThiYOaMkUJ35R8ZmoL4k2qnGGi2v0w%2B9DhD%2FPnlRN7ATiFD95%2BwCs4ZrHf256Y7sjYDxvLav7Hp3SHmeAiHRcHhS15HFLq9ZcchZilGPKC8ohhpFd%2BDczc0g5rQd2RFu1RNacHG2yZC825cZY1cLCgBlqUGWbJ%2BvzEHXJFzkc%2B1Vt6ullansyFj53yGNV93NWKYSZOOve%2FshLOAn%2FVv0KDqfBwSTtU3akPkHzdyOQvdJ4s9n57UmUHLWai%2FRXs3UJ0Ox%2Bn9JPbCDMsB1vp1LOHrqL8ehHxLXvTpHJ9tg%2FKv6yGbM2IHhFq9WEGQtB0ZmZOcKUbalPgi2uwD6U6Gz8RmqBkbLNvwIqCVhOrNY19YA7kbxvWOw3WYGNDbJSxJsJOfyyXTucNNIU4m%2BMiqShnLe8IyLaLfFtEIIWtsbrwjl5JUhZTnvsDx6QLXtiKa%2Bfq98evWQtqdEU0HltBpFUwDKzyEUJXPALFfFFunE7tqqH%2BiTS0%2BQxAIRFFliZm6GiKrdxD7r%2F9%2FCrFcvEPEqVEF532vxeikG6hRIZFsxYn0TadP6%2FtUh4XlXqSmozgYWRcQ6wotI4WtJc64EE8h8J0eUw%2Fbj2E44P9lcQk3X%2F6YOQDXdcds%2B4fyKGlqHRE%2BpiUkHBCY0b40%3D&ctl00%24hdnKeepAlive=No&ctl00%24MainContent%24hdnPid=&ctl00%24MainContent%24txtSearchAddress=&ctl00%24MainContent%24txtSearchOwner=&ctl00%24MainContent%24txtSearchAcctNum=&ctl00%24MainContent%24txtM=407&ctl00%24MainContent%24txtMc=&ctl00%24MainContent%24txtB=&ctl00%24MainContent%24txtBc=&ctl00%24MainContent%24txtL=&ctl00%24MainContent%24txtU=&ctl00%24MainContent%24txtUc=&ctl00%24MainContent%24txtSearchPid=&ctl00%24MainContent%24txtSearch=&ctl00%24MainContent%24ddlSearchSource=3&ctl00%24MainContent%24btnSubmit=Search&ctl00%24MainContent%24hdnSearchAddress=&ctl00%24MainContent%24hdnSearchOwner=&ctl00%24MainContent%24hdnSearchAcctNum=&ctl00%24MainContent%24hdnM=407&ctl00%24MainContent%24hdnMc=&ctl00%24MainContent%24hdnB=&ctl00%24MainContent%24hdnBc=&ctl00%24MainContent%24hdnL=&ctl00%24MainContent%24hdnLc=&ctl00%24MainContent%24hdnU=&ctl00%24MainContent%24hdnUc=&ctl00%24MainContent%24hdnSearchPid=&ctl00%24MainContent%24hdnSearch="
```

# Scraping AVA

The Grafton County Register of Deeds uses the AVA software
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
that date range. Save the file in `HTML/MMMMYYYY.html`

The `scrapingAVA.py` file sucks in each of those files
and produces a tab-delimited file that includes all the records. 
**Run -> Edit configuration...** to read the proper HTML file.

The program outputs a file named `AVA_Records-timestamp.tsv`

## Processing the `.tsv` files

* Open it, and save as `.xlsx` file for ease of formatting
* If needed, split the Date&Time column on the " " character.
It'll flow into three column: Date, Time, AM/PM.
Discard the AM/PM column.
* If needed, split the Book&Page Column into two new columns
* Check all the `PLAN` entries and fix according to the steps below
* Discard the `-` column between Type and Book&Page
* Extra credit: Examine `DEED`s and record transfer tax (see below).
* Convert all dates to YYYY-MM-DD
* Convert all prices to numeric, no decimals, no commas, no "$"
* Create a new tab in the 
`Tax Fairness/Raw Data/GCRoD-All-Data **.XLSX** file`
and paste in this data
* Append the new data to the "All Data" tab 
* Export as a `.csv` file and import into SQLite

**Fixing "PLAN" entries:** These don't have a Book&Page entry, so the results
for those rows are shifted one column to the left.
You must manually shift the entries to the right to produce the CSV file.

**Transfer Tax:** Examine each `DEED`.
Record its Transfer Tax by looking at the actual deed. 
If there's a Transfer Tax, record it in the rightmost column,
otherwise enter '-' to indicate that someone has checked it.
There's (almost) always a $25 LCHIP entry; ignore it.

### Notes on imports

* The five files **GCRoD-1.html** .. **GCRoD-5.html** were retrieved 
on 18Aug2022, each for a different date range to keep the record count
under 200. 
After processing by `scrapingAVA.py`, the tab-separated output is in
**GCRoD-N.tsv**
