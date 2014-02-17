#!/usr/bin/env python

import urllib2
import json
import time
import psycopg2
import psycopg2.extras
import httplib
import sys

class psql:
    def __init__(self):
        #
        self.db = []
        
    def connect(self):
        conn_string = ''
	print "Connecting to database\n	->%s" % (conn_string)
	self.conn = psycopg2.connect(conn_string)
	self.cursor = self.conn.cursor()


def grab(url):
    while True:
        try:
            print 'grabbing ' + url
            req = urllib2.Request(url)
            req.add_header('User-Agent','crawl bot v0.1')    
            response = urllib2.urlopen(req)
            the_page = response.read()
            
            d = json.loads(the_page)
        except (ValueError):
            print "ValueError"
            time.sleep(10)
            continue
        except (urllib2.HTTPError, urllib2.URLError):            
            return None
        except httplib.IncompleteRead:
            print "incomplete read"
            return None
        break

    return d.get("data")

get_url = 'http://www.reddit.com/r/all/new/.json?sort=new&limit=100&after=t3_'

def main():

    db = psql()
    db.connect()

    g_after = '1vj6ey'

    while True:
        try:
            data = grab(get_url + g_after)
            children = data.get("children")
            for item in children:
                listing = item.get("data")

                id        = listing.get("id")
                subreddit = listing.get("subreddit")
                title     = listing.get("title")
                author    = listing.get("author")
                created   = listing.get("created")
                url       = listing.get("url")
                domain    = listing.get("domain")
                permalink = listing.get("permalink")
                ups       = listing.get("ups")
                downs     = listing.get("downs")
                comments  = listing.get("num_comments")
                scraped   = time.time()
                
                insert_data = (id,subreddit,title,author,created,url,domain,permalink,ups,downs,comments,scraped)

                print insert_data
            
                try:
                    db.cursor.execute("INSERT INTO posts VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", insert_data)
                except psycopg2.IntegrityError:
                    print "Integrity Error!"
                    db.conn.commit()

            db.conn.commit()

            next = data.get("after")
            if next == None:
                break
            g_after = next[3:]
            print g_after

            #bail if reached already committed threads
            if base36decode(g_after) <= int('1v6761', 36):
                break

        #pause and continue
            time.sleep(2)
            
        except AttributeError:
            after_int = base36decode(g_after)
            g_after   = base36encode(after_int-50).lower()
            time.sleep(2)
            continue

#http://en.wikipedia.org/wiki/Base_36#Python_implementation
def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    base36 = ''
    sign = ''
 
    if number < 0:
        sign = '-'
        number = -number
 
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36
 
def base36decode(number):
    return int(number, 36)

if __name__ == "__main__":
    main()
