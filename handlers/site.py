import base
import helpers
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
		
		last_kochs = Koch.all().order('-created').fetch(3)
		fkoch = last_kochs[0]
		last_users = User.all().order('-created').fetch(12)
		users = []
		for user in last_users:
			if user.fb_profile_url:
				avatar = "https://graph.facebook.com/%s/picture" % (user.nickname)
			elif not user.usegravatar and user.avatar:
				avatar = "/avatar/?user_id=%s" %(user.key())
			else:
				avatar = helpers.get_gravatar( user.email, 90 )
			
			users.append({
				'nickname'	: user.nickname,
				'avatar'	: avatar 
			})

		self.response.out.write(template.render('templates/landing.html', locals()))