import base
from base import BaseHandler
from gaesessions import get_current_session
from google.appengine.ext.webapp import util, template
from models import User
from django.core.validators import email_re

class Edit(BaseHandler):
	"""docstring for Edit"""
	def get(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
			self.response.out.write(template.render('templates/home.html', locals()))
		else:
			self.response.out.write('Nonono')
		
		