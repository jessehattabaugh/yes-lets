#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, bottle
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch
import simplejson as json

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	from dev_settings import *
	bottle.debug(True)
else: #prod
	from prod_settings import *

def before(fn):
	def wrapped():
		bottle.request.out=dict()
		bottle.request.oauth_token=bottle.request.get_cookie('user', secret=CLIENT_SECRET)
		if bottle.request.oauth_token:
			user_info_url='https://api.foursquare.com/v2/users/self?oauth_token='+bottle.request.oauth_token+'&v='+DATEVERIFIED
			api_string = fetch(user_info_url).content
			api_response=json.loads(api_string)
			if 'response' in api_response and 'user' in api_response['response']:
				bottle.request.out['user']=api_response['response']['user']
			else:
				bottle.response.set_cookie('user', None, CLIENT_SECRET)
				bottle.request.out['debug']='invalidated auth token'
		#todo memcache user data for up to 30 days
		return fn()
	return wrapped

@bottle.get('/')
@bottle.view('home')
@before
def home():
	if not 'user' in bottle.request.out:
		bottle.request.out['client_id']=CLIENT_ID
		bottle.request.out['redirect_uri']=REDIRECT_URI
	else:
		#load all the user's checkins
	return bottle.request.out
	
@bottle.get('/callback')
@bottle.view('main')
def after_auth():
	code = bottle.request.query.code
	access_token_url='https://foursquare.com/oauth2/access_token?client_id='+CLIENT_ID+'&client_secret='+CLIENT_SECRET+'&grant_type=authorization_code&redirect_uri='+REDIRECT_URI+'&code='+code
	auth_response=json.loads(fetch(access_token_url).content)
	if 'access_token' in auth_response:
		oauth_token=auth_response['access_token']
		bottle.response.set_cookie('user', oauth_token, secret=CLIENT_SECRET)
		return dict(debug=oauth_token)
	else:
		return dict(debug=auth_response)
	
	#todo: store user id in DataStore in case token changes
	#todo: get an email address if we don't have one yet
	#todo: tell them what we're doing with their data and email

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
