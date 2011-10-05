from google.appengine.ext import webapp
from gaesessions import get_current_session
from google.appengine.ext.webapp import util, template
from libs import facebook
from models import User


class Home(webapp.RequestHandler):
	def get(self):
		user = User.is_logged(self)
		is_home = True
		if user:
			self.redirect('/explore')
		self.response.out.write(template.render('templates/landing.html', locals()))