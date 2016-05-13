"""
+++ cluster.py +++
WHAT'S NEW :
-

THIS MODULE :
- this module loads yesterday's dashboard, the model of the tumblr, and the model of
yersterday's dashboard. it builds a matrix with all the posts from the dashboard,
characterised by its blog -heritage- and the post itself, each posts has 600 dim.
it finally clusters the matrix following a greedy argorithm. the clusters index the
posts by reblog_key and saves file in the local drive.

(!) NOTES :
-
"""

import json, os, ast, sqlite3
from datetime import date, timedelta
from scipy.cluster.vq import kmeans, vq

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

cluster_size = 2000

def main(): # (!) <--- MAIN PROCEDURE
	print "- clustering :"

	posts, postsIndex = model_dashboard(get_dashboard(), get_tumblr_model(), get_dashboard_model())
	clusters = greedy_clusters(build_index(posts, postsIndex))
	clusters = rename_key(clusters)

	# update database
	update_db(clusters)
	
	print "    %s indexed clusters"%len(clusters)
	print ''

def update_db(clusters):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for cluster in clusters:
		for post in clusters[cluster]:
			#try:
			c.execute("UPDATE lsi_dashboard SET cluster=? WHERE reblog_key=?", [cluster, post])
			#except: pass
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

def get_tumblr_model():
    """(!) the file to be loaded should be periodically updated,
    and each of the 300 dimensions should be rounded to 4 decimal points."""
    try:
        with open('/home/jorgeo/Desktop/VsCave/src/matrix_300.json', 'r') as data_file: f = json.load(data_file)
    except: print 'error not a .json file'
    return f

def get_dashboard_model():	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, post_model FROM lsi_dashboard")
	models = {key : ast.literal_eval(value1) for (key, value1) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	return models

def get_dashboard():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, blog_name FROM dashboard")
	posts = {key : value1 for (key, value1) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	return posts

def model_dashboard(dashboard, M_textModeling, dash_modeling):
	M, M_index = [],[] # <--- (!) datasets for clustering
	dim = 300 # (!) HARD NUMBER, NOT GOOD
	for key in dashboard:
		blog_name = dashboard[key]
		reblog_key = key
		thisPost = []
		try : # adding blog model
			thisPost = thisPost+M_textModeling[blog_name]
		except: thisPost = thisPost+[0]*dim
		try : # adding post model
			thisPost = thisPost+dash_modeling[reblog_key]
		except: thisPost = thisPost+[0]*dim
		if sum(thisPost) != 0:
			M.append(thisPost)
			M_index.append(reblog_key)
	return M, M_index

def build_index(posts, postsIndex):
    index = {'0':{}}
    for i in range(len(posts)): index['0'][postsIndex[i]] = posts[i]
    return index

def greedy_clusters(clusters, count=0):
	flag = False
	for cluster in clusters:
		if len(clusters[cluster]) > cluster_size:
			flag = True
			sub_index = cluster_posts(clusters[cluster])
			clusters = update_index(clusters, sub_index, cluster)
	if flag == True:
		count+=1
		clusters = greedy_clusters(clusters, count)

	return clusters

def cluster_posts(cluster, ks=2):
    new_clusters = {}
    # build matrix
    M, M_index = [], []
    for key in cluster:
        M.append(cluster[key])
        M_index.append(key)
    # cluster
    centroids,_ = kmeans(M, ks)
    idx,_ = vq(M, centroids)
    idxL = idx.tolist()
    # build dictionary
    for i in range(ks):
        thisCluster = {}
        for j in range(len(M)):
            if idxL[j] == i: thisCluster[M_index[j]] = M[j]
        new_clusters[str(i)] = thisCluster
    return new_clusters

def update_index(old_index, new_index, cluster_id):
    index = {}
    # get the last key in old_index
    last = 0
    for key in old_index:
        if int(key) > last: last = int(key)
    last+=1
    # take out the old cluster
    for key in old_index:
        if key == cluster_id: pass
        else: index[key] = old_index[key]
    # add the new clusters
    for key in new_index:
        index[str(last)] = new_index[key]
        last+=1
    return index

def rename_key(dic):
    new_dict = {}
    i = 0
    for key in dic:
        new_dict[str(i)] = dic[key]
        i+=1
    return new_dict

if __name__ == '__main__': main()

