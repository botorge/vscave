"""
+++ build_subgraph.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, tumblr_sqlite, time

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main(): 
	print '- building subgraph :'
    
    # DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	# get graph
	r = c.execute("SELECT blog_name, source_title FROM graph")
	graph = {key : value.split() for (key, value) in r}
	graph_count = len(graph)
	
	# get timestamps
	r = c.execute("SELECT blog_name, timestamp FROM tumblr_model")
	timestamps = {key : value for (key, value) in r}
	
	# build subgraph
	subgraph = {}
	months3 = 7884000
	hours24 = 86400
	past = int(time.time()-months3)
	for node in graph:
		try:
			if timestamps[node] > past: subgraph[node] = graph[node]
		except: subgraph[node] = graph[node]
	
	# update table
	for blog in subgraph:
		val = ' '.join(subgraph[blog])
		c.execute("INSERT INTO subgraph (blog_name, source_title) VALUES (?,?)", [blog, val])

	# count rows
	r = c.execute("SELECT blog_name, source_title FROM subgraph")
	subgraph = {key : value.split() for (key, value) in r}
	subgraph_count = len(subgraph)

	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

	# prints out the changes in the graph
	print '    %s nodes in subgraph from'%subgraph_count
	print '    %s nodes in graph'%graph_count
	print ''
    
if __name__ == '__main__': main()

