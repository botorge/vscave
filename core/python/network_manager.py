"""
+++ network_manager.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, tumblr_api, time

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

threshold = 7884000 # three months in seconds

def update_following():
	"""(!) to run sporadically"""
	print "- updating following :"
	
	following = {}
	off = 0
	for unused in range(250):
		# TUMBLR API REQUEST FOLLOWING BLOGS
		this_following = tumblr_api.get_following(path, offset=off)
		for blog in this_following['blogs']:
			name = blog['name']
			updated = blog['updated']
			following[name] = updated
		off += 20
		time.sleep(5)
	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	c.execute("UPDATE tumblr_model SET following=NULL") # everything to null first
	for blog in following:
		try:
			c.execute("INSERT INTO tumblr_model (blog_name) VALUES (?)", [blog])
		except: pass	
	for blog in following:
		c.execute("UPDATE tumblr_model SET following=?, timestamp=? WHERE blog_name=?", ['1', following[blog], blog])
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
    
	print '    ok'

def unfollow_blogs():
	print "- unfollowing inactive blogs :"
	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT blog_name, timestamp FROM tumblr_model WHERE following='1'")
	timestamps = {key : value for (key, value) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	#print '    %s following blogs'%len(timestamps) # (!) this count differs from tumblr api's count

	to_unfollow = []
	now = int(time.time())
	for blog in timestamps:
		try: updated = int(timestamps[blog])
		except:
			# TUMBLR API REQUEST
			blog_info = tumblr_api.blog_info(path, blog)
			try: updated = blog_info['blog']['updated']
			except: updated = 0
			# DB-CONNECT
			conn = sqlite3.connect(db_path)
			c = conn.cursor()
			# DB-EXECUTE
			c.execute("UPDATE tumblr_model SET timestamp=? WHERE blog_name=?", [updated, blog])
			# DB-COMMIT AND CLOSE
			conn.commit()
			conn.close()
		if (now-updated) < threshold: pass
		else: to_unfollow.append(blog)
	print '    %s inactive blogs'%len(to_unfollow)
	
	# unfollow tumblr api and sqlite
	for blog in to_unfollow:
		# TUMBLR API UNFOLLOW
		unfollow = tumblr_api.unfollow(path, blog)
		if unfollow == {u'meta': {u'status': 404, u'msg': u'Not Found'}, u'response': []} or unfollow['blog']['followed'] == False:
			# DB-CONNECT
			conn = sqlite3.connect(db_path)
			c = conn.cursor()
			# DB-EXECUTE
			c.execute("UPDATE tumblr_model SET following=? WHERE blog_name=?", ['0', blog])
			# DB-COMMIT AND CLOSE
			conn.commit()
			conn.close()
			time.sleep(5)

def follow_blogs():
	print "- following new blogs :"
	
	following_api = tumblr_api.get_following(path)
	to_follow = 5000 - following_api['total_blogs']
	print '    %s blogs to reach the 5k follow limit'%to_follow
	
	if to_follow > 0:
		# DB-CONNECT
		conn = sqlite3.connect(db_path)
		c = conn.cursor()
		# DB-EXECUTE
		r = c.execute("SELECT blog_name, network_dist, timestamp FROM tumblr_model WHERE following IS NULL OR following='0'")
		non_following = {key : [value1, value2] for (key, value1, value2) in r}
		# DB-COMMIT AND CLOSE
		conn.commit()
		conn.close()
	
		# get rid of the inactive blogs, .coms, and 'I'
		now = int(time.time())
		non_foll = {}
		for blog in non_following:
			if blog == 'I': pass
			elif '.' in blog: pass
			else:
				try: updated = int(non_following[blog][1])
				except: updated = now-1
				if (now-updated) < threshold: non_foll[blog] = non_following[blog]
				else: pass

		# sort unique distances
		unique = []
		for blog in non_foll:
			dist = non_foll[blog][0]
			if dist not in unique: unique.append(dist)
		unique = sorted(unique, reverse=False) # (!) True starts from the farthest
		try:
			if unique[0] == None: del unique[0]; unique.append(None)
		except: print '    %s'%unique

		to_follow_list = []
		for u in unique:
			for blog in non_foll:
				dist = non_foll[blog][0]
				if dist == u: to_follow_list.append(blog)
		print '    %s blogs in the pool to follow'%len(to_follow_list)
		
		count = follow(to_follow_list, to_follow)
		print '    %s new blogs following'%count

def follow(blog_list, to_follow, count=0):
	count, count_404 = 0, 0
	for blog in blog_list:
		if count < 200 and count < to_follow:
			# TUMBLR API REQUEST
			blog_info = tumblr_api.blog_info(path, blog)
			if blog_info == {u'meta': {u'status': 404, u'msg': u'Not Found'}, u'response': []}: count_404 += 1
			else:
				follow = tumblr_api.follow(path, blog)
				if follow == {'meta': {'status': 500, 'msg': 'Server Error'}, 'response': {'error': 'Malformed JSON or HTML was returned.'}}:
					print '    500 status on %s'%blog
					print '    %s new blogs followed so far'%count
					print '    ...sleeping for an hour'
					time.sleep(3600)
				else:
					if follow['blog']['followed'] == True:
						updated = follow['blog']['updated']
						# DB-CONNECT
						conn = sqlite3.connect(db_path)
						c = conn.cursor()
						# DB-EXECUTE
						c.execute("UPDATE tumblr_model SET following=?, timestamp=? WHERE blog_name=?", ['1', updated, blog])
						# DB-COMMIT AND CLOSE
						conn.commit()
						conn.close()
						count += 1
						time.sleep(5)
	return count

def main(): # <----- (!) MAIN PROCEDURE
	#update_following() # to be run once in a lifetime
	unfollow_blogs()
	follow_blogs()

if __name__ == '__main__': main()

