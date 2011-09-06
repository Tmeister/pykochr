from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp import util, template
from google.appengine.api import images

from django.utils import simplejson
from django.core.validators import email_re

from gaesessions import get_current_session
from models import (User, Koch, Ingredient, Direction, Tag, Photo)


class Create(webapp.RequestHandler):
	"""docstring for Create"""
	def get(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
			self.response.out.write(template.render('templates/new_koch.html', locals()))
		else:
			self.redirect('/')
		
	def post(self):
		session = get_current_session()
		if not session.has_key('user'):
			self.redirect('/')

		user = session['user']
		ingredients	= self.request.get_all('ingredients[]')
		directions	= self.request.get_all('directions[]')
		tags		= self.request.get_all('tags[]')
		name		= self.request.get('name')
		notes		= self.request.get('notes')

		koch = Koch(author=user, title=name, notes=notes)
		koch.put()

		img_data = self.request.POST.get('photo').file.read()
		try:
			img = images.Image(img_data)
			img.im_feeling_lucky()
			png_data = img.execute_transforms(images.PNG)
			img.resize(300, 300)
			thumb = img.execute_transforms(images.PNG)
			Photo(koch=koch, image=thumb).put()

		except images.BadImageError:
			pass
		except images.NotImageError:
			pass
		except images.LargeImageError:
			pass

		

		for ingredient in ingredients:
			Ingredient(koch=koch, ingredient=ingredient).put()

		for direction in directions:
			Direction(koch=koch, direction=direction).put()
		
		for tag in tags:
			Tag(koch=koch, tag=tag).put()
		
		self.redirect('/')
	