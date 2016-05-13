"""
+++ update_pagerank.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, operator
import networkx as nx

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main():
	print '- updating pagerank :'

	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	# get subgraph
	r = c.execute("SELECT blog_name, source_title FROM subgraph")
	graph = {key : value.split() for (key, value) in r}
	
	G = nx.DiGraph(graph)
	pr = nx.pagerank_scipy(G, alpha=0.85)
	
	# normalise
	ranks = pr.values()
	rank_min, rank_max = min(ranks), max(ranks)
	for k in pr: pr[k] = round(((pr[k] - rank_min) / (rank_max - rank_min)), 4)
	
	# update table
	for blog in pr:
		c.execute("UPDATE tumblr_model SET pagerank=? WHERE blog_name=?", [pr[blog], blog])
	
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	# sorting, optional
	pr_sorted = sorted(pr.items(), key=operator.itemgetter(1))
	print "    %s is the most popular domain in the network"%pr_sorted[-1:][0][0] 
	print '' 
	
if __name__ == '__main__': main()

