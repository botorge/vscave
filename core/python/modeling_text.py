"""
+++ VsCave_0.04 : modeling_text.py +++
WHAT'S NEW :
-

THIS MODULE :
-

(!) NOTES :
- the gensim text modeling happens in 3 different procedures in this module, not efficient.
"""

import os, sqlite3, numpy, ast
from gensim import corpora, models, similarities
from collections import defaultdict
from bs4 import BeautifulSoup
from stop_words import get_stop_words

thisPath = os.path.dirname(os.path.abspath(__file__))
path = thisPath[:-11]+'src/'
db_path = path+'vscave.db'

def topic_modeling(): # (!) <--- MAIN PROCEDURE
    numTopics = 300
    liked = get_liked()
    modeling_tags(liked, numTopics)
    modeling_caption(liked, numTopics)
    modeling_dashboard(numTopics)

def get_liked():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, tags, caption FROM likes")
	liked = {key : [value1, value2] for (key, value1, value2) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	return liked

def modeling_tags(liked, numTopics):
	print '- my likes tag modeling :'
	
	# get documents
	documents = []
	for like in liked:
		s = unicode(' ')
		documents.append(s.join(liked[like][0]))

	# remove common and repeated words, and tokenize
	#stoplist = set('for a of the and to in'.split())
	stoplist = get_stop_words('en')
	texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
	frequency = defaultdict(int)
	for text in texts:
		for token in text: frequency[token] += 1
	texts = [[token for token in text if frequency[token] > 0] for text in texts]
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]

	# transformations
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=numTopics)
	corpus_lsi = lsi[corpus_tfidf]
	index = similarities.MatrixSimilarity(corpus_lsi)
	
	# save transformation
	dictionary.save('/tmp/tags.dict')
	corpora.MmCorpus.serialize('/tmp/tags.mm', corpus)
	index.save('/tmp/tags.index')
	lsi.save('/tmp/tags.lsi')

	print '    ok'
	print ''
        
def modeling_caption(liked, numTopics):
    print '- my likes caption modeling :'
    
    # get documents
    documents = []
    for post in liked:
        try:
            soup = BeautifulSoup(post[1], "html.parser")
            text = soup.get_text(" ", strip=True)
            documents.append(text)
        except: pass
    
    # remove common and repeated words, and tokenize
    stoplist = set("for a of the and to in , - ~ | : (via via (by by ( )".split())
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
    frequency = defaultdict(int)
    for text in texts:
        for token in text: frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # transformations
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=numTopics)
    corpus_lsi = lsi[corpus_tfidf]
    index = similarities.MatrixSimilarity(corpus_lsi)
    
    # save transformations
    index.save('/tmp/caption.index')
    dictionary.save('/tmp/caption.dict')
    corpora.MmCorpus.serialize('/tmp/caption.mm', corpus)
    lsi.save('/tmp/caption.lsi')

    print '    ok'
    print ''

def modeling_dashboard(numTopics):
	print '- dashboard modeling :'
	
	documents, documentsIndex, posts = get_dashboard()
	# remove common and repeated words, and tokenize
	stoplist = set("for a of the and to in , - ~ | : (via via (by by ( )".split())
	texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
	frequency = defaultdict(int)
	for text in texts:
		for token in text: frequency[token] += 1
	texts = [[token for token in text if frequency[token] > 1] for text in texts]
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	
	# transformations
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=numTopics)
	corpus_lsi = lsi[corpus_tfidf]
	
	# build an operable matrix
	topics = {} # the keys are the 'reblog_key' from each post
	i = 0
	for doc in corpus_lsi:
		if len(doc) == numTopics:
			thisB = [round(dimensions[1], 4) for dimensions in doc]
		else: thisB = [0]*numTopics
		topics[documentsIndex[i]] = thisB
		i+=1
	
	# update database
	update_db(topics, posts)
	
	print '    ok'
	print ''
	
def update_db(topics, posts):
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for key in topics:
		try:
			c.execute("INSERT INTO lsi_dashboard (reblog_key, post_model) VALUES (?,?)", [key, str(topics[key])])
		except: pass
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()
	
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	for key in posts:
		try:
			c.execute("UPDATE lsi_dashboard SET blog_name=? WHERE reblog_key=?", [posts[key][2], key])
		except: pass
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

def get_dashboard():
	# DB-CONNECT
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	# DB-EXECUTE
	r = c.execute("SELECT reblog_key, tags, caption, blog_name FROM dashboard")
	posts = {key : [ast.literal_eval(value1), value2, value3] for (key, value1, value2, value3) in r}
	# DB-COMMIT AND CLOSE
	conn.commit()
	conn.close()

	# build the variables
	caption_tags, index = [], []
	for post in posts:
		thisCapTag = str()
		# add caption
		try:
			soup = BeautifulSoup(posts[post][1], "html.parser")
			text = soup.get_text(" ", strip=True)
			thisCapTag = text
		except: pass
		# add tags
		s = str(' ')
		thisCapTag = thisCapTag+' '+s.join(posts[post][0])
		# substitute not desired characters
		characters = set("# : . ,".split())
		for ch in characters: thisCapTag = thisCapTag.replace(ch, ' ')
		# add to the main variable
		caption_tags.append(thisCapTag)
		index.append(post)
	return caption_tags, index, posts

if __name__ == '__main__': topic_modeling()

