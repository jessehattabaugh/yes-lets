#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, logging, bottle, random
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
import simplejson as json
from urllib import urlencode
from bottle import request
from datetime import datetime
from cluster import KMeansClustering

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	from dev_settings import *
	bottle.debug(True)
else: #prod
	from prod_settings import *

def before(fn):
	def wrapped():
		request.out=dict()
		request.oauth_token=request.get_cookie('user', secret=CLIENT_SECRET)
		if request.oauth_token:
			user_info_url='https://api.foursquare.com/v2/users/self?oauth_token='+request.oauth_token+'&v='+DATEVERIFIED
			api_response=json.loads(fetch(user_info_url).content)
			if 'response' in api_response and 'user' in api_response['response']:
				request.out['user']=api_response['response']['user']
			else:
				bottle.response.set_cookie('user', None, CLIENT_SECRET)
				logging.info('invalidated auth token')
		#todo memcache user data for up to 30 days
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
		chunk_key = 'checkins'+oauth_token+'chunk'+str(n)
		chunk = memcache.get(chunk_key)
		if not chunk:
			api_says = fetch(api+'?'+urlencode(params))
			calls += 1
			data = json.loads(api_says.content)
			chunk = data['response']['checkins']['items']
			if not memcache.replace(chunk_key, chunk, CACHE_CHECKINS):
				logging.error("memcache.add(%s) failed"%(chunk_key))
			else:
				logging.info("memcached.add(%s) succeeded"%(chunk_key))
		checkins.extend(chunk)
	
	logging.info("Loaded %s of %s checkins in %s calls"%(len(checkins), total, calls))
	return checkins

def get_cluster_data(checkins):
	data = []
	for ci in checkins:
		if ci.get('venue', 0):
			d = datetime.fromtimestamp(ci['createdAt'])
			data.append((
				int(ci['createdAt']),
				int(d.hour*60*60 + d.minute*60 + d.second),
				int(d.weekday()),
				ci['venue']['location']['lat'],
				ci['venue']['location']['lng']
			))
	return data

def mode(iterable):
	counts = dict()
	for item in iterable:
		counts[item] = counts.get(item,0) + 1
	return max(counts, key = counts.get)

@bottle.get('/')
@bottle.view('home')
@before
def home():
	if not 'user' in request.out:
		request.out['client_id']=CLIENT_ID
		request.out['redirect_uri']=REDIRECT_URI
	else:
		#load all the user's checkins
		checkins = get_checkins(request.oauth_token, request.out['user']['checkins']['count'])
		data = get_cluster_data(checkins)
		kmcl = KMeansClustering(data)
		clusters = kmcl.getclusters(6)
		groups=[]
		for cl in clusters:
			groups.append(dict(
				len=len(cl),
				tod_avg=sum([i[1] for i in cl])/len(cl),
				tod_max=max([i[1] for i in cl]),
				tod_min=min([i[1] for i in cl]),
				day_avg=mode([i[2] for i in cl]),
				day_max=max([i[2] for i in cl]),
				day_min=min([i[2] for i in cl]),
				lat_avg=sum([i[3] for i in cl])/len(cl),
				lat_max=max([i[3] for i in cl]),
				lat_min=min([i[3] for i in cl]),
				lng_avg=sum([i[4] for i in cl])/len(cl),
				lng_max=max([i[4] for i in cl]),
				lng_min=min([i[4] for i in cl])
			))
		request.out['groups'] = groups
	return request.out
	
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
	else:
		logging.error(auth_response)
	return dict()
	
	#todo: store user id in DataStore in case token changes
	#todo: get an email address if we don't have one yet
	#todo: tell them what we're doing with their data and email

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
