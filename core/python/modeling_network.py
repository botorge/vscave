"""
+++ modeling_network.py +++
WHAT'S NEW :
-

THIS MODULE :
-

(!) NOTES :
-
"""

import os, sqlite3, ast
from gensim import corpora, models, similarities
from bs4 import BeautifulSoup

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def main():
	print "- modeling posts by network :"

	daily_index = {} # <--- MAIN VARIABLE
	dashboard = get_dashboard()
	update_dashboard(dashboard)
	build_index(dashboard)
	modeling_text(dashboard)
	update_db(dashboard)
	
	print "    %s photo posts modeled"%len(dashboard)
	print ''

def update_db(dashboard):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for post in dashboard:
		#print dashboard[post], post
		c.execute("UPDATE lsi_dashboard SET network_model=? WHERE reblog_key=?", [str(dashboard[post]), post])
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

def get_dashboard():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, blog_name, tags, caption, note_count FROM dashboard")
	posts = {key : [value1, ast.literal_eval(value2), value3, value4] for (key, value1, value2, value3, value4) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return posts

def update_dashboard(dashboard):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT blog_name, pagerank, network_dist, notes_max, notes_min FROM tumblr_model")
	blogs = {key: [value1, value2, value3, value4] for (key, value1, value2, value3, value4) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	# update dashboard
	for key in dashboard:
		try: tumblr_model = blogs[dashboard[key][0]]
		except:
			print '    %s has not been modeled yet'%dashboard[key][0]
			tumblr_model = [0.5, 0.5, 1, 0] # (!) where to place missing values ?
		dashboard[key] = dashboard[key][1:]+tumblr_model
	return dashboard

def build_index(dashboard):
	for post in dashboard:
		this_post = []
		# 0. tags
		s = unicode(' ')
		this_post.append(s.join(dashboard[post][0]))
		# 1. caption
		try:
			soup = BeautifulSoup(dashboard[post][1], "html.parser")
			text = soup.get_text(" ", strip=True)
			this_post.append(text)
		except: this_post.append(str())
		# 2. add pagerank
		try: this_post.append(round(dashboard[post][3],4))
		except: this_post.append(0.5) # (!) where to put a missing value ?
		# 3. add network distance
		try: this_post.append(round(dashboard[post][4], 4))
		except: this_post.append(0.5) # (!) where to put a missing value ?
		# 4. add local popularity
		note_count = dashboard[post][2]
		this_post.append(note_count)
		# 5. add global popularity
		try:
			note_max = dashboard[post][5]
			note_min = dashboard[post][6]
			g_pop = round((note_count - note_min) / (note_max - note_min), 4)
			this_post.append(g_pop)
		except: this_post.append(0.5) # (!) where to put a missing value ?
		# update dashboard
		dashboard[post] = this_post

def modeling_text(daily_images):
    tags_dictionary = corpora.Dictionary.load('/tmp/tags.dict')
    tags_corpus = corpora.MmCorpus('/tmp/tags.mm')
    tags_tfidf = models.TfidfModel(tags_corpus)
    tags_corpus_tfidf = tags_tfidf[tags_corpus]
    tags_lsi = models.LsiModel(tags_corpus_tfidf, id2word=tags_dictionary, num_topics=300)
    tags_index = similarities.MatrixSimilarity.load('/tmp/tags.index')
    for post in daily_images:
        tags_vec_bow = tags_dictionary.doc2bow(daily_images[post][0].lower().split())
        tags_vec_tfidf = tags_tfidf[tags_vec_bow] # needs to be transformed to tfidf, because the lsi is tfidf
        tags_vec_lsi = tags_lsi[tags_vec_tfidf] # convert the query to LSI space
        tags_sims = tags_index[tags_vec_lsi]
        tags_sims = sorted(enumerate(tags_sims), key=lambda item: item[1])
        tag_value = tags_sims[-1:][0]
        daily_images[post][0] = round(tag_value[1], 4) # substitute tags for value
		
    caption_dictionary = corpora.Dictionary.load('/tmp/caption.dict')
    caption_corpus = corpora.MmCorpus('/tmp/caption.mm')
    caption_tfidf = models.TfidfModel(caption_corpus)
    caption_corpus_tfidf = caption_tfidf[caption_corpus]
    caption_lsi = models.LsiModel(caption_corpus_tfidf, id2word=caption_dictionary, num_topics=300)
    caption_index = similarities.MatrixSimilarity.load('/tmp/caption.index')
    for post in daily_images:
        caption_vec_bow = caption_dictionary.doc2bow(daily_images[post][1].lower().split())
        caption_vec_tfidf = caption_tfidf[caption_vec_bow] # needs to be transformed to tfidf, because the lsi is tfidf
        caption_vec_lsi = caption_lsi[caption_vec_tfidf] # convert the query to LSI space
        caption_sims = caption_index[caption_vec_lsi]
        caption_sims = sorted(enumerate(caption_sims), key=lambda item: item[1])
        caption_value = caption_sims[-1:][0]
        daily_images[post][1] = round(caption_value[1], 4) # substitute caption for value
    return daily_images

if __name__ == '__main__': main()

