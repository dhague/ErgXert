# ErgXert
Python code to convert ERG &amp; MRC files into Xert workouts. Requires Python 3.6.

Also works with RPE data (copy data from the range **B15:E** in the relevant 
workout page from the
[Sufferfest ERG files spreadsheet](https://docs.google.com/spreadsheets/d/1ehIbV4Kldv_k82JtadNavpeZaI7o9JGHoWghDitrM-4/edit#gid=2117722110)) 

Using RPE data allows you to customize the workout by assigning any Xert effort level to any Sufferfest RPE level. 
For example, you might set RPE 7.5 to "100% Threshold Power", and RPE 9 to "5-minute mean maximal power".

**Usage:**

Set the following environment variables:

| Name        | Description |
| ----------- | ----------- |
| XERT_USERNAME | Your Xert username |
| XERT_PASSWORD | Your Xert password |
| XERT_FILE_NAME | Location of ERG/MRC/RPE file |
| XERT_RPE_MAPPINGS | Location of file mapping RPE levels to Xert effort levels (RPE only) |

Then run:

`python3 erg_xert.py`
