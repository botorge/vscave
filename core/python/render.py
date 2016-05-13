"""
+++ render.py +++
WHAT'S NEW :
-

THIS MODULE :
-

(!) NOTES :
-
"""

from datetime import date, timedelta
import json, os, random, sqlite3, ast

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def get_days():
    today = date.today()
    yesterday = today - timedelta(1)
    before_yesterday = yesterday - timedelta(1)
    return str(today), str(yesterday), str(before_yesterday)

def main(): # (!) <--- MAIN PROCEDURE
	print '- building rendering file :'

	today, yesterday, before_yesterday = get_days()
	maxPosts = 36
	index = {'daily_images':[]} # <--- MAIN VARIABLE

	# loading likes
	myLikes = get_likes()

	# loading characters
	try:
		with open('/home/jorgeo/Desktop/VsCave/src/cien_anios_personajes.json', 'r') as data_file: f = json.load(data_file)
		characters = f['characters']
	except: print 'error loading the .json file'

	# loading clusters
	clusters = get_clusters()
	
	for cluster in clusters:
		cover, cluster_index, new_cluster = [], [], []
		blogs_int = []
		cover_int, cover_str = [], str()
		posts = get_posts(clusters[cluster])
		
		# get indexes from cluster to render
		for i in range(len(posts)):
			post = posts[i]
			if post['blog_name'] in myLikes: cluster_index.append(i)
		
		if cluster_index:
			# getting indexes
			if len(posts) < maxPosts: new_cluster = range(len(posts))
			elif len(cluster_index) >= maxPosts: new_cluster = cluster_index[:maxPosts]
			else:
				get_neighbors(cluster_index, len(posts), maxPosts, new_cluster)
				new_cluster = sorted(new_cluster[:maxPosts])

			# building file
			for i in new_cluster:
				try: # to catch bug at get_neighbors()
					post = posts[i]
					cover.append(post) # variable to pass on to the html
				except: pass

			# statistics
			for i in new_cluster:
				try: # to catch bug at get_neighbors()
					post = posts[i]
					if post['blog_name'] not in blogs_int: blogs_int.append(post['blog_name'])
					if post['blog_name'] in myLikes:
						if post['blog_name'] not in cover_int:
							cover_int.append(post['blog_name'])
							cover_str = cover_str + ', ' + post['blog_name']
				except: pass
			cover_str = cover_str[2:]
				
			# modify the main variable
			try:
				name = random.choice(characters)
				characters.remove(name)
			except: name = 'other characters'
			dic = {'name':name.upper(), 'cluster':cover, 'num_blogs':len(blogs_int), 'blogs':cover_str, 'posts':len(posts)}
			index['daily_images'].append(dic)

	# saving file for render in browser
	try:
		with open('/home/jorgeo/Desktop/VsCave_render/%s.json'%yesterday, 'w') as f: json.dump(index, f)
	except: print 'error saving the .json file'

	print '    %s clusters to render'%len(index['daily_images'])
	print ''

def get_posts(cluster):
	posts = []
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for reblog_key in cluster: # (!) VERY SLOW
		r = c.execute("SELECT reblog_key, blog_name, photos, short_url, caption FROM dashboard WHERE reblog_key=?", [reblog_key])
		thisR = [{'reblog_key':reblog_key, 'blog_name':blog_name, 'url': ast.literal_eval(photos)[0]['original_size']['url'], 'short_url':short_url, 'caption':caption} for (reblog_key, blog_name, photos, short_url, caption) in r]
		posts.append(thisR[0])
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()	
	return posts

def get_clusters():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT DISTINCT cluster FROM lsi_dashboard")
	clusters = {key[0]:[] for key in r}
	for cluster in clusters:
		r = c.execute("SELECT reblog_key FROM lsi_dashboard WHERE cluster=?", [cluster])
		clusters[cluster] = [key[0] for key in r]
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return clusters

def get_neighbors(cluster_index, lenPosts, maxPosts, new_cluster, neigh=1):
	if len(new_cluster) >= maxPosts: return            
	else:
		for c in cluster_index:
			if c not in new_cluster: new_cluster.append(c)
		for c in cluster_index:
			a, b = c-neigh, c+neigh
			if a not in new_cluster:
				if a >= 0: new_cluster.append(a)
			if b not in new_cluster:
				if b < lenPosts: new_cluster.append(b)
		neigh+=1
		get_neighbors(cluster_index, lenPosts, maxPosts, new_cluster, neigh)

def get_likes():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	r = c.execute("SELECT blog_name FROM likes")
	liked = [value[0] for value in r]

	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

	countLikes = []
	for blog_name in liked:
		if blog_name not in countLikes:
			c = liked.count(blog_name)
			if c > 1: countLikes.append(blog_name)
	print '    %s blogs to track'%len(countLikes)
	return countLikes

def get_blogs_names(posts, max_posts=100):
    blogs = []
    blogs_s = str()
    for post in posts:
        if post['blog_name'] in blogs: pass
        else:
            blogs.append(post['blog_name'])
            if len(blogs)<max_posts: blogs_s = blogs_s + ', ' + post['blog_name']
    blogs_s = blogs_s[2:] # remove first coma
    return len(blogs), blogs_s

if __name__ == '__main__': main()

