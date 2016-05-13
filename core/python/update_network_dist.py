"""
+++ update_network_dist.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3
import networkx as nx

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main():
	print '- updating network_distance :'

	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	# get subgraph
	r = c.execute("SELECT blog_name, source_title FROM subgraph")
	graph = {key : value.split() for (key, value) in r}
	
	# get likes
	r = c.execute("SELECT id, blog_name FROM likes")
	liked = {key : value for (key, value) in r}
	
	# add my likes to the graph
	orig = 'I'
	no = [None, False]
	for post in liked:
		dest = liked[post]
		if dest in no: pass
		else:
		    if orig in graph:
		        if dest not in graph[orig]: graph[orig].append(dest)
		    else: graph[orig] = [dest] # just for the first iteration
		    
	# make graph
	G = nx.Graph(graph)
	
	# shortest path calculation
	shortests = {}
	for node in G.nodes():
		try:
		    dist = len(nx.shortest_path (G, 'I', node))
		    shortests[node] = float(dist)
		except: pass
	
	# normalise
	distances = shortests.values()
	distances_min, distances_max = min(distances), max(distances)
	for k in shortests: shortests[k] = (shortests[k] - distances_min) / (distances_max - distances_min)
	
	# update table
	for blog in shortests:
		c.execute("UPDATE tumblr_model SET network_dist=? WHERE blog_name=?", [shortests[blog], blog])
	
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	print '    ok'
	print ''

if __name__ == '__main__': main()
