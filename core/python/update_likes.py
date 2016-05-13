"""
+++ update_likes.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, pytumblr, tumblr_sqlite, tumblr_api
from datetime import date, timedelta

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'
client = tumblr_api.auth(path)

def get_days():
    today = date.today()
    yesterday = today - timedelta(1)
    before_yesterday = yesterday - timedelta(1)
    return str(today), str(yesterday), str(before_yesterday)

def request_likes():
	maxLikes = 500
	likes = client.likes()
	thisOffset = 20
	for unused in range(likes['liked_count']/20):
		if len(likes['liked_posts']) < maxLikes:
			req = client.likes(offset=thisOffset)
			for post in req['liked_posts']:
				if post in likes['liked_posts']: pass
				else: likes['liked_posts'].append(post)
			thisOffset = thisOffset+20
	return likes

def build_text(post, all_cols):
    cols, vals = [], []
    
    # values from the posts
    for key in all_cols:
        if key in post:
            vals.append("""%s"""%post[key])
            cols.append(key)
    
    # build request text
    text = 'INSERT INTO likes (' + ','.join(cols) + ') values (' + ','.join(['?']*len(cols)) + ')'
    return text, vals

def main():
	print "- updating likes :"
	
	today, yesterday, before_yesterday = get_days()
	
	# requests tumblr likes
	likes = request_likes()
	
	# build table
	# (!) this table should be build by the db_manager 
	name = 'likes'
	cols = {'blog_name': 'TEXT', 'id': 'INT', 'post_url': 'TEXT', 'type': 'TEXT', 'timestamp': 'INT',
    'date': 'TEXT', 'format': 'TEXT', 'reblog_key': 'TEXT', 'tags': 'TEXT', 'bookmarklet': 'TEXT',
    'mobile': 'TEXT', 'source_url': 'TEXT', 'source_title': 'TEXT', 'liked': 'TEXT', 'state': 'TEXT',
    'caption': 'TEXT', 'short_url': 'TEXT', 'note_count': 'INT', 'photos': 'TEXT', 'date_short': 'TEXT'}
	tumblr_sqlite.create_table_scratch(db_path, name, cols)
	
    # connect to db
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
    
    # request dashboard
	for post in likes['liked_posts']:
		text, vals = build_text(post, cols)
		c.execute(text, vals) # <--- insert values 
    
	final_count = [key[0] for key in c.execute("SELECT count(*) from likes")][0]
    
    # commit and close db
	conn.commit()
	conn.close()
    
    # print out the changes in the index
	print "    %s total likes indexed"%final_count
	print ""

if __name__ == '__main__': main()

