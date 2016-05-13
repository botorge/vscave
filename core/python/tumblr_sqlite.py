"""
+++ tumblr_sqlite.py +++
WHAT'S NEW :
-
"""

import sqlite3

def create_table(db_name, table_name, cols, primary=None):
	""" variable cols should be a dictionary type with form {'column_name': 'column_type', ...} """
	keys = [key for key in cols]
	vals = [cols[key] for key in cols]
	cols = ['%s %s'%(keys[i], vals[i]) for i in range(len(keys))]
	if primary: cols.append("PRIMARY KEY ("+ ", ".join(primary) + ")")
	# build command
	#exec_text = 'INSERT INTO t (' + ','.join(cols) + ') values(' + ','.join(['TEXT'] * len(cols)) + ')'
	exec_text = 'CREATE TABLE IF NOT EXISTS %s ('%table_name + ', '.join(cols) + ')'
	
	# connect to db
	conn = sqlite3.connect(db_name)
	c = conn.cursor()
	
	# execute
	c.execute(exec_text)
	
	# commit and close
	conn.commit()
	conn.close()

def create_table_scratch(db_name, table_name, cols, primary=None):
	""" variable cols should be a dictionary type with form {'column_name': 'column_type', ...} """
	keys = [key for key in cols]
	vals = [cols[key] for key in cols]
	cols = ['%s %s'%(keys[i], vals[i]) for i in range(len(keys))]
	if primary: cols.append("PRIMARY KEY ("+ ", ".join(primary) + ")")
    
	# build command
	exec_text = 'CREATE TABLE %s ('%table_name + ', '.join(cols) + ')'
	
	# connect to db
	conn = sqlite3.connect(db_name)
	c = conn.cursor()
	
	# execute
	c.execute("DROP TABLE IF EXISTS %s"%table_name)
	c.execute(exec_text)
	
	# commit and close
	conn.commit()
	conn.close()

def get_columns(db_name, table_name):
	# connect to db
	conn = sqlite3.connect(db_name)
	c = conn.cursor()
	# execute
	cols = [key[1] for key in c.execute("pragma table_info(%s)"%table_name)]
	# commit and close
	conn.commit()
	conn.close()
	
	return cols
	


