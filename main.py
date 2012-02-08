#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, logging, bottle, random
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
from google.appengine.ext import db
import simplejson as json
from urllib import urlencode
from bottle import request
from datetime import datetime
from cluster import KMeansClustering
from math import floor
import pytz

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	from dev_settings import *
	bottle.debug(True)
else: #prod
	from prod_settings import *

class User(db.Model):
	oauth_token = db.StringProperty()
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	photo = db.LinkProperty()
	email = db.EmailProperty()
	link = db.LinkProperty()
	checkins = db.IntegerProperty()
	
	def from_api(self, data):
		self.firstName = data['firstName']
		self.lastName = data['lastName']
		self.photo = db.Link(data['photo'])
		self.link = db.Link(data['canonicalUrl'])
		self.email = db.Email(data['contact']['email'])
		self.checkins = int(data['checkins']['count'])
	

def prepare_request(fn):
	""" before filter that sets properties in request to be used by all request handlers """
	def wrapped():
		request.out=dict() 
		request.oauth_token = request.get_cookie('user', secret=CLIENT_SECRET)
		if request.oauth_token:
			user = User.all().filter('oauth_token =', request.oauth_token).get() # look for a User with the token
			if not user: # can't find the oauth_token
				#todo: also do this if the user's data needs to be refreshed
				# ask the api for user data
				users_url = 'https://api.foursquare.com/v2/users/self?oauth_token=%s&v=%s'%(request.oauth_token, DATEVERIFIED)
				api_response = json.loads(fetch(users_url).content)
				if 'response' in api_response and 'user' in api_response['response']: # api call succeeded 
					# look for a user with the user id
					foursquare_id=int(api_response['response']['user']['id'])
					user = User.get_by_id(foursquare_id) 
					if not user: # no user is found
						# make a new user record
						user = User(key=db.Key.from_path('User', foursquare_id))
					else: # oauth_token must have changed
						user.oauth_token = request.oauth_token
					# update the User's data while we have the api response
					user.from_api(api_response['response']['user']) 
					user.put()
					logging.info('created user')
				else: # api call failed, the oauth_token is bad
					# delete cookie
					bottle.response.set_cookie('user', None, CLIENT_SECRET) 
					logging.info('invalidated auth token')
			# store the user
			if user:
				request.user = user
			# else: oauth_token must be bad, get another
				#todo: bottle.redirect('login')?
		return fn()
	return wrapped

def get_checkins(oauth_token, total):
	api = 'https://api.foursquare.com/v2/users/self/checkins'
	params = dict(
		oauth_token=oauth_token,
		v=DATEVERIFIED)
	checkins=[]
	calls = 0

	#load the most recent checkins
	params['limit'] = total%CHECKINS_CHUNK
	api_says = fetch(api+'?'+urlencode(params))
	calls += 1
	data = json.loads(api_says.content)
	items = data['response']['checkins']['items']
	checkins.extend(items)
	
	#load chunks of checkins starting from the oldest
	params['limit'] = CHECKINS_CHUNK
	for i in range(total/CHECKINS_CHUNK):
		n = CHECKINS_CHUNK*i+CHECKINS_CHUNK
		params['offset'] = total-n
		chunk_key = 'checkins:%s:%s:%s'%(oauth_token, n, CHECKINS_CHUNK)
		chunk = memcache.get(chunk_key)
		if not chunk:
			api_says = fetch(api+'?'+urlencode(params))
			calls += 1
			chunk = api_says.content
			if not memcache.add(chunk_key, chunk, CACHE_CHECKINS):
				logging.error("memcache.add(%s) failed"%(chunk_key))
			else:
				logging.info("memcached.add(%s) succeeded"%(chunk_key))
		
		data = json.loads(chunk)
		items = data['response']['checkins']['items']
		checkins.extend(items)
	
	logging.info("Loaded %s of %s checkins in %s calls"%(len(checkins), total, calls))
	return checkins

def get_tod_data(checkins, oauth_token):
	#todo should really be pulling checkins from the DataStore so I can slice them more easily
	memcache_key='get_tod_data%s%s'%(oauth_token,len(checkins))
	data = None#memcache.get(memcache_key)
	if not data:
		data=[]
		for ci in checkins:
			if ci.get('venue', 0):
				d = datetime.fromtimestamp(ci['createdAt'], pytz.UTC).astimezone(pytz.timezone(ci['timeZone']))
				data.append((
					int(d.hour*60*60 + d.minute*60 + d.second),
					int(d.hour*60*60 + d.minute*60 + d.second)
				))
				int(d.hour*60*60 + d.minute*60 + d.second)
		if memcache.add(memcache_key, data):
			logging.error('memcache add failed %s'%(memcache_key))
	return data

def mode(iterable):
	counts = dict()
	for item in iterable:
		counts[item] = counts.get(item,0) + 1
	return max(counts, key = counts.get)

@bottle.get('/')
@prepare_request
def home():
	if not request.user:
		request.out['client_id']=CLIENT_ID
		request.out['redirect_uri']=REDIRECT_URI
		return bottle.template('welcome')
	else:
		#load all the user's checkins
		checkins = get_checkins(request.oauth_token, request.user.checkins)
		data = get_tod_data(checkins, request.oauth_token)
		kmcl = KMeansClustering(data)
		clusters = kmcl.getclusters(10)
		groups=[]
		for cl in clusters:
			tod_max=max([i[0] for i in cl])
			tod_min=min([i[0] for i in cl])
			groups.append(dict(
				len=len(cl),
				tod_avg=sum([i[0] for i in cl])/len(cl),
				tod_max=tod_max,
				tod_min=tod_min,
				width=int(floor((tod_max-tod_min)/(60*60*24/100))),
				left=int(floor(tod_min/(60*60*24/100)))
			))
				
		groups=sorted(groups, key=lambda k: k['tod_min'])
		return bottle.template('home', user=request.user, groups=groups)
	
@bottle.get('/callback')
@bottle.view('auth')
def auth():
	code = request.query.code
	access_token_url='https://foursquare.com/oauth2/access_token?client_id='+CLIENT_ID+'&client_secret='+CLIENT_SECRET+'&grant_type=authorization_code&redirect_uri='+REDIRECT_URI+'&code='+code
	auth_response=json.loads(fetch(access_token_url).content)
	if 'access_token' in auth_response:
		oauth_token=auth_response['access_token']
		bottle.response.set_cookie('user', oauth_token, secret=CLIENT_SECRET)
		logging.info(oauth_token)
		bottle.redirect('/')
	else:
		logging.error(auth_response)
		bottle.abort()
	
	#todo: store user id in DataStore in case token changes
	#todo: get an email address if we don't have one yet
	#todo: tell them what we're doing with their data and email

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
