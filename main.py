#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, bottle
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import fetch

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	import dev_settings as settings
	bottle.debug(True)
else: #prod
	import prod_settings as settings

@bottle.get('/')
@bottle.view('main')
def home():
	return dict(client_id=settings.CLIENT_ID,
		redirect_uri=settings.REDIRECT_URI)
	
@bottle.route('/callback')
@bottle.view('main')
def after_auth():
	code = bottle.request.query.code
	access_token_url='https://foursquare.com/oauth2/access_token?client_id='+CLIENT_ID+'&client_secret='+CLIENT_SECRET+'&grant_type=authorization_code&redirect_uri='+REDIRECT_URI+'&code='+code
	result=fetch(access_token_url)
	return dict(debug=result.content)

def main():
	app = bottle.default_app()
	util.run_wsgi_app(app)

if __name__ == "__main__":
	main()
