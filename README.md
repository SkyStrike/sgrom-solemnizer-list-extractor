# sgrom-solemnizer-list-extractor
A simple program to pull ROM solemnizer list from ROM website. 
At point of writing (2019 June 02), the scripts are still working on the rom.gov.sg page.
- https://www.rom.gov.sg/reg_info/rom_licensed_sol_result.asp
- https://www.rom.gov.sg/reg_info/rom_grassroots_all.asp
- https://www.rom.gov.sg/reg_info/rom_licensed_sol_result2.asp

What this program does is to
1. Access the webpage (via HTTP POST request)
2. Download the page result as HTML (temp file)
3. Parse the result as JSON using some black magic
4. Export the JSON as CSV.

tldr: performs black magic to convert the ROM list into an organized CSV format.


Hopefully this can save time for those looking for solemnizers by name.


# Warranty
Well...This script is provided as is without any warranty/support etc...


# Requirements
- Requires Python3
- Uses the python library BeautifulSoup, json, csv.

# How to use
Just run the batch files required.

General syntax

script-name.py "codeA,codeB,codeC....." "my-outputfile.csv"

*Note: You will need to find out the code that the page is using if you are going this deep.*