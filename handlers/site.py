import base
import helpers
import random
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
		
		last_kochs = Koch.all().order('-created').fetch(3,1)
		fkoch = Koch.all().order('-created').fetch(1)
		fkoch = fkoch[0]
		last_users = User.all().order('-created').fetch(12)
		users_grid = []
		random_id = random.randrange(1,4)
		for user_home in last_users:
			if user_home.fb_profile_url:
				avatar = "https://graph.facebook.com/%s/picture" % (user_home.nickname)
			elif not user_home.usegravatar and user_home.avatar:
				avatar = "/avatar/?user_id=%s" %(user_home.key())
			else:
				avatar = helpers.get_gravatar( user_home.email, 90 )
			
			users_grid.append({
				'nickname'	: user_home.nickname,
				'avatar'	: avatar 
			})

		self.response.out.write(template.render('templates/landing.html', locals()))