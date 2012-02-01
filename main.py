#!/usr/bin/env python
#
# Copyright 2012 Jesse Hattabaugh
#

import os, bottle
from google.appengine.ext.webapp import util

bottle.debug(True)

@bottle.get('/')
@bottle.view('main')
def index():
  return dict()

def main():
  app = bottle.default_app()
  util.run_wsgi_app(app)

if __name__ == "__main__":
  main()
