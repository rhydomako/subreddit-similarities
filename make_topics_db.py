#!/usr/bin/python

import sys
import MySQLdb
import operator
from gensim import models, corpora, similarities
import progressbar

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary().load('dictionary_nochars.dict')
mm = corpora.MmCorpus('doc_matrix.mm')
lsi = models.LsiModel(id2word=dictionary, num_topics=268).load('lsi.model')
index = similarities.MatrixSimilarity(corpus=None, num_features=500).load('lsi.index')

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="web", # your username
                     passwd="", # your password
                     db="db1") # name of the data base

cur = db.cursor() 

stoid = {}
idtos = {}
id = 0
for subreddit in open('subreddits','r'):
    stoid[subreddit.strip()] = id
    idtos[id] = subreddit.strip()
    id += 1


pgbar = progressbar.ProgressBar(widgets=['Processed: ', progressbar.Counter(), ' lines | (',progressbar.Percentage(),') | ', progressbar.Timer(), ' | ',  progressbar.ETA()])

for subreddit in pgbar( stoid.keys() ):

    sims_array = index[lsi[mm[stoid[subreddit]]]]
    in_order   = sims_array.argsort()[::-1]

    subs = ()
    sims = ()
    cnt = 0
    for in_order_idx in in_order:
        if idtos[in_order_idx] == subreddit: continue
        subs = subs + (idtos[in_order_idx],)
        sims = sims + (str(sims_array[in_order_idx]),)
              
        cnt += 1
        if cnt >= 50:
            break

    record = (subreddit,) + subs + sims

    cur.execute(
            """INSERT INTO db1.similar_submissions VALUES (%s,
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

