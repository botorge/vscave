"""
+++ update_graph.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, tumblr_sqlite

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main(): 
	print '- updating graph :'
    
    # DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	# get graph
	r = c.execute("SELECT blog_name, source_title FROM graph")
	graph = {key : value.split() for (key, value) in r}
	graph_ini_count = len(graph)
	
	no = [None, False]
	r = c.execute("SELECT blog_name, source_title FROM dashboard")
	for key in r:
		blog_name, source_title = key[0], key[1]
		if blog_name == source_title: pass
		elif source_title in no: pass
		else: 
			if blog_name in graph:
				if source_title not in graph[blog_name]: graph[blog_name].append(source_title)
			else: graph[blog_name] = [source_title]
	
	# update table
	for blog in graph:
		val = ' '.join(graph[blog])
		c.execute("INSERT OR REPLACE INTO graph (blog_name, source_title) VALUES (?,?)", [blog, val])

	# count rows
	r = c.execute("SELECT blog_name, source_title FROM graph")
	graph = {key : value.split() for (key, value) in r}
	graph_final_count = len(graph)

	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

	# prints out the changes in the graph
	new_nodes = graph_final_count - graph_ini_count
	print '    %s new nodes in graph'%new_nodes
	print '    %s total nodes in graph'%graph_final_count
	print ''
    
if __name__ == '__main__': main()

