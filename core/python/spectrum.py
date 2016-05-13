"""
+++ spectrum.py +++
WHAT'S NEW :
-

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, ast, operator
from sklearn import (manifold)

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'
    
def main():
	print '- spectrum :'
	
	network_model = get_network_model()
	clusters = get_clusters(get_likes())
	for cluster in clusters:
		spectrum = build_spectrum(network_model, clusters[cluster])
		update_db(spectrum)

	print '    ok'
	print ''

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
	return countLikes

def update_db(spectrum):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for post in spectrum:
		c.execute("UPDATE lsi_dashboard SET spectrum=? WHERE reblog_key=?", [post[1], post[0]])
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

def build_spectrum(network_model, cluster):
	# build matrix
	M, M_index = [], []
	new_cluster = {}
	for reblog_key in cluster:
		thisModel = network_model[reblog_key]
		thisModel[3] = 1/thisModel[3] # inverting the network_distance value
		M.append(thisModel)
		M_index.append(reblog_key)
		
	# reduce dimensions
	numPosts = len(cluster)
	if numPosts > 5: # (!) hard number
		M_iso = manifold.Isomap(n_neighbors=5, n_components=1).fit_transform(M)
		# update the index
		i = 0
		for reblog_key in M_index:
			new_cluster[reblog_key] = round(M_iso[i][0], 4)
			i+=1
	else:
		for reblog_key in M_index: new_cluster[reblog_key] = 0.
	
	# sort
	new_cluster = sorted(new_cluster.items(), key=operator.itemgetter(1)) # the first item is the 'closest'
	return new_cluster

def get_clusters(myLikes):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	r = c.execute("SELECT blog_name, cluster FROM lsi_dashboard")
	blogs = {key: value1 for (key, value1) in r}
	
	cl = []
	for blog_name in blogs:
		if blog_name in myLikes:
			if blogs[blog_name] not in cl: cl.append(blogs[blog_name])
	unique_clusters = set(cl)
	clusters = {key:[] for key in unique_clusters}
	
	r = c.execute("SELECT reblog_key, cluster FROM lsi_dashboard")
	for (key, value1) in r:
		try: clusters[value1].append(key)
		except: pass
	
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return clusters

def get_network_model():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, network_model FROM lsi_dashboard")
	network_model = {key : ast.literal_eval(value1) for (key, value1) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return network_model

if __name__ == '__main__': main()

