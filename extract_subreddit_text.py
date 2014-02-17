import progressbar
import time
import os
import psycopg2
import psycopg2.extras

class psql:
    def __init__(self):
        #
        self.db = []
        
    def connect(self):
        conn_string = ""
	print "Connecting to database\n	->%s" % (conn_string)
	self.conn = psycopg2.connect(conn_string)
	self.cursor = self.conn.cursor()


#grab the list of subreddits
subreddits = [line.strip() for line in open('subreddits','r')]

#progress bar, just because
pgbar = progressbar.ProgressBar(widgets=['Processed: ', progressbar.Counter(), ' lines | (',progressbar.Percentage(),') | ', progressbar.Timer(), ' | ',  progressbar.ETA()])

db = psql()
db.connect()

for subreddit in pgbar(subreddits):

    short_dir = 'texts/' + subreddit[:2].lower()
    try:
        os.mkdir(short_dir)
    except:
        pass

    sql = "select ups-downs, translate(title,E'\t\n','') from submissions where subreddit='"+subreddit+"'"
    db.cursor.execute(sql)

    try:
        with open(short_dir+'/'+subreddit,'w') as f:
            for record in db.cursor.fetchall():
                f.write( str(record[0])+'\t'+record[1]+'\n' )
    except:
        continue
