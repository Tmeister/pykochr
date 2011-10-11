from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
import os
from models import (User)

class BaseHandler(webapp.RequestHandler):
	def error(self, code):
		user = User.is_logged(self)
		super(BaseHandler, self).error(code)
		if code == 404:
			self.response.out.write(template.render('templates/404.html', locals()))