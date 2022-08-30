'''
Scrape VGSI PID Numbers

Retrieve a list of PIDs from the Vision property database for Lyme, NH.
Request pages for each of the Tax Maps, iterating through all the result
pages until a 500 error indicates that there are no more pages for that map.

Input is a list of Map Numbers. This list comes from
https://www.lymenh.gov/assessing-department/pages/tax-maps

Output is a text file that contains PIDs found on all maps

Here is a sample curl command that retrieves page 4 for Map 408:

curl -vv -X POST https://gis.vgsi.com/lymeNH/Search.aspx -d "__EVENTTARGET=ctl00%24MainContent%24grdSearchResults&__EVENTARGUMENT=Page%245&__VIEWSTATE=wlcGoyoNj82xWgjyvgVCVFJlCLRDtQCVyyIIOZh8qsIKAgmiWE9ZTv7WsAObj5UZaO8Lo52Cn%2FagCqSrgQN5r9tqK0GupskvX2V9EjYfTOCc1GczuYL%2B1y2Cb0JtniYEdVLPEcA%2Bou3Kw1r3qjZlYLLL%2FPiGqdFiR6bKHpTxQEDG6DFgvcTVNxrFlntKM3f2Uv%2F4kYJmO89Ki7YzJWorfY%2F02EWT8rNlOmVAqEkfkHv%2F1p%2FqmmiBcZvGzDrd2NHwE0KoUqQ1bXa1dxjhX1558B20fM2dtqsMDa9vDINmUm25pHGVoyYhWB8W9CwZWFVyejn56AII4rrcnO%2FDswzCYpPfdYq4lyRJuIzviiPuvDQ8f2lcn%2B%2BjdDBNqVNuRcnvxP%2Fcc%2BLjTHnMvGGHVdt76WpRI%2BQ6M1IQUMYCpQjTU%2Fv4gMQxzuI%2BlyF7oVQ5VJMLIFgIjSeXeFAPQTWRDqyuk5dKe8pJ4dcBwSui7RmH6dqPVNcnhZz2w77RA1sPuPvP7XCZVLTIuZwGecaTsmnMZouwluXT%2BTGPJIUlYM2v6M5JVJklQNfkFzbqrSoIAsGqoYLw9ikx6vKqWmzrEv7o51Bo5awyAsXOsI3bv3hBj54%2B6082nP3MxL97DXh1SlkMyxeGwwjH3tTCA9NXOpE2zKyK%2B0WnMAqGTWaN3%2Bl%2FwXlH4CM5Jdivzy1y0qcij0lkL1UMsw884kzElm8NmgAoxpllCTciw9tL0KyYiGlRACUqJHzykN%2FL2s%2Fzq3uJMy4DPWLgYmbKwsR8fwePYNKJEDu%2FDP%2FY72dfQxhMzy8LXyYK6nr7M%2F20xw0TOgJ%2BnciRaf52HOzxVgZ3jlWNUncM6%2B0nJfIkE3n%2FW2bV5i1WcQ2DT%2FGsGfnpKJU1siFewfGCsKkk0%2FvnP%2FrAX9ROb1kEYQKzY4erQjiIm91E%2BBMwXFyNGo4V%2F4PM%2FjwQSLLk%2Bc8EurnHdbh5oVO1wzYCmHBbUuOWL6fzhiV6C9JTazVMFsOIikV6or4%2BTAWqUbQVWrMb99pg81D483jik0eJbnhMbMd5Ih%2B2oNeOmytLD8n2k1PdnYR5%2BpFK6oeCFJVY84YWIqHMnXfqhbUglAhKvQfv%2FPNNwIHHymyQUE5WVxhlaDgNJq8AEUBceDJTZV2WWOyndbHViINx3vDaD%2BdHZPbwMayN%2FjsrqMRQXGXGKuzE96RJM7XQpN1L%2BNgiJM%2FW6CNidJannxiIzToluN5cxByfM2ZqXLQThJ9eeY9%2B0EkPK3ZWdt9xuntj9vGZwLByQObvCcx0L3WxHGA68numC9gvWLddw%2B3L%2FVVFjhcPN5JVDVR%2B1lq4r%2Fizzx1ckyoR%2BiEW%2FKI4%2FQCp3fOJKO4Ia7yeQXe2zMbju3FuKTzOtdiFVUUijjMy9hr%2FY5jrdcwl8CX35eU%2BRQWRloRKxoi1LyXwAZqb%2B%2FY2DxKBMGbKwRfuNuksXu8UcEWBAPa8XfHJlZeoxGXQY0LlwzX5zEkX%2BWg0CoLdtZQqGtOjrl6rLtyG6SyyceRvtkzFNwOElXf3mdHVrPD0VgJeL8IaxDih%2BT8QXTe%2Fm2R6%2BPfsgmygsej1wQLaGZCukEW79KVYhoORm%2BJFD5FpQZT%2Fse7utsgMTNI%2FjG0flo6SsINO0ic4QrhSYGP3%2BPWw8cJh9pz662V26uLwDraLiCgwlpS2k2%2BYxVYCysaYsUX9lJieaPIHhCxK%2Fo7jDmLRF1FIo8eetGJen5mXDXSveQry5QA3biab4fi8ko1aF3e%2Fmvmkr2ciuqZuegYlOHrGvnFuhJqNyVz0l1eTjykLXuIXfAqKplB%2FR0V3pLCmeIsoMLv%2FIBKKZ1wemLZOwouoiTyQVbaV1UqC2ZmR%2B1LdBXaavJMN5hs%2FQ5TLdBSYO7oRMHxPB0hOp88J5jPOZpg5qigf1JsbdPfQhyKPSZVb%2FzGLtYk77mgpsXj9N9moeECJfzv4D6p1N1AdvC0Vj2tGJ%2F97jIC2Va%2FkC2zc1K9dh7xAC4sPqGHmHpuTsNtgeWEQQg6ATjuJ6gfERmwl0aSL6tjXS8%2BiIxjf6c%2BQVC8y3ZdcniP32mjMVgJZutyQaUZwuGC0Pfn7Q8KRMR7ddeMmZQMXP7RRmBvCQqWUKIvg9MytvW9y17bZmThxwgLWYEUCU0M%2BS5%2FFkg1xzEyf6sSetLR3pHoyvuHoiUVaw6va4R0%2FjZMPuIJ7kIR%2Bm%2FSdaIBpHuHJ5XkfuKgZ8AEeG%2FnPeM%2B9ktZ5MTvXhICIBXwcDE4WBr2xXZ5LFEkSmPWZRdPMtQyuGJ6%2FQDt8s8EJ2jQDIYvMTL1KnRqtR8Bg9i5ATxS0H03IdJLZa%2FeQWxcZjwu7OM8hVgSzICXrxGi2qtspRESkSiBUBj61CuZkaFdxMuBEXYeFXRNfDSzNg1wJiKuBl0y12TfUJE%2BHlR%2BHF%2BPmpG6cgrU9zy2wCFqZLMXCc2%2Bp94aWau85b%2BE3z%2F3Q2ZUSfAkgTjIy%2BWx1oIjpItx%2BLCNbYnc8WwoaipWc6G7A5OR2TWsjpzRDC14xVsBGkezhS8LNxIfby0AqusORypTfwBy%2F6TdCAMLOQ0MWLKHSh%2Bsey2zeDZ3yfmyVAXf8W91xBVhQe0Ad%2BgUouyIBuMeA27T0HtuGgXQIynXFO3ASAu%2BDXJQnd%2FPHsbfM0DbW1CRW3N%2F%2BdtgIkiiRETpLEyC8sEFBqqr5EymYhyPoWibxG7yoL%2BKfm4Rdae5Ccxr7eXmHo663EivAgtSvVl%2BB9XuZ9%2BpLDxdVStY6rl3Jsg7okfOa6bxCKw2dATRJTuYmfLbQccizEYnauBwkwnB9OnphBIr9JRdEREo4eV20h2rEoVTRYmMptJiXjbTolggAiCVHzIMSG%2Be4jhygL%2BVeFRPDXSGXyLdCFXxsdurFJiLrZ6YPHktWwIa8TXGKQU39GKLYpSCE9t%2FKIqvRVL9vBMGITC3QDSe44jGd2SwBVZempgjyG8Q0DpkQqjoXWZqGx03R%2BP8Jr7EVGLA6UZYBYlgMY3okPQwL%2BaG3kw4FvINIpClREerL5iPobpQX0%2BlhPjebvK2i85mo1QwxSQbptwB3DvlK4bM%2FHz7BAiGllLrAYs%2BRioElbvdzqxT73n99LMl9NjpQtEdQ48yYmKJaxkk6Oc9vpB7UNDdPBSqWCxnrMoQJ3qVLWo2u2E18AjHkS9RS4O6NLeofsThQ07NauIu%2FrIsbl9GWjZ37HqU37R4RkE9qy1mauQeheMe1IvQcPqFqMgjpRHo1Oa3DHMrcIifTYV%2FHtyAeQ46gbes%2Br3l%2BrZJ2r7F%2BwQGiKt9yRJNpiH9Nnq%2BYOJTcO7SU%2BuqjAHvsaIr9x1Y2uU0iFI8LbViSFpro6eOTqL48d%2BG%2F%2Bn4za%2F3udBY0oeov9XCdVmkugs0CJgqlsZ4hKCMfTyELIrFX73hKQ%2FJd8%2F%2F2nExOzVO6nSBJXDXe5j5esefbbx7eDk9jro%2F2Nd74GFzbKIBe8T%2B8TGm%2FKLQuOSyvajbdLa%2FVyvHj4TxUn6D1lyonSj3xnZzl3Ri2%2FHoz8REOg6RsgkObzhAGtmrhC1HflDJnEN5f0%2BFTwxpE80qvNgBZ%2BygXUGyM4Jzc1uMskBlKFffMG2r3Fbq1aF4N8HPQ%2B2KZ0rYOojHUroX%2Bm2OP3LZRrCWf%2BiMvzBdnxoVcyiSIK21i8TB%2FTPjj95jvSzL6JRfEdB%2BUBbZCUoOKwICROIbdre3PgT61sM4s1NXKZjd8Eh2EuL6L7KWoYMV0KLAFRPEoCWQzxcnPmEyvBhtWLUiPc%2BH%2FpBkHcI5qxgvPkz9sbOCCCnbToDgukAbpjCHN5KIG1k%2Fut5PTmxLVDBg2sYsVbn4HmILrbnu2cQRQ6UmaAgfsfYSNBuoKhZo2FuhACWBwaFoBql0CkE%2FwcJ0rF4meF4ZsnM049ig5iXIIw%2Ft%2BIaRhKjy9AiP%2F8%2BlHGkcjCIm1pjdOQsisSXOLKBYzShXizShgXpTBzssln%2FJ9UFjc%2BnZh6iZLx9b0mztNjy8xU8YbmNJ9HtfFjFB%2BOB99jDP0yOJf5DT21%2BXEAU3tanG8K6UfDLAtlTh6RyK7BDL%2B6Lr616qcAk5jkaiqb7e%2Frfmu%2FS4sqtm9lgscoidEleFesW1LbAPGOBsu6oUEeo1GVWdDZcZvvtqqJFulg1giksEf6Ppu6LZ7mzSnV4i1%2Bbqa7epq0KiSPpzavQb6%2FbkT4WB20AAEwsSeFKmfQ0tLYKNT8tBuVe%2BD06W6MQum2W0BRBW2PF7JAbaO5EiZu0Wjfx75nbPq5C0tA%2FFLfZHR1wxy%2FH41Q9XAM3r4kodDfobIXoJvFDq74%2B9qHvipLjjnQOIcHlivmqn%2BHak1Rd%2BkqIkddp9UTtNHGhE2LpAhdUx6WPUoUxlJsxMWl9qGx3%2Fowqz2aPxASF1KQ%2FWAUaNwbk4GXq1bX%2Bc1K05MRIjjZmL28UEhggX7j0%2BYqAF%2B8B4bCS44veiaO6odTit40mfjfLmymv9eNZ9yNQMGbdZaUlzjQRTR65chdWxZNfSvH3Tu%2FwbqxtOfU4%2B%2BmQ4qZu5hw1Y2%2BBOCFd2akopt4X4S5KZpl6ZDmpsH05PBWCJGTHhPESVUWN6ISS%2F6Y9MI8VXeiFUFoRnXxzCpdy%2FtDOM4yW7g5HK7uMPNdY1tiusIHc64dwZHntcRF4Z4XMfKvXYTW1juN8a0F3bqFrsqooPwtRtPE89KIchawRYlrBpy1GIjcjxpJay0BNUhlHnYMu%2BrCc2ftsl03Pnpd4WrVaqnrvlaQFO6EXEjSuKTBswXqi9LPD%2BsiLEGaBOUAwnSBFfrkmfU%2FpTtWdB3OEnrDJzrkzHnM904B%2B3TK%2BKkJDz%2BPdpnJoSTOb807xL%2B1UAMf6Qdjf80WMhPJ%2B8CtTC%2FBUhvWtBdtZoKWeSV4IQF27eysSJyQuCpRAfasT1bMhIDVPSHTQb7OwY4rtOnRGbG%2BpMwelx3hwd1Q5wQIoo%2BddJNcsFAUJQtvbgfWSLL0UexJ0eKrONAJe6xkc8GjYdLwnEXC1O7Nsb2HE0NAC6oPW0MhzYWW34iDR00J%2FF98fCrPbzt6sVIiwyOQ1bieOE8t8YkDZEl%2FEQaWcxG5y%2BSEh4H9ZsmwMQJl3RNh97tCrnP3iICqiJnJzGy%2BBveGVlAaxT43TojoSZXLoHaLMHO2hGohi6AULzgooRCtOaSdoAc4%2BcGiBQHN%2Fg%2FSaz5UJJ3y%2B8ruGmofbR0JxOhoBLdNjpmJyGDVBO90tek2nUcWEzVihx6BZsBxhMhAbSB7TFNONMuf%2B9tOmm3ZatGr1bgYHe%2Bj5XRLysBgbhlTUQb99sGWbnxX2dTht8%2BKCubWwrMf%2BVvsaoHpoIahwyU930R6%2B62balXmMiarpNS9K6WPHkXB4BaccXPZnr2dV9eo13gls7bZyrSr8FHmfYQCsmuhGRtASLZBto%2F8qFOfgL58bj1vZ%2FW9y%2BnBXv9TRGSxPhlXBodDA6JUcYUG9qiybk43RUu0WdD9eseiuUIvvJUDH2bkbyUdN%2FuUOLLFS5b5%2FQtexZMUYO3s3VAm%2BpDZgIdBPJFjskUn3FTgwTJQYSs9mRHtTIc%2Bb%2B%2F64Gn1SWh4P%2BwWhkDdOAvHZ3EG81YhXlIRxnHHzddkR9Zw%2FW5t3J5yty3cw4B0DJhDKQS7F%2Fej0uZ4PL1UfhcUO9e80PauejpML3r%2Ffp%2B7XPAJ3ILsuas4Hnyjjm71RXH5zlciCNMEVO5jf0AAlWVeaMEi1lzn57qXaDSCXeFeiEntvuAF34%2FczSSAaYke86iX0xLecAvNFnjyATVkKtjRM79myVXLIyF35qjHx%2FuvS3kowWzPOqHfRMXmiJpy%2BxpnIbUigFavbWUN4o5qV%2BKzBJdV0DUSeSY2jyeu3nfgSL9u3%2F2DGl1h%2B%2FyBs0kfbsRre1IgRD2L%2F0Egm8fxVfKCF%2BDAO%2FPbceNnP0%2Bz4ouv2Pr%2FTz6g1pwlkipDKH26khxECHDq642hhE4cw%2Fh1H7UyMLQOloJYWBzDi0AjQofq1OAvQsYAuotV1gWzsNDu1uKWfB83cGRm4MPFDfYqS8krhQdYwC9ibS%2Favdm3SsDxeXCxEdoQx4U3CWDDwW02n2Bw2dtRI9%2FHxyaTuo%2F20XwvoLmnnBdSvBBFh2PaOtCTFtV2CX33KpzxjFLysvX6wMpS%2BE2uBQPp7y%2FOSHDndBuDCytbsVs1ZqNfLd6arTDVaPpWNlR3sfrscD29nVF%2BxWTzEGAg%2B1FwIg46zfJsolEwvZzsntHAguhe8CK7RGYUj820yAnZ86P%2FJPxqcPJhFTyp3rTr%2BMD7ty9m0lNvQAVeb8PGz00wVCkDHyvv%2FbTt2OXqRKYlpE3pL0JMnEVPxuZuHFfh1KJCdcc%2FiBcTfzpEbC3MKiYumdkFH7HE%2FdVfK8wyhokHUvS9Kxu7HH3SuJT5iWweFj2RGIDlnwmPXotDaQuTpucQrWS3%2BhU3t65%2BJCCT50K%2FkWI53J6Ojh4jMsiFuO7wY3sFakii5WZPeH%2FuPiWCQcrCSrnIcfOaFDb4Ztm0Z04ous%2FljbWS4RQ77fvNk9nppM0Wef4lNdq4N3jreoN9EDIwbwkKE2b9nBsitTB8dx2UOd9kp3ky2YMvlfIzPkOB5ycMa6YZibcsZpWy5hcqqYPMUr8zqauEiAIUR3TfaXaE6FLgtcZcFoLoCb3bxS15M8B6lMCNss5N2ZqFnqlXpNgnzG5vHYG5aBVWYPGngkQjbMvi3ZuzTumVjhWeYo%3D&__VIEWSTATEGENERATOR=47FAFF47&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION=nvTOwheQqKA1ylid6rgkKiLdyIqjF1ccU80aki3ovquvFG9EXX%2BGpwv5GIA2w2nJCNd7ZnqgZXqiFLFAOIxw1rY%2FlTORqN8X7k8tVLNhLCQ2LkyfbsH6uA8oSowlFDUCq4SmrEUs%2Fa0%2BoQzuJngHPfZiDLM8OeSgCIuC5OXigKAFDD%2FDizVqs7zHyHk8k2JKn3Svce6W5b%2Fzc27MYEAPjcnRufk6HtVdzBz37DagxXl%2FLdUlplhvaCzxiD8GsF2LqMxAIwaNfobmebLc1IarSuXEFXIyNd1x1UClsst70jIc8MpqdF2bg6zFOxo7fBaNGEjoiP6o9PaaECP8LPigLVEuQqXPuF%2BaXZsxJhfnOdnvgCPoqUrNbpJkF%2FQBL2xN7Z56UCpXQXDpOY93r4fAvFCUAaOPKm2y83DpdqTLOIiVEIa2SJ9mdB%2FUa7EU1Ei2uiEqywKRfSQm893je6lmdD3RF928t%2BM0tONk6NlOBgRropAdqlH0%2B0gYf99xM7nu%2FZjEOwqkaiXIsHz9QlmAM0qpuBMGz5Na7aAXoBlnOZ4o0D54tag63vxTZBggK4fIoMLFuUAGEm33w%2FNHUWzs9IB1DCq3KeMhAWk6h3VD%2FjvMlB682nfE24RuTEPm6kru5UC6i4bPTKxJCPKpk8PNwVB9vtzdOUUPBykCgbxmpNry8NsD2%2FXhRKkWoaFITewdvUgApRez%2B42BdVhaOabj9%2Bi%2BrA0wSSngLRJWf5%2FOYKV6MzmtEB31X%2FRGcnX8xCU5eVH%2Bc1j7ifh1EgtRvejJ0QC2WoY2cSEH%2FD1kaci71H1yWNR7eEn6FkV3Hd7bifY3w%2FLDOisAqkMp7TR%2FHWI85VodqCe%2FkWxcy8DFw42VO8MbzpXXpfeKwciWDEky9Lb3XqL3%2FWCAU5yfrMCQDaXnKw%3D%3D&ctl00%24hdnKeepAlive=No&ctl00%24MainContent%24hdnPid=&ctl00%24MainContent%24txtSearchAddress=&ctl00%24MainContent%24txtSearchOwner=&ctl00%24MainContent%24txtSearchAcctNum=&ctl00%24MainContent%24txtM=408&ctl00%24MainContent%24txtMc=&ctl00%24MainContent%24txtB=&ctl00%24MainContent%24txtBc=&ctl00%24MainContent%24txtL=&ctl00%24MainContent%24txtU=&ctl00%24MainContent%24txtUc=&ctl00%24MainContent%24txtSearchPid=&ctl00%24MainContent%24txtSearch=&ctl00%24MainContent%24ddlSearchSource=3&ctl00%24MainContent%24hdnSearchAddress=&ctl00%24MainContent%24hdnSearchOwner=&ctl00%24MainContent%24hdnSearchAcctNum=&ctl00%24MainContent%24hdnM=408&ctl00%24MainContent%24hdnMc=&ctl00%24MainContent%24hdnB=&ctl00%24MainContent%24hdnBc=&ctl00%24MainContent%24hdnL=&ctl00%24MainContent%24hdnLc=&ctl00%24MainContent%24hdnU=&ctl00%24MainContent%24hdnUc=&ctl00%24MainContent%24hdnSearchPid=&ctl00%24MainContent%24hdnSearch="

'''

mapNumbers = [
 201,
 401,
 402,
 403,
 404,
 405,
 406,
 407,
 408,
 409,
 410,
 411,
 412,
 413,
 414,
 415,
 416,
 417,
 418,
 419,
 420,
 421,
 422
 ]

# cookie = {
# 	"Request Cookies": {
# 		"ASP.NET_SessionId": "cqggbvj4c4w4fogikruiyook"
# 	}
# }

# cookie = { "ASP.NET_SessionId": "cqggbvj4c4w4fogikruiyook" }

reqParams = {
  "__VIEWSTATE": "UFv4+rE4OWxooK8ASSHmnfoe03KVmH9YIIN7xvPsEIyRaM34LLIPk93HasVbq9jUQZF0doTxMLOhpehs5f/m/RdP5ElJyli/mA7zDqEc//BPULI372rs2ux6u7NhT8ctmBkGCLEiduCA3zA/M/pQozxfh5nsBJmfR5Ji/P++GNQR38XFYiB8acVaHVkUjv4iMpcUIobLCrzI0tRT8/bth79OBaOi8ynfjqmctvfZAdw6SIiEUvprvQsugfSSYWtpecGrOUouJvItHo8noXxOei1XKzi7nMTUSNfnwtUwaOwLlBJXbEMNxR0/17afVEgw2GCLBdCQhTrgWgzOS9HsGiciyX0KypTa6E83jmjdf+6j1xVPaehszAyZciF+0X1h9KmguWBdxKHWGxgV0Ot+G+ULfgBBWtDm/KzoQliO61wUoAUCTqrrsJUxFEe877psc7OsrGsGMGCSJkMm968BHUJ2TnDjij2ZWMEcNx+0N8wqgM1DHu52wrIlg1TPOJfad2Lm1O/Gwh5DThVBwH7LkIBS3Jk9kXHGy+t0ktqWl8XScmhqBc+wBE+QDDBMFglVm/NoIARJaNaHafTet28mcRI5iPaYjOBYmSNvm72AoUPYgGMAe9I+kSlVwyH93lvcE2sNAgKzfhqH4lINImnftyNyoFQjtGRIK81hmCG9kvRM0/3ORrMjl6I9hsrltWV5oVVDvdXFS+RtTxKmM2Wvun+D5Bf+ILJz19OPdtBYpwVkUExXCzW+Lro+mbZeyztClXSIH2mMWk5Yxn5H4Tm0kA==",
  "__VIEWSTATEGENERATOR": "47FAFF47",
  "__EVENTTARGET": "",
  "__EVENTARGUMENT": "Page$8",
  "__VIEWSTATEENCRYPTED": "",
  "__EVENTVALIDATION": "XV2OlJp+0ShEWhv1hKuwlWjAFmEQH+Pk/oJo6mCnyJSoSeDETsDLnRPmA9m3qUt/K6ojPSDBcXDpq5Sgn1p4r0ThjUh5Tne6jcElCeqSWIXPH28EYNR0hp1D3AE8eJiiUb4NP9wFow+doo/kKO7VG2qppF/dtXfQfzZXrvx0mRkT2DOYUBaw4E7mm4ompnZlubpW5Of8Z57tdsw9Ufo4q/GYp4iMpMquQdgI8ddYRkj7b6XyJQuYdj3g0ChvyzfYYu+Bfu6A+bJtmhZ1b9xieNNLdBABparwpQsfmVVbJDmKPmjfimZlsNOrDxoxwWx3KT2lQ55w5wDajqkCEjB19i5mHGXnVYVGOShMhqg+ZRPdIZKwxBq/XwlnY7zQT7l5utyVwNxR0yTzSbXSLsWS6eq43+G0AsN94HyfDRLWjJpTYxGVFRyGPd6Mp9fNmkZnUkSdrCor6FiZPpavcu8OWjdZNvIqGtzKCUSl3SlzeWg3uWKYiOQRj9XMMdfEDwxi0zws60OZ+UBGLL8vyAcYu6CPf7V9eUYg2XwVQfaWI4CGG0WYSBRLDjHJObdYakaJpMLnbof9XpVcONSPD2yYLoQ4xGDl9UNN/GMuJl6S0ik3gcoBcHgsZ1sUmLEdbEFyX7uum/QKQRciRYEtbk3wCKOaUCofUH/NYzoE2mRcw+CH4MSC3BGBjo6B7IVX8XQL/N81CdxGwQw9AQ9hdWFC0HFq8dcjMiI4TC46WWlc5xHYZNUB0+TFXkZwwgtONbKKmzdVjF3obiIHoGjE4y0kxUQhhtn/r5yRjqZg5R+hQZIKpZXmLz+1AV/dUrYiJFnfJOxaGHxkCA9dUdIMwaWGBQ==",
  "ctl00$hdnKeepAlive": "No",
  "ctl00$MainContent$hdnPid": "",
  "ctl00$MainContent$txtSearchAddress": "",
  "ctl00$MainContent$txtSearchOwner": "",
  "ctl00$MainContent$txtSearchAcctNum": "",
  "ctl00$MainContent$txtM": "407",
  "ctl00$MainContent$txtMc": "",
  "ctl00$MainContent$txtB": "",
  "ctl00$MainContent$txtBc": "",
  "ctl00$MainContent$txtL": "",
  "ctl00$MainContent$txtU": "",
  "ctl00$MainContent$txtUc": "",
  "ctl00$MainContent$txtSearchPid": "",
  "ctl00$MainContent$txtSearch": "",
  "ctl00$MainContent$ddlSearchSource": "3",
  "ctl00$MainContent$btnSubmit": "Search",
  "ctl00$MainContent$hdnSearchAddress": "",
  "ctl00$MainContent$hdnSearchOwner": "",
  "ctl00$MainContent$hdnSearchAcctNum": "",
  "ctl00$MainContent$hdnM": "407",
  "ctl00$MainContent$hdnMc": "",
  "ctl00$MainContent$hdnB": "",
  "ctl00$MainContent$hdnBc": "",
  "ctl00$MainContent$hdnL": "",
  "ctl00$MainContent$hdnLc": "",
  "ctl00$MainContent$hdnU": "",
  "ctl00$MainContent$hdnUc": "",
  "ctl00$MainContent$hdnSearchPid": "",
  "ctl00$MainContent$hdnSearch": ""
}

import sys
import argparse
import requests
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
# import pycurl
# import certifi
# from io import BytesIO
# try:
# 	python 3
	# from urllib.parse import urlencode
# except ImportError:
# 	python 2
	# from urllib import urlencode


import urllib3
# from urllib.parse import urlencode
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random

import re
import os


'''
Main Function

Parse arguments
Scan through file
Build up dictionary for each IP address

'''


def main(argv=None):
	try:
		parser = argparse.ArgumentParser(description=__doc__)
		parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('rU'), default=sys.stdin)
		parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
		parser.add_argument("-e", '--errfile', nargs='?', type=argparse.FileType('w'), default=sys.stderr)
		parser.add_argument('-d', '--debug', action="store_true", help="Enable the debug mode.")
		theArgs = parser.parse_args()
	except:
		return "Error parsing arguments"

	fi = theArgs.infile  # the argument parsing returns open file objects
	fo = theArgs.outfile
	fe = theArgs.errfile

	# for i in range(len(mapNumbers)):
	#     print(i, mapNumbers[i], file=fo)


	# c.setopt(c.URL, 'https://httpbin.org/post')
	# post_data = {'field': 'value'}
	# # Form data must be provided already urlencoded.
	# postfields = urlencode(post_data)
	# # Sets request method to POST,
	# # Content-Type header to application/x-www-form-urlencoded
	# # and data to send in request body.
	# c.setopt(c.POSTFIELDS, postfields)
	#
	# c.perform()
	# c.close()


	url = "https://gis.vgsi.com/lymeNH/Search.aspx"
	# buffer = BytesIO()
	# c = pycurl.Curl()
	# c.setopt(c.URL, url)
	# postfields = urlencode(reqParams)
	# c.setopt(c.POSTFIELDS, postfields)
	# c.setopt(c.WRITEDATA, buffer)
	# c.perform()
	#
	# # HTTP response code, e.g. 200.
	# print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
	# # Elapsed time for the transfer.
	# print('Time: %f' % c.getinfo(c.TOTAL_TIME))
	#
	# # getinfo must be called before close.
	# c.close()

	urllib3.disable_warnings()
	# headers = CaseInsensitiveDict()
	# headers["Content-Type"] = "application/json"
	headers = {"Content-Type": "application/json"}
	from http.client import HTTPConnection  # py3
	HTTPConnection.debuglevel = 1
	
	try:
		# cookies=cookie
		page = requests.post(url, verify=False, headers=headers , json=reqParams)
	except HTTPError as e:
		output_string = "Can't reach the server %s?"%(e.response.text)
		print(output_string)
	else:
		print(page.status_code)
		# print(page.text)

if __name__ == "__main__":
	sys.exit(main())


