"""
+++ update_timestamp.py +++
WHAT'S NEW :
- 

THIS MODULE :
- this module loads the timestamp file and the purged dashboard
so to update the blog's timestamp index with yesterday's posts. 

(!) NOTES :
-
"""

import os, sqlite3, tumblr_sqlite

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main():
	print "- updating timestamps :"
	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	r = c.execute("SELECT blog_name, timestamp FROM tumblr_model")
	timestamps = {key : value for (key, value) in r}
	
	r = c.execute("SELECT blog_name, timestamp FROM dashboard")
	all_blog_name = [key[0] for key in r]
	for key in r:
		blog_name, timestamp = key[0], key[1]
		if blog_name in timestamps:
			if timestamp > timestamps[blog_name]: timestamps[blog_name] = timestamp
			else: pass
		else: timestamps[blog_name] = timestamp
	
	# update table
	for blog in timestamps:
		try:
			c.execute("INSERT INTO tumblr_model (blog_name) VALUES (?)", [blog])
		except: pass
	for blog in timestamps:
		c.execute("UPDATE tumblr_model SET timestamp=? WHERE blog_name=?", [timestamps[blog], blog])
		
	for blog in all_blog_name:
		c.execute("UPDATE tumblr_model SET following=? WHERE blog_name=?", ['1', blog])
	
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
    
	print '    ok'
	print ''

if __name__ == '__main__': main()

