#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, logging, bottle, random
from bottle import request, response, redirect, get, abort, template
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch
from urllib import urlencode
from datetime import datetime
import simplejson as json
import time

from models import User, Checkin

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
@get('/user/<user_id>')
@get('/')
def home(user_id=None):
	request.user = User.current()
	if not request.user:
		return bottle.template('welcome', client_id=CLIENT_ID, redirect_uri=REDIRECT_URI)
	else:
		return template('profile', user=request.user)

@get('/callback')
def auth():
	"""Sets an access_token in a secure cookie"""
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

@get('/logout')
def logout():
	deauthenticate()
	
@get('/clusters')
def clusters():
	# load the user's clusters
	# load the other user's clusters
	# calculate the similarity between every cluster
	# sort by similarity
	# return json
	pass

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
