"""
+++ build_dashbaord.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
- this version of the module does not leave behind the banned blogs
"""

import os, sqlite3
from datetime import date, timedelta

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def get_days():
    today = date.today()
    yesterday = today - timedelta(1)
    before_yesterday = yesterday - timedelta(1)
    return str(today), str(yesterday), str(before_yesterday)

def main():
	print "- building the dashboard :"
	
	today, yesterday, before_yesterday = get_days()
	cols = ['reblog_key', 'caption', 'short_url', 'blog_name', 'type', 'note_count', 'photos', 'tags',
		'source_title', 'timestamp']
    
	# build commands
	attach = "ATTACH ? AS db2"
	insert = "INSERT INTO dashboard (" + ", ".join(cols) + ") SELECT " + ", ".join(cols) + " FROM db2.tumblr_dashboard WHERE date_short='%s' AND type='photo'"%yesterday
	purge_count = "SELECT count(*) FROM dashboard"
	count = "SELECT count(*) FROM db2.tumblr_dashboard WHERE date_short='%s'"%yesterday
	detach = "DETACH DATABASE 'db2'"
	
	# connect to db
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# execute
	c.execute(attach, (path+'tumblr_api.db', ))
	c.execute(insert)
	purge_count = [key[0] for key in c.execute(purge_count)][0]
	count = [key[0] for key in c.execute(count)][0]
	c.execute(detach)
	
	# commit and close
	conn.commit()
	conn.close()
		
	print "    %s posts indexed from yerterday's dashboard"%count
	print "    %s photo-posts after purge"%purge_count
	print ""

if __name__ == '__main__': main()

