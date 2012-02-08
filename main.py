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
import time

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	from dev_settings import *
	bottle.debug(True)
else: #prod
	from prod_settings import *

class User(db.Model):
	'Key.id() == user.id'
	oauth_token = db.StringProperty()
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	photo = db.LinkProperty()
	email = db.EmailProperty()
	link = db.LinkProperty()
	
	def from_api(self, data):
		self.firstName = data['firstName']
		self.lastName = data['lastName']
		self.photo = db.Link(data['photo'])
		self.link = db.Link(data['canonicalUrl'])
		self.email = db.Email(data['contact']['email'])
		
	def checkins(self):
		memcache_key = 'checkins:%s'%self.key().id()
		checkins = memcache.get(memcache_key)
		if not checkins:
			# Load all checkins from the DataStore
			query = Checkin.all().filter('user =', self).order('created')
			checkins = [ci for ci in query]
			if not checkins:
				checkins = []
			
			# Look for new checkins
			api = 'https://api.foursquare.com/v2/users/self/checkins'
			params = dict(
				oauth_token=self.oauth_token,
				v=DATEVERIFIED,
				limit=CHECKINS_CHUNK)
			calls = 0
			while calls < 20:
				
				# ask the api for all the checkins since the last one
				if len(checkins) > 0:
					params['afterTimestamp'] = checkins[0].timestamp
				
				api_says = fetch('%s?%s'%(api, urlencode(params)))
				calls += 1
				data = json.loads(api_says.content)
				if api_says.status_code == 401:
					raise ApiException(data['meta']['errorType'])
					
				data = json.loads(api_says.content)
				
				items = data['response']['checkins']['items']
				
				# store the new checkins
				new_checkins = []
				for ci in items:
					checkin = Checkin(key=db.Key.from_path('Checkin', ci['id']))
					checkin.user = self
					checkin.from_api(ci)
					checkin.put()
					new_checkins.append(checkin)
					
				# add the new checkins to the list
				new_checkins.extend(checkins)
				checkins = new_checkins
				
				# quit when less than the limit are returned
				if len(items) < CHECKINS_CHUNK:
					break
			logging.info('performed %s api calls'%calls)
			if not memcache.add(memcache_key, checkins, CACHE_CHECKINS):
				logging.error('memcache.add(%s) failed'%memcache_key)
		return checkins
	
	def time_of_day_data(self):
		checkins = self.checkins()
		data=[]
		for ci in checkins:
			data.append((
				ci.time_of_day(),
				ci.time_of_day()
			))
		return data
	#end User

class ApiException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Checkin(db.Model):
	'Key.name() == checkin.id'
	user = db.ReferenceProperty(User)
	created = db.DateTimeProperty()
	location = db.GeoPtProperty()
	timestamp = db.IntegerProperty()
	
	def from_api(self, data):
		self.timestamp = data['createdAt']
		date = datetime.fromtimestamp(data['createdAt'], pytz.UTC)
		self.created = date.astimezone(pytz.timezone(data['timeZone']))
		lat=None
		lng=None
		if data.get('location', False):
			lat = data['location']['lat']
			lng = data['location']['lng']
		elif data.get('venue'):
			lat = data['venue']['location']['lat']
			lng = data['venue']['location']['lng']
		self.location = db.GeoPt(lat, lng)
		
	def time_of_day(self):
		return int(self.created.hour*60*60 + self.created.minute*60 + self.created.second)
		
def prepare_request(fn):
	""" before filter that sets properties in request to be used by all request handlers """
	def wrapped():
		oauth_token = request.get_cookie('user', secret=CLIENT_SECRET)
		if oauth_token:
			user = User.all().filter('oauth_token =', oauth_token).get() # look for a User with the token
			if not user: # can't find the oauth_token
				#todo: also do this if the user's data needs to be refreshed
				
				# ask the api for user data
				users_url = 'https://api.foursquare.com/v2/users/self?oauth_token=%s&v=%s'%(oauth_token, DATEVERIFIED)
				api_response = json.loads(fetch(users_url).content)
				if 'response' in api_response and 'user' in api_response['response']: # api call succeeded 
				
					# look for a user with the user id
					foursquare_id=int(api_response['response']['user']['id'])
					user = User.get_by_id(foursquare_id) 
					if not user: # no user is found
					
						# make a new user record
						user = User(key=db.Key.from_path('User', foursquare_id))
						
					else: # oauth_token must have changed
						user.oauth_token = oauth_token
						
					# update the User's data while we have the api response
					user.from_api(api_response['response']['user']) 
					user.put()
					logging.info('created user')
				else: # api call failed, the oauth_token is bad
					# delete cookie
					bottle.response.delete_cookie('user') 
					logging.info('invalidated auth token')
			
			# store the user
			if user:
				request.user = user
				
			# else: oauth_token must be bad, get another
				#todo: bottle.redirect('login')?
		return fn()
	return wrapped

def mode(iterable):
	counts = dict()
	for item in iterable:
		counts[item] = counts.get(item,0) + 1
	return max(counts, key = counts.get)

def pretty_tod(tod):
	t = time.gmtime(tod)
	return str(abs(int(time.strftime('%I',t))))+time.strftime('%p',t).lower()

@bottle.get('/')
@prepare_request
def home():
	
	if not hasattr(request, 'user'):
		return bottle.template('welcome', 
			client_id=CLIENT_ID, 
			redirect_uri=REDIRECT_URI)
			
	else:
		try: # get clustering data
			tod_data = request.user.time_of_day_data()
		except ApiException:
			# delete cookie
			bottle.response.delete_cookie('user') 
			logging.info('invalidated auth token')
			bottle.redirect('/')
		
		# determine clusters
		kmcl = KMeansClustering(tod_data)
		clusters = kmcl.getclusters(10)
		
		groups=[]
		for cl in clusters:
			tod_max=max([i[0] for i in cl])
			tod_min=min([i[0] for i in cl])
			groups.append(dict(
				len=len(cl),
				tod_avg=sum([i[0] for i in cl])/len(cl),
				tod_min=tod_min,
				start=pretty_tod(tod_min),
				end=pretty_tod(tod_max),
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
