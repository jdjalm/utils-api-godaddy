"""
Author: Juan Almanza
Date: 2/1/2024
Version 0.1
Purpose: Faciliate retrieving domain data from GoDaddy via API.
Details: Requires reference to a file containing API key data. Will retrieve live/active domains and all records for each of those domains. The resulting record sets are saved as a CSV.

Notes: Currently does not support pagination on API responses.

"""

#Import libraries
import datetime
import json
import requests
import time
import argparse
import pandas
import os
from pathlib import Path
from math import ceil as mceil

#Script execution begins
print("==============================")
print("Start script [" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "]...\n")

#Verbose output print method
def printv(msg):
    if args["verbose"]:
        print(str(msg))

def cexit():
    print("\nExiting script [" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "]...")
    print("==============================")
    quit()

#Parse arguments
parser = argparse.ArgumentParser(description = "This script is a work in progress. It is meant to faciliate retrieving domain data from GoDaddy via API.", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-k", "--keypath", help = "Absolute or relative directory path where the file containing API key data is located. If omitted, the current working directory is searched.")
parser.add_argument("-s", "--storepath", help = "Absolute or relative directory path where API responses will be saved. If omitted, the current working directory is used.")
parser.add_argument("-v", "--verbose", action = "store_true", help = "Increase script verbosity. Default is false.")
args = vars(parser.parse_args())

#Verify path where API responses will be saved
if args["storepath"]:
    if Path(args["storepath"]).is_dir() and not Path(args["storepath"]).is_file():
        path_save = args["storepath"]
    else:
        print("\nERROR: Search path argument is not a directory or insufficient permissions!\n")
        exit()
else:
    if Path(os.getcwd()).is_dir():
        path_save = os.getcwd()
    else:
        print("\nERROR: No search path argument provided and writing to current working directory is not permitted!\n")
        cexit()

#Verify path where API key data stored
if args["keypath"]:
    if Path(args["keypath"]).is_file():
        path_keys = os.path.abspath(args["keypath"])
    else:
        if Path(os.getcwd() + args["keypath"]).is_file():
            path_keys = os.getcwd() + args["keypath"]
        else:
            print("\nERROR: API key file path argument is not a file or insufficient permissions!\n")
            cexit()
else:
    print("\nERROR: Mandatory argument for API key file path was not provided.\n")
    cexit()

#Read and verify API key data. Max number of lines read is 10. Lines beginning with symbol # are treated as comments.
keydata = ""
print("Attempting to ingest API key data from file: " + str(path_keys))
with open(path_keys, 'r') as k:
    for l, line in enumerate(k):
        if l < 10:
            if line[:1] == "#":
                continue
            else:
                keydata = str(line).rstrip('\n')
                break
if keydata == "":
    print("ERROR: Maximum number of non-comment lines (10) read from API key file but failed to find a valid data. Verify file contents and try again.")
    cexit()

#API usage variables
api_url_base = "https://api.godaddy.com/"
api_headers = {
    "accept":"application/json",
    "Authorization":"sso-key " + str(keydata)
}

#Get all domains for account
print("Retrieving all domains with an 'ACTIVE' status...")
rd = requests.get("https://api.godaddy.com/v1/domains?statuses=ACTIVE", headers=api_headers)
if rd.ok:
    domain_list = json.loads(str(rd.text))
    print("Successfully retrieved [" + str(len(domain_list)) + "] domains...")
    if args["verbose"]:
        for domain in domain_list:
            print("\t" + domain["domain"])
else:
    print("ERROR: API call failed with the following response: " + str(rd))
    cexit()

#Get all records for each domain
print("Retrieving all records for domain list. It will take at least " + str(mceil(len(domain_list) * 1.1)) + " seconds due to API rate-limiting...")
domain_found = []
domain_records = []
for domain in domain_list:
    time.sleep(1.1)
    t_combined_url = api_url_base + "v1/domains/" + domain["domain"] + "/records/"
    rr = requests.get(t_combined_url, headers=api_headers)
    if rr.ok:
        domain_found.append(domain["domain"])
        domain_records.append(rr)
        if args["verbose"]:
            print("Successfully retrieved records for [" + domain["domain"] + "]")
        else:
            print(".", end=" ")
    else:
        if args["verbose"]:
            print("\tERROR: API call failed for [" + domain["domain"] + "] with the following response: " + str(rr))
        else:
            print("x", end=" ")
if not args["verbose"]: print("\n")
print("Captured [" + str(len(domain_found)) + "] succesful responses out of [" + str(len(domain_list)) + "] queries...")

#Save responses
print("Saving responses to: " + path_save)
for d, dom in enumerate(domain_records):
    records = json.loads(str(dom.text))
    df = pandas.json_normalize(records)
    sp = os.path.join(path_save, str(domain_found[d]) + "_records_" + datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S") + ".csv")
    df.to_csv(sp)
    printv("Processed response for: " + str(domain_found[d]) + " - " + str(sp))
    printv(json.dumps(records, sort_keys=True, indent=4))
print("Done.")

#Exit notify
cexit()
