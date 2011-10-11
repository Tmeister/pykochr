import base
from base import BaseHandler
from gaesessions import get_current_session
from google.appengine.ext.webapp import util, template
from libs import facebook
from models import User, Koch


class Home(BaseHandler):
	def get(self):
		user = User.is_logged(self)
		is_home = True
		if user:
			self.redirect('/explore')
		
		last_kochs = Koch.all().order('-created').fetch(5)
		self.response.out.write(template.render('templates/landing.html', locals()))