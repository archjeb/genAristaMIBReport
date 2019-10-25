# genAristaMIBReport.py 

The purpose of this script is to generate a CSV report of Arista MIBs by automatically downloading them
and then using the mibdump.py utility to parse and generate json files.

# Author
Jeremy Georges 

# Description
genAristaMIBReport

The purpose of this script is to generate a CSV report for all the MIB files that provides a *pretty* spreadsheet
of all the OIDs, types and descriptions by parsing the MIBs. The script also automatically scrapes the Arista website
to download all the proprietary MIBs.

The main reason behind this script is that several customers have asked if a nice document of all the MIBs existed or not. 
While the source of truth for SNMP has always been to refer to the MIB files themselves for details of what is available, 
no convenient *pretty* document existed. The purpose of this script is to be able to generate such a document dynamically
and easily. 

By using the '-a' switch, it will also download the IETF and IEEE based MIBs and provide these too.

## Dependencies
Requires:
* BeautifulSoup 
* mibdump tool from http://snmplabs.com/pysmi/mibdump.html
* Curl

## CLI Arguments

```
usage: genAristaMIBReport.py [-h] -o OUTPUTFILE [-t] [-a] [-v]

Arguments for script

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        Output File Name (CSV)
  -t, --trapsonly       Generate Trap Report Only
  -a, --allmibs         Generate Report for all MIBs (Arista, IETF & IEEE)
  -v, --version         show program's version number and exit
```
 


License
=======
MIT, See LICENSE file
