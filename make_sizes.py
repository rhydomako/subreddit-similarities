#!/usr/bin/python

import sys
import csv
import json

#csvfile from commandline argument
csvfile = 'data/vectors_named.csv'

#initialize the dictionaries
size_hash           = {}
user_subreddit_hash = {}
user_num            = 0

with open(csvfile,'r') as f:
    csv_reader = csv.reader(f)

    for linenum,line in enumerate(csv_reader):

        subreddit = line[0]
        users     = line[1:]

        size = len( set(users) )
        size_hash[subreddit] = size

#json files for the subreddit/
json.dump(size_hash, open("data/size_hash.json",'w'))
