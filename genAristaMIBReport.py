#!/usr/bin/env python
#
# genAristaMIBReport.py
#
# Simple script to grab all the MIB files from Arista/and or IETF/IEEE and
# parse them to generate a CSV with OIDs and descriptions.
# It will automatically scrape the Arista page for the proprietary MIBs.
# The IETF and IEEE MIBs are a little more challenging in the way they are presented
# on the Arista site (some are by MIB name, others by RFE#).
# In the end, for these other MIBs its easier to maintain a list in the variable
# section of script. Just add/remove whatever IETF/IEEE MIBs are listed
# at https://www.arista.com/en/support/product-documentation/arista-snmp-mibs
#
# Note that if you have any MIB.txt files in the current working directory,
# the script will try to parse these. To clear everything between runs,
# manually delete the .txt and .json files  in the CWD before running the script.
# This is by design, because you may have a situation where you want to parse
# some additional MIB files that you manually place in this directory and you
# want the script to parse these too.
#
########################################
# Dependencies
# -----------
# This requires BeautifulSoup4 and pysmi.
#   pip install beautifulsoup
#   pip install pysmi
#   
#  Also requires curl
########################################
# Change log
# ==========
# 4-19-2019 --  Version 1.0  -- Jeremy Georges -- Initial Script
# 4-20-2019 --  Version 1.1  -- Jeremy Georges -- Added CLI arguments for options
# 9-2-2020  --  version 1.2  -- Jeremy Georges -- Changes to support Python 3. Pull Mibs from simpleweb.org
# 4-20-2021 --  version 1.3  -- Jeremy Georges -- Updated IETF MIB listed required for newer EOS versions 
#                                               - Also added IANA MIB List needed for these newer versions
#
########################################

import re
import os
from BeautifulSoup import BeautifulSoup
import urllib2
import glob
import subprocess
import json
import csv
import argparse
import sys

# Check to make sure pysmi is Installed
import imp
try:
    imp.find_module('pysmi')
    found = True
except ImportError:
    found = False
if found == False:
    print ('Failed to load pysmi, please install from pip.')
    exit()
#######################################################
# Global Variables
#######################################################

VERSION='1.3'


# Unfortunately, the files available out there are based on whether its IEFT or IEEE,etc. So we'll make a couple of lists dependant on source.
IETFFILES=['P-BRIDGE-MIB', 'RFC1213-MIB','RFC-1212', 'RFC1155-SMI', 'RFC1271-MIB','INET-ADDRESS-MIB','TOKEN-RING-RMON-MIB',\
'SNMP-FRAMEWORK-MIB','SNMPv2-CONF','SNMPv2-TC','ENTITY-STATE-TC-MIB','SNMPv2-SMI','MAU-MIB','IF-MIB','Q-BRIDGE-MIB','RMON-MIB','RMON2-MIB',\
'HC-RMON-MIB','EtherLike-MIB','SNMPv2-MIB','IF-INVERTED-STACK-MIB','IP-FORWARD-MIB','BRIDGE-MIB','UDP-MIB','TCP-MIB','IP-MIB','VRRP-MIB',\
'IPMROUTE-STD-MIB','IGMP-STD-MIB','PIM-MIB','HOST-RESOURCES-MIB','ENTITY-MIB','ENTITY-SENSOR-MIB','ENTITY-STATE-MIB','MSDP-MIB',\
'OSPF-MIB','BGP4-MIB','SNMP-TLS-TM-MIB','SNMP-TSM-MIB']

# IEEEFILES=['LLDP-MIB','LLDP-EXT-DOT1-MIB','LLDP-EXT-DOT3-MIB','IEEE8021-PFC-MIB-201806210000Z.txt']
IEEEFILES=['lldp.mib','lldp_dot1.mib','lldp_dot3.mib','IEEE8021-PFC-MIB-201412150000Z.mib']
IANAFILES=['IANA-MAU-MIB','IANAifType-MIB']

IEEEURL="http://www.ieee802.org/1/files/public/MIBs/"
IETFURL="https://www.simpleweb.org/ietf/mibs/modules/IETF/txt/"
IANAURL="https://www.simpleweb.org/ietf/mibs/modules/IANA/txt/"


#######################################################
# Functions
#######################################################
def matchme(strg, pattern):
    search=re.compile(pattern).search
    return bool(search(strg))

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='Arguments for script')
    parser.add_argument('-o', '--outputfile',
                        required=True,
                        action='store',
                        help='Output File Name (CSV)')
    parser.add_argument('-t', '--trapsonly',
                        required=False,
                        action='store_true',
                        help='Generate Trap Report Only')
    parser.add_argument('-a', '--allmibs',
                        required=False,
                        action='store_true',
                        help='Generate Report for all MIBs (Arista, IETF & IEEE)')
    parser.add_argument('-v','--version', action='version', version='%(prog)s '+ VERSION)
    args = parser.parse_args()
    return args

def getArista():
    print ("Retrieving Arista Proprietary MIBs")
    # Lets get our file list first
    URLPREFIX='https://www.arista.com/en/support/product-documentation/arista-snmp-mibs'
    url = urllib2.urlopen(URLPREFIX)
    content = url.read()
    soup = BeautifulSoup(content)
    links = soup.findAll("a")

    FILELIST=[]

    for x in links:
        if (matchme(str(x), ".txt")):
            FILELIST.append(str(x).split('\"')[1])
    # FILELIST has all our filenames we care about
    # Now lets download the files.
    MIBURLPREFIX='https://www.arista.com'
    for x in FILELIST:
        print ("Getting file %s" % x)
        os.system('curl -s -O %s' % (MIBURLPREFIX+x))

def getOthers():
    print ("Downloading IETF MIB Files...")
    for x in IETFFILES:
        FILENAME=x+'.txt'
        print ("Downloading file %s" % FILENAME)
        os.system("curl %s -s -o %s" % (IETFURL+str(x),FILENAME))

    print ("Downloading IEEE MIB Files...")
    for x in IEEEFILES:
        FILENAME=x+'.txt'
        print ("Downloading file %s" % FILENAME)
        os.system("curl %s -s -o %s" % (IEEEURL+str(x),FILENAME))

    print ("Downloading IANA MIB Files...")
    for x in IANAFILES:
        FILENAME=x+'.txt'
        print ("Downloading file %s" % FILENAME)
        os.system("curl %s -s -o %s" % (IANAURL+str(x),FILENAME))

def genJSON():
    # Get our MIB files as a list to walk through
    MIBFILELIST=(glob.glob("*.txt"))
    # If we get any successful or failed MIBs, lets just add them to the appropriate list for a summary afterwards
    SUCCESSLIST=[]
    FAILEDLIST=[]
    #
    for x in MIBFILELIST:
        print ("Running mibdump on MIB file %s" % x)
        # mibdump.py --generate-mib-texts --destination-format json <filename>

        # Need to specify local dir as source too in addition to the defaults.
        CWD = os.getcwd()

        # Need multiple sources including the local working director
        # FULLCLI='mibdump.py --mib-source=file:///usr/share/snmp --mib-source=%s --mib-source=http://mibs.snmplabs.com/asn1/@mib@ ' % CWD
        # Switched order here...use remote instead of local.
        #FULLCLI = 'mibdump.py --mib-source=file:///usr/share/snmp --mib-source=http://mibs.snmplabs.com/asn1/@mib@ --mib-source=%s  ' % CWD
        FULLCLI = 'mibdump.py --mib-source=/usr/share/snmp --mib-source=%s  ' % CWD
        FULLCLI += '--generate-mib-texts --destination-format json %s' % str(x)
        try:
                    subprocess.check_output(FULLCLI, shell=True)
        except subprocess.CalledProcessError as e:
            FAILEDLIST.append(x)
        else:
            SUCCESSLIST.append(x)

    print (" ")
    print ("Successfully Compiled MIBs:")
    print ("-------------------------")
    if len(SUCCESSLIST) == 0:
        print ("None")
    else:
        for x in SUCCESSLIST:
            print (x)
    print ("\n\r")

    print ("Failed Compiling MIBs:")
    print ("-------------------------")
    if len(FAILEDLIST) == 0:
        print ("None")
    else:
        for x in FAILEDLIST:
            print (x)
    print ("\n\r")


def genJSONReport(args):
    # Now Generate our JSON report
    # Get our MIB /json files as a list to walk through
    JSONFILELIST=(glob.glob("*.json"))
    #
    if args.trapsonly:
        print ("Parsing JSON files for MIB Notifications ONLY and generating file %s" % args.outputfile)
        with open(args.outputfile, 'w') as csvFile:
            writer = csv.writer(csvFile)

            # Write header first
            # CSV Header
            header = ['MIBFILE', 'NAME', 'OID', 'DESCRIPTION']
            writer.writerow(header)

            for x in JSONFILELIST:
                FILENAME=x.split('.')[0]
                CWD = os.getcwd()
                with open(str(x)) as fh:
                    data = json.load(fh)
                for mibkey in data.keys():
                    if 'class' in data[mibkey]:
                        # Do I need notificationgroup also?
                        if data[mibkey]['class'] == 'notificationtype':
                            row = []
                            row.append(FILENAME)
                            row.append(data[mibkey]['name'])
                            row.append(data[mibkey]['oid'])
                            if 'description' in data[mibkey]:
                                row.append(data[mibkey]['description'])
                            else:
                                row.append('N/A')
                            writer.writerow(row)
        csvFile.close()

    else:
        # Get everything
        print ("Parsing JSON files for all OIDs and generating file %s" % args.outputfile)

        with open(args.outputfile, 'w') as csvFile:
            writer = csv.writer(csvFile)
            #
            # Write header first
            # CSV Header
            header = ['MIBFILE', 'NAME', 'OID', 'TYPE', 'DESCRIPTION']
            writer.writerow(header)

            for x in JSONFILELIST:
                FILENAME=x.split('.')[0]
                CWD = os.getcwd()
                with open(str(x)) as fh:
                    data = json.load(fh)
                for mibkey in data.keys():
                    # Let's skip the import MIB info.
                    if mibkey != 'import':
                        # We only care about elements that have an OID.
                        if 'oid' in data[mibkey]:
                            row = []
                            row.append(FILENAME)
                            row.append(data[mibkey]['name'])
                            row.append(data[mibkey]['oid'])
                            if 'syntax' in data[mibkey]:
                                row.append(data[mibkey]['syntax']['type'])
                            else:
                                row.append('N/A')
                            if 'description' in data[mibkey]:
                                row.append(data[mibkey]['description'])
                            else:
                                row.append('N/A')
                            writer.writerow(row)
        csvFile.close()

def main():
    #
    args = build_arg_parser()

    # Get Arista MIBs
    getArista()

    # If 'all' then get IETF and IEEE MIBS
    if args.allmibs:
        getOthers()

    # Parse MIBs and generate JSON output
    genJSON()

    # Generate parse JSON files and generate CSV report file
    genJSONReport(args)

    print ("Complete!\n\r")

if __name__ == "__main__":
    main()
