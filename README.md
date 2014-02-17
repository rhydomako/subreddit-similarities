Summary of an analysis to determine similar subreddits
==================================

This README outlines two approaches for determining the top 50 similar subreddits for a given 
input subreddit. All of the scripts used in this analysis are outlined in the steps below.

The final results can be see for the two methods: 

[The subreddit-similarity is the overlap in the set of users posting to that subreddit](http://rhydomako.ca/by_users/)

or 

[The subreddit-similarity is the cosine distance between the topic-vectors found by Latent Semantic Indexing of the posting texts](http://rhydomako.ca/by_title/)

Preamble - Scrape Reddit posts into Postgres database
------

The Python script `crawl_reddit.py` is used to access the Reddit API and store the posting information into a 
Postgres database with the following schema:

```
CREATE TABLE posts (
    id        TEXT       NOT NULL PRIMARY KEY,
    subreddit TEXT,
    title     TEXT,
    author    TEXT,
    created   TIMESTAMP,
    url       TEXT,
    domain    TEXT,
    permalink TEXT,
    ups       INTEGER,
    downs     INTEGER,
    comments  INTEGER,
    scraped   TIMESTAMP
);
```

When using a single client and following the Reddit TOS, which limits a client
to one API request ever 2 seconds, this script can take several weeks.

Step 1 - Find all of the Users that post to each subreddit
-------

We can then dump all `(user, subreddit)` tuples to a CSV file -- easily done using the `psql` commandline tool:

`$ psql -A -F, -t -c 'select author, subreddit from posts;' > user_subreddit_tuples.csv`

Using Apache Pig and the Pig Latin script `group_by_subreddit.pig`, the tuples are 
regrouped according to subreddit, with any duplicate user removed. The output of the 
Pig script is in the form: `subreddit {(user1),(user2),(user3),...,(userN)}`, which can be 
converted back to CSV format via:

`$ sed -e 's/\t{(/,/' -e 's/)}//' <pig-output-file> | tr -d \( | tr -d \) > subreddit_lists.csv`

which leaves `subreddit_lists.csv` in the form: `subreddit,user1,user2,user3,...,userN`

However, we are going to be using the `SparseVector` class in Apache Mahout, which only supports
integer row-names, so we have to convert all of the subreddit names to integer indices. At the same
time, we can convert the user-names into a sparse vector format by assigning each user a unique number,
which represents its vector index. The python script `convert_lists_to_vectors.py` scripts will do this job:

`$ python convert_lists_to_vectors.py subreddit_lists.csv > subreddit_vectors.csv`

Step 2 - User Apache Mahout to find the vector similarities
--------

(I wrote a module that that took as the `CSV` file as input and created a `SequenceFile` containing 
Mahout `SparseVector` objects, but I can't seem to find that code.)

Anyway, the Mahout `rowsimilarity` utility works nicely to find the similary between all of the 
rows of the csv file, and therefore all of the subreddit vectors:

`bin/mahout rowsimilarity -i mahout-vectors/part-m-00000 -o sim -s SIMILARITY_TANIMOTO_COEFFICIENT --tempDir /tmp/ -ow -m 10000 -ess true`

Here, the [Tanimoto similarity](http://en.wikipedia.org/wiki/Jaccard_index#Tanimoto_Similarity_and_Distance), which is 
similar to the Jaccard similarity, is used to find the overlap between the sets of users in each subreddit. The resulting
vectors can be dumped to file using the `vectordump` utility:

`bin/mahout vectordump -i sim -o sim-rows -p true --tempDir /tmp`

Each row of the output file is of the form: `subreddit_id<tab>{subreddit_id_1:similarity_coefficient,subreddit_id_2:similarity_coefficient,....}` where the similar subreddits are sorted in order of decreasing similarity.

This output can be reorganized back into CSV format using:

`sed -e 's/\t{/,/' <row_similarity_output> | tr -d } > similarity_matrix.csv`

Step 3 - Insert results into a MySQL database
-------

My web hosting provider only really provides MySQL support, so the analysis results are 
put dumped into a SQL table (with schema definition in `sim_table.sql`). This database is
intentially denormalized for the purposes of presenting these results. For each row in 
`similarity_matrix.csv`, the script `insert_mysql_flat.py` is used to convert the subreddit ids
back to proper names, and insert the top 50 similarity matches into the database.

[Finally, I put together a simple AngularJS frontend to display the results and allow for searching.](http://rhydomako.ca/by_users/)

Step 4 - Tackle the same problem using an NLP approach
-------

The [gensim](http://radimrehurek.com/gensim/) Python library provides topic modeling tools
that can be applied to this same dataset to use a [Latent Semantic Indexing](http://en.wikipedia.org/wiki/Latent_semantic_indexing)
model to find topic-vectors for each subreddit, then find the Cosine similarity between all 
of those topic-vectors.

First, a list of subreddits is generated:

`psql -t -A -c 'select distinct subreddit from posts' > subreddits`

And then the script `extract_subreddit_text.py` is used to extract the text of all of the postings and 
create individual files containing all of the posting text for that subreddit. A dictionary of all of the
words used in all of the posting is then created using the `make_dictionary.py` script. Finally, the 
`make_topics_db.py` script is used to create the topic model and similarity matrix, find the 50 top similiar 
subreddits for each subreddit, and dump those results into a MySQL table.

[Just like above, an AngularJS frontend was created to allow for searching of the results.](http://rhydomako.ca/by_title/)
