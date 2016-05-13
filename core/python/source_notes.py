"""
+++ source_notes.py +++
WHAT'S NEW :
- 

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, time
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def get_days():
    """ this procedure returns the variables as obejects and not as strings """
    today = date.today()
    yesterday = today - timedelta(1)
    before_yesterday = yesterday - timedelta(1)
    return today, yesterday, before_yesterday

def main():
	print "- sourcing blog's notes :"
	today,_,_ = get_days()
	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	
	# DB-EXECUTE
	# get previous notes
	r = c.execute("SELECT blog_name, notes_min, notes_max, notes_timestamp FROM tumblr_model")
	notes_index = {key : [value1, value2, value3] for (key, value1, value2, value3) in r}
		
	# get blog_name to source
	r = c.execute("SELECT DISTINCT blog_name FROM dashboard")
	blog_names = [key[0] for key in r]
	print "    %s blog's archives to source"%len(blog_names)

	# get note counts
	count, p = 0, 0
	for name in blog_names:
		if count%int((len(blog_names)/10)) == 0:
			print "    %s%s"%(p, '%')
			p+=10
		now = int(time.time())
		try: updated = int(notes_index[name][2])
		except: updated = 0
		if (now-updated) < 2628000: pass # one month in seconds
		else:
			get_notes(notes_index, name, today, 100)
			try: c.execute("INSERT INTO tumblr_model (blog_name) VALUES (?)", [name])
			except: pass
			try:
				c.execute("UPDATE tumblr_model SET notes_min=?, notes_max=?, notes_timestamp=? WHERE blog_name=?",
					[notes_index[name][0], notes_index[name][1], notes_index[name][2], name])
			except : print "sqlite3 error"
		count+=1
	
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	print ''

def get_notes(index, blog_name, today, sample_size):
    """ this procedure updates the index variable with max
    sample_size of post's note_count from the last 6 months """
    notes = []
    year, month = today.year, today.month
    for i in range(6): # for the lasts six months
        if len(notes) < sample_size:
            thisNotes = get_month(blog_name, year, month)
            notes = notes+thisNotes
            month -= 1
            if month == 0: year -= 1; month = 12
    try: mmin, mmax = min(notes[:sample_size]), max(notes[:sample_size])
    except: mmin, mmax = 0, 0
    # update the variable
    index[blog_name] = [mmin, mmax, int(time.time())]

def get_month(blog_name, year, month):
    """ this procedure parses the posts' note count per month """
    notes = []
    doc = 'http://%s.tumblr.com/archive/%s/%s'%(blog_name, year, month)
    try: r = requests.get(doc)
    except: r = None
    if r:
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.body.find_all('a'):
            try:
                if tag['class'][0] == 'hover':
                    for tag2 in tag.find_all('span'):
                        try: notes.append(int(tag2['data-notes']))
                        except: pass
                else: pass
            except: pass
    else: print '    error requesting %s'%blog_name # (!) keep track of these failures
    return notes


if __name__ == '__main__': main()

