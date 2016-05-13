"""
+++ main_sourcing.py +++
WHAT'S NEW :
-

THIS MODULE :
-

NOTES :
-
"""

import datetime, time, os
import sqlite3
import tumblr_api as api
import tumblr_sqlite, db_manager

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_name = 'tumblr_api.db'

def build_text(post, today, all_cols):
    cols, vals = [], []
    
    # values from the posts
    for key in all_cols:
        if key in post:
            vals.append("""%s"""%post[key])
            cols.append(key)
            
    # values outside the posts
    vals.append(today)
    cols.append('date_short')
    
    # build request text
    text = 'INSERT INTO tumblr_dashboard (' + ','.join(cols) + ') values (' + ','.join(['?']*len(cols)) + ')'
    return text, vals
    

def request(today, cols):
	# request dashboard
	dashboard = api.get_dashboard(path)
		    
    # connect to db
	conn = sqlite3.connect(path+db_name)
	c = conn.cursor()
    
    # select existing values
	keys = [key[0] for key in c.execute("SELECT reblog_key FROM tumblr_dashboard WHERE date_short=?", [today])]
	ini_count = [key[0] for key in c.execute("SELECT count(*) from tumblr_dashboard WHERE date_short=?", [today])][0]

	for post in dashboard['posts']:
		if post['reblog_key'] not in keys:
			text, vals = build_text(post, today, cols)
			c.execute(text, vals) # <--- insert values 
    
	final_count = [key[0] for key in c.execute("SELECT count(*) from tumblr_dashboard WHERE date_short=?", [today])][0]
    
    # commit and close db
	conn.commit()
	conn.close()

def main():
	print '(!) indexing dashboard'
	
	db_manager.create_tumblr_dashboard()
	cols = tumblr_sqlite.get_columns(path+db_name, 'tumblr_dashboard')
	
	while True:
		try:
			today = str(datetime.date.today())
			request(today, cols)
			time.sleep(2)
		except:
			print '...internet connection is lost, please wait'
			time.sleep(60)

if __name__ == '__main__': main()

