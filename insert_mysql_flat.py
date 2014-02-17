#!/usr/bin/python

import sys
import csv
import json
import MySQLdb
import operator

subreddit_hash    = json.load(open('data/subreddit_hash.json'))
subreddit_invhash = {v:k for k,v in subreddit_hash.iteritems() }
size_hash         = json.load(open('data/size_hash.json'))

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="web", # your username
                     passwd="", # your password
                     db="db1") # name of the data base

cur = db.cursor() 

with open('data/similarity_matrix.csv','r') as f:
    csv_reader = csv.reader(f)
    for linenum,line in enumerate(csv_reader):
        
        main_subreddit = subreddit_invhash[int(line[0])]
        sim_subreddits = line[1:]
        if sim_subreddits[0]=='':
            continue

        records = []
        for subreddits in sim_subreddits:
            s = subreddits.split(':')
            subreddit  = subreddit_invhash[int(s[0])]
            similarity = float(s[1])

            records.append( (subreddit,similarity,size_hash[subreddit]) )
        records = sorted(records,key=operator.itemgetter(1),reverse=True)[0:50]
        n_to_add = 50-len(records)
        for i in range(n_to_add):
            records.append( (None, None, None) )

        records = zip(*records)
        record  = (main_subreddit,) + records[0] + records[1] + records[2]

        cur.execute(
            """INSERT INTO db1.similar_subreddits VALUES (%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,

%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,

%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            record)
        db.commit()
