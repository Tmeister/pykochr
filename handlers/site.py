from google.appengine.ext import webapp
from gaesessions import get_current_session
from google.appengine.ext.webapp import util, template

class Home(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		if session.has_key('user'):
		    user = session['user']
		    self.redirect('/explore')

		self.response.out.write(template.render('templates/home.html', locals()))