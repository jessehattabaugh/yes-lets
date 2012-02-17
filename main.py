#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, logging, bottle, random
from bottle import request, response, redirect, get, abort, template
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
from google.appengine.ext import db
import simplejson as json
from urllib import urlencode
from datetime import datetime
from cluster import KMeansClustering
from math import floor
import pytz
import time

# Load appropriate settings globals
if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	from dev_settings import *
	bottle.debug(True)
else: #prod
	from prod_settings import *

# Custom Exceptions
class ApiException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# Models
class User(db.Model):
	#Key.id() == user.id
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
	
	@classmethod
	def current(self):
		"""returns a User instance representing the currently authenticated 
		user"""
		
		oauth_token = request.get_cookie('user', secret=CLIENT_SECRET)
		if oauth_token:
			
			# look for a User with the token
			user = User.all().filter('oauth_token =', oauth_token).get() 
			
			if not user: # can't find the oauth_token
				#todo: also do this if the user's data needs to be refreshed
				
				# ask the api for user data
				users_url = 'https://api.foursquare.com/v2/users/self?oauth_token=%s&v=%s'%(oauth_token, DATEVERIFIED)
				api_response = json.loads(fetch(users_url).content)
				logging.info('API call: %s'%users_url)
				if 'response' in api_response and 'user' in api_response['response']: # api call succeeded 
				
					# look for a user with the user id
					foursquare_id=int(api_response['response']['user']['id'])
					user = User.get_by_id(foursquare_id) 
					if not user: # no user is found
					
						# make a new user record
						user = User(key=db.Key.from_path('User', foursquare_id))
						logging.info('Created a new User')
						
					else: # oauth_token must have changed
						user.oauth_token = oauth_token
						
					# update the User's data while we have the api response
					user.from_api(api_response['response']['user']) 
					user.put()
					logging.info('User.put OAuth Token: %S'%oauth_token)
			#else: what if oauth_token has been revoked
			
			if user:
				return user
			else: # the oauth_token is bad
				unauthenticate()
	
	def checkins(self):
		"""Gets a User's Checkins from DataStore, fetching new ones from the 
		API if necessary"""
		
		# the lifespan of this memcache value determines the frequency of 
		# polling for new checkins
		memcache_key = 'checkins:%s'%self.key().id()
		checkins = memcache.get(memcache_key)
		if not checkins:
			
			# Load all checkins from the DataStore
			query = Checkin.all().filter('user =', self).order('created')
			checkins = [ci for ci in query]
			if not checkins:
				checkins = []
			#todo: find out what happens when someone has a butt-ton of checkins
			
			# Look for new checkins
			#todo: don't bother if it hasn't been very long since the last one
			api = 'https://api.foursquare.com/v2/users/self/checkins'
			params = dict(
				oauth_token=self.oauth_token,
				v=DATEVERIFIED,
				limit=CHECKINS_CHUNK)
			calls = 0
			while calls < 20: # do at most 20 API calls
				
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
			#todo: decide what to do with old checkins
			#todo: move this to the TaskQueue of course
			
			if not memcache.add(memcache_key, checkins, CACHE_CHECKINS):
				logging.error('memcache.add(%s) failed'%memcache_key)
		return checkins
	
	def time_of_day_data(self): #todo: allow min/max parameters
		"""Returns a list of tuples representing the time of day of a user's
		checkins"""
		
		try:
			checkins = self.checkins()
		except ApiException:
			deauthenticate()
			
		data=[]
		for ci in checkins:
			data.append((
				ci.time_of_day(),
				ci.time_of_day()
			))
		return data
	
	def geo_data(self): #todo: allow min/max parameters
		"""Returns a list of tuples representing the lat/lng of a user's
		checkins"""
		try:
			checkins = self.checkins()
		except ApiException:
			deauthenticate()
			
		data=[]
		for ci in checkins:
			data.append((
				ci.location.lat,
				ci.location.lon
			))
		return data
	#end User

class Checkin(db.Model):
	#Key.name() == checkin.id
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
		hour_seconds = self.created.hour*60*60
		minute_seconds = self.created.minute*60
		return int(hour_seconds + minute_seconds + self.created.second)

# Plain old functions
def mode(iterable):
	counts = dict()
	for item in iterable:
		counts[item] = counts.get(item,0) + 1
	return max(counts, key = counts.get)

def pretty_tod(tod):
	t = time.gmtime(tod)
	hour_with_no_leading_zero = str(abs(int(time.strftime('%I',t))))
	lowercase_am_or_pm = time.strftime('%p',t).lower()
	return hour_with_no_leading_zero + lowercase_am_or_pm

def deauthenticate():
	response.delete_cookie('user')
	request.user = None
	logging.info('invalidated auth token')
	redirect('/')

# Request handlers
@get('/<user_id>')
@get('/')
def home():
	request.user = User.current()
	
	if not request.user:
		return template('welcome', 
			client_id=CLIENT_ID, 
			redirect_uri=REDIRECT_URI)
	
	else:
		
		if not user_id None:
			user = User(db.Key.from_path('User', int(user_id)))
		w   e
		tod_data = request.user.time_of_day_data()
		if not user None:
			user = User(db.Key.from_path('User', int(user_id)))
			tod_data.extend(user.time_of_day_data())
		kmcl = KMeansClustering(tod_data)
		time_clusters = kmcl.getclusters(10)
		timeslots = format_time_clusters(time_clusters)
		
		geo_data = request.user.geo_data()
		if not user None:
			geo_data.extend(user.geo_data())
		kmcl = KMeansClustering(geo_data)
		geo_clusters = kmcl.getclusters(20)
		areas = format_geo_clusters(ge_clusters)
		
		#todo: kmeans is parallelizable, so I could use MapReduce
		#todo: move this to an ajax call
		
		return template(
			'home', 
			user=request.user, 
			timeslots=timeslots, 
			areas=areas,
			most=most
		)
def format_time_clusters(clusters):
	# format tod groups
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
	
	return sorted(groups, key=lambda k: k['tod_min'])
	
def format_geo_clusters(clusters):
	# format tod groups
	areas=[]
	most=dict(
		north=None,
		south=None,
		east=None,
		west=None
	)
	for cl in clusters:
		
		lat_max=max([i[0] for i in cl])
		if not most['north'] or lat_max > most['north']:
			most['north'] = lat_max
			
		lat_min=min([i[0] for i in cl])
		if not most['south'] or lat_min < most['south']:
			most['south'] = lat_min
		
		lng_max=max([i[1] for i in cl])
		if not most['east'] or lng_max > most['east']:
			most['east'] = lng_max
			
		lng_min=min([i[1] for i in cl])
		if not most['west'] or lng_min < most['west']:
			most['west'] = lng_min
			
		areas.append(dict(
			len=len(cl),
			percent=len(geo_data)/len(cl)/100,
			opacity=float(len(geo_data))/100.0/float(len(cl)),
			avg_lat=sum([i[0] for i in cl])/len(cl),
			avg_lng=sum([i[1] for i in cl])/len(cl),
			lat_max=lat_max,
			lat_min=lat_min,
			lat_mid=lat_max-(lat_max-lat_min) / 2,
			lng_max=lng_max,
			lng_min=lng_min,
			lng_mid=lng_max-(lng_max-lng_min) / 2,
			radius=(lat_max - lat_min + lng_max - lng_min) / 2
		))
	
	return sorted(areas, key=lambda k: k['percent'])

@get('/callback')
def auth():
	"""Sets an access_token in a secure session cookie"""
	code = request.query.code
	auth = 'https://foursquare.com/oauth2/access_token'
	params = dict(
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		grant_type='authorization_code',
		redirect_uri=REDIRECT_URI,
		code=code
	)
	auth_says = fetch('%s?%s'%(auth, urlencode(params)))
	auth_response = json.loads(auth_says.content)
	if 'access_token' in auth_response:
		oauth_token=auth_response['access_token']
		response.set_cookie('user', oauth_token, secret=CLIENT_SECRET)
		logging.info('new oauth_token:%s'%oauth_token)
		redirect('/')
	else:
		logging.error(auth_response)
		abort()

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
