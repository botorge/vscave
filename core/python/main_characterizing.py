"""
+++ main_characterizing.py +++
WHAT'S NEW :
-

THIS MODULE :
-

NOTES :
-
"""

from datetime import date, timedelta, datetime
from os import listdir
from os.path import isfile, join
import os, json, time
import db_manager
import build_dashboard, build_subgraph
import update_likes, update_timestamp, update_graph, update_pagerank, update_network_dist
import source_notes
import modeling_text, modeling_network
import cluster, spectrum, render
import network_manager

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'

def main():
	ini = datetime.now()
	new_flags = {}
	# get the flags
	try:
		with open(path+'main_flags.json', 'r') as data_file: flags = json.load(data_file)
	except: print 'error loading main_flags.json'
	
	# get previous files to render
	render_dir = "/home/jorgeo/Desktop/VsCave_render/"
	contents = [f for f in listdir(render_dir) if isfile(join(render_dir, f))]
	today = date.today()
	yesterday = str(today - timedelta(1))+'.json'
	
	if yesterday in contents:
		new_flags['first'], new_flags['second'] = 0,0
		print "done, refresh your browser !"
	else:
		if flags['first'] == 1:
			print '(!) getting your daily images 1/2'
	
			db_manager.main()
			build_dashboard.main()
			update_timestamp.main()
			update_likes.main()
			update_graph.main()
			build_subgraph.main()
			update_pagerank.main()
			update_network_dist.main()
			source_notes.main()
		
			new_flags['first'], new_flags['second'] = 0,1
			print 'done in %s, rebooting the system !'%str(datetime.now()-ini)
			time.sleep(30)
		
		if flags['second'] == 1:
			print '(!) getting your daily images 2/2'
		
			modeling_text.topic_modeling()
			modeling_network.main()
			cluster.main()
			spectrum.main()
			render.main()
		
			new_flags['first'], new_flags['second'] = 1,0
			print 'done in %s, refresh your browser !'%str(datetime.now()-ini)
	
		# update the flags file
		try:
			with open(path+'main_flags.json', 'w') as f: json.dump(new_flags,f)
		except: print 'error saving main_flags.json'
	
	if new_flags['first'] == 0 and new_flags['second'] == 1: os.system('echo asdfla|sudo -S reboot')
	else: network_manager.main()

if __name__ == '__main__': main()

