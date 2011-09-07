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
		prep 		= self.request.get('prep_time')
		cook 		= self.request.get('cook_time')
		level 		= self.request.get('level')
		private 	= True if self.request.get('private') == "1" else False

		koch = Koch(
						author		= user, 
						title		= name, 
						notes		= notes,
						prep_time	= prep,
						cook_time	= cook,
						level		= level,
						private 	= private
					)
		koch.put()

		for ingredient in ingredients:
			Ingredient(koch=koch, value=ingredient).put()

		for direction in directions:
			Direction(koch=koch, value=direction).put()
		
		for tag in tags:
			Tag(koch=koch, value=tag).put()

		if len(self.request.POST.get('photo')):
			try:
				img_data = self.request.POST.get('photo').file.read()
				img = images.Image(img_data)
				img.im_feeling_lucky()
				png_data = img.execute_transforms(images.PNG)
				img.resize(300, 300)
				thumb = img.execute_transforms(images.PNG)
				Photo(koch=koch, value=thumb).put()

			except images.BadImageError:
				pass
			except images.NotImageError:
				pass
			except images.LargeImageError:
				pass

		self.redirect('/')

class List(webapp.RequestHandler):
	"""docstring for MyKochs"""
	def get(self, cook):
		user = User.all().filter('nickname =', cook.lower()).fetch(1)
		if len( user ) == 0:
			self.redirect('/')
		
		user = user[0]
		tmp_kochs = Koch.all().filter('author =', user)
		kochs = []

		for koch in tmp_kochs:
			ingredients	= Ingredient.all().filter('koch =', koch)
			directions	= Direction.all().filter('koch =', koch)
			tags		= Tag.all().filter('koch =', koch)
			images		= Photo.all().filter('koch =', koch)
			kochs.append({
					'author'		: user,
					'koch'			: koch, 
					'ingredients'	: Ingredient.all().filter('koch =', koch), 
					'directions'	: Direction.all().filter('koch =', koch), 
					'tags'			: Tag.all().filter('koch =', koch),
					'images'		: Photo.all().filter('koch =', koch)
				})
		self.response.out.write(template.render('templates/list_kochs.html', locals()))
