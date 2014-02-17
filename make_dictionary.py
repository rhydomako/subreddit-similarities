#!/usr/bin/python

from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from gensim import corpora, models, similarities
import nltk
import string
import progressbar

#grab the list of subreddits
subreddits = [line.strip() for line in open('subreddits','r')]

sw = stopwords.words('english')

#progress bar, just because
pgbar = progressbar.ProgressBar(widgets=['Processed: ', progressbar.Counter(), ' lines | (',progressbar.Percentage(),') | ', progressbar.Timer(), ' | ',  progressbar.ETA()])

dictionary = corpora.Dictionary()

for subreddit in pgbar(subreddits):

    short_dir = 'texts/' + subreddit[:2].lower() + '/'
    try:
        with open(short_dir+subreddit,'r') as f:
            lines = [line.strip() for line in f]
    except:
        continue

    corpuses = []
    for line in lines:
        s = line.split('\t')

        score  = int(s[0])
        try:
            tokens = wordpunct_tokenize(s[1])
        except:
            continue

        filtered_tokens = [word.lower() for word in tokens if word not in sw if word not in list(string.punctuation)]

        corpuses.append(filtered_tokens)

    dictionary.add_documents(corpuses)

dictionary.save("dictionary.dict")

#dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n=10000000)
#dictionary.compactify() # remove gaps in id sequence after words that were removed

