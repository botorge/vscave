"""
+++ db_manager.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

from datetime import date, timedelta
import os, tumblr_sqlite, sqlite3

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def create_tumblr_dashboard():
	""" this procedure is called from outside this module """
	db_path = path+'tumblr_api.db'
	name = 'tumblr_dashboard'
	cols = {'blog_name': 'TEXT', 'id': 'INT', 'post_url': 'TEXT', 'type': 'TEXT', 'timestamp': 'INT',
		'date': 'TEXT', 'format': 'TEXT', 'reblog_key': 'TEXT', 'tags': 'TEXT', 'bookmarklet': 'TEXT',
		'mobile': 'TEXT', 'source_url': 'TEXT', 'source_title': 'TEXT', 'liked': 'TEXT', 'state': 'TEXT',
		'caption': 'TEXT', 'short_url': 'TEXT', 'note_count': 'INT', 'photos': 'TEXT', 'date_short': 'TEXT'}
	tumblr_sqlite.create_table(db_path, name, cols)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

def create_dashboard():
	print "    vscave/dashboard"
	name = 'dashboard'
	cols = {'reblog_key': 'TEXT', 'caption': 'TEXT', 'short_url': 'TEXT', 'blog_name': 'TEXT',
		'type': 'TEXT', 'note_count': 'INT', 'photos': 'TEXT', 'tags': 'TEXT', 'source_title': 'TEXT',
		'timestamp': 'INT'}
	#prim = ['reblog_key']
	prim = []
	tumblr_sqlite.create_table_scratch(db_path, name, cols, prim)

def create_tumblr_model():
	print "    vscave/tumbr_model"
	name = 'tumblr_model'
	cols = {'blog_name': 'TEXT', 'timestamp': 'INT', 'pagerank': 'REAL', 'network_dist': 'REAL',
		'notes_min': 'INT', 'notes_max': 'INT', 'notes_timestamp': 'INT', 'following': 'INT'}
	prim = ['blog_name']
	tumblr_sqlite.create_table(db_path, name, cols, prim)

def create_graph():
	print "    vscave/tumbr_graph"
	name = 'graph'
	cols = {'blog_name': 'TEXT', 'source_title': 'BLOB'}
	prim = ['blog_name']
	tumblr_sqlite.create_table(db_path, name, cols, prim)

def create_subgraph():
	print "    vscave/tumbr_subgraph"
	name = 'subgraph'
	cols = {'blog_name': 'TEXT', 'source_title': 'BLOB'}
	prim = ['blog_name']
	tumblr_sqlite.create_table_scratch(db_path, name, cols, prim)

def create_lsi_dashboard(): # the name of this tables is misleading
	print "    vscave/lsi_dashboard"
	name = 'lsi_dashboard'
	cols = {'reblog_key': 'TEXT', 'post_model': 'BLOB', 'cluster': 'INT', 'network_model': 'BLOB',
		'spectrum':'REAL', 'blog_name': 'TEXT'}
	prim = ['reblog_key']
	tumblr_sqlite.create_table_scratch(db_path, name, cols, prim)

def create_tables():
	print "- creating tables :"
	
	# permanent tables
	create_tumblr_model()
	create_graph()
	
	# temporary tables
	create_subgraph()
	create_dashboard()
	create_lsi_dashboard()
	
	print "    ok"
	print ""

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

def clean_tables():
	print "- purging database :"
	
	good_days = [d for d in get_days()[:2]]
	db_days = get_dates()
	delete_rows(good_days, db_days)
	
	print "    ok"
	print ""

def get_days():
	today = date.today()
	yesterday = today - timedelta(1)
	before_yesterday = yesterday - timedelta(1)
	return str(today), str(yesterday)

def get_dates():
	db_path = path+'tumblr_api.db'
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT DISTINCT date_short FROM tumblr_dashboard")
	distincts = [key[0] for key in r]
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return distincts

def delete_rows(good_days, db_days):
	db_path = path+'tumblr_api.db'
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for day in db_days:
		if day not in good_days:
			r = c.execute("DELETE FROM tumblr_dashboard WHERE date_short='%s'"%day)
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

def main(): # <----- (!) MAIN PROCEDURE
	clean_tables()
	create_tables()

if __name__ == '__main__': main()

