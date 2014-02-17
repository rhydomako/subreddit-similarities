#!/usr/bin/python

import sys
import csv
import json
import time

#csvfile from commandline argument
csvfile = sys.argv[1]

#initialize the dictionaries
user_n           = {}
subreddit_n      = {}
user_subreddit_n = {}
user_num            = 0
subreddit_num       = 0

with open(csvfile,'r') as f:
    csv_reader = csv.reader(f)

    for linenum,line in enumerate(csv_reader):

        user      = line[0]
        subreddit = line[1]

        #disregard deleted threads, and default subreddits
        if user == '[deleted]':
            continue

        #update the user numbering
        try:
            unum = user_n[user]
        except:
            user_n[user] = user_num
            unum            = user_num
            user_num       += 1

        #update subreddit numbering
        try:
            snum = subreddit_n[subreddit]
        except:
            subreddit_n[subreddit] = subreddit_num
            snum                      = subreddit_num
            subreddit_num            += 1

        #append the subreddit hash
        try:
            if unum in user_subreddit_n[snum]:
                continue
            else:
                user_subreddit_n[snum].append(unum)
        except:
            user_subreddit_n[snum] = []
            user_subreddit_n[snum].append(unum)

#json files for the subreddit/
json.dump(subreddit_n, open("subreddit_nums.json",'w'))
json.dump(user_n,      open("user_nums.json",'w'))

#csv file
for key in user_subreddit_n.keys():
    print str(key) + ',' + ','.join(str(x) for x in user_subreddit_n[key])
