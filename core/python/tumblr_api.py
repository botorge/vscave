"""
+++ tumblr_api.py +++
WHAT'S NEW :
-
"""

import pytumblr, json

def auth(path):
	credentials = json.loads(open(path+'tumblr_credentials.json', 'r').read())
	client = pytumblr.TumblrRestClient(credentials['consumer_key'], credentials['consumer_secret'], credentials['oauth_token'], credentials['oauth_token_secret'])
	return client

def get_dashboard(path, numPosts=20):
	client = auth(path)
	return client.dashboard(limit=numPosts)
	
def get_following(path, offset=0):
	client = auth(path)
	return client.following(offset=offset)

def unfollow(path, blog):
	client = auth(path)
	return client.unfollow('http://%s.tumblr.com/'%blog)
	
def follow(path, blog):
	client = auth(path)
	command = 'http://%s.tumblr.com/'%blog
	return client.follow(command)

def blog_info(path, blog):
	client = auth(path)
	return client.blog_info(blog)
