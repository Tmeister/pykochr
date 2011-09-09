from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db

from google.appengine.api import mail
from google.appengine.api import images


from django.utils import simplejson
from django.core.validators import email_re
from django.contrib.humanize.templatetags.humanize import intcomma

from gaesessions import get_current_session
from models import (User, Koch, Ingredient, Direction, Tag, Photo, Like)

import helpers


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
		slug 		= helpers.sluglify( name )


		koch = Koch(
						author		= user, 
						title		= name, 
						notes		= notes,
						prep_time	= prep,
						cook_time	= cook,
						level		= level,
						private 	= private,
						slug 		= slug					)
		koch.put()

		for ingredient in ingredients:
			Ingredient(koch=koch, value=ingredient).put()

		for direction in directions:
			Direction(koch=koch, value=direction).put()
		
		for tag in tags:
			Tag(koch=koch, value=tag).put()

		if self.request.get('photo'):
			try:
				img_data = self.request.POST.get('photo').file.read()
				img = images.Image(img_data)
				img.im_feeling_lucky()
				png_data = img.execute_transforms(images.PNG)
				img.resize(450)
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
		session = get_current_session()
		user = False
		if session.has_key('user'):
			user = session['user']

		author = User.all().filter('nickname =', cook.lower()).fetch(1)
		if len( author ) == 0:
			self.redirect('/')
		
		author = author[0]
		tmp_kochs = Koch.all().filter('author =', author).order('-created')
		kochs = []

		for koch in tmp_kochs:
			if user:
				alreadylike = Like.alreadylike( koch, user )
			else:
				alreadylike = False

			kochs.append({
					'author'		: author,
					'koch'			: koch, 
					'tags'			: Tag.all().filter('koch =', koch),
					'image'			: Photo.all().filter('koch =', koch).fetch(1),
					'humanlikes'	: intcomma( int( koch.likes) ),
					'alreadylike'	: alreadylike
				})
		
		self.response.out.write(template.render('templates/list_kochs.html', locals()))

class Detail(webapp.RequestHandler):
	"""docstring for Detail"""
	def get(self, slug):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']

		query = Koch.all().filter( 'slug =', slug).fetch(1)
		if len( query ):
			koch = query[0];
			ingredients	= Ingredient.all().filter('koch =', koch)
			directions	= Direction.all().filter('koch =', koch)
			tags		= Tag.all().filter('koch =', koch)
			image		= Photo.all().filter('koch =', koch).fetch(1)
			if len(image):
				image = image[0]
			
			self.response.out.write(template.render('templates/details_koch.html', locals()))
		else:
			print 'nononono'


class UpVote(webapp.RequestHandler):
	"""docstring for vote"""
	def post(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
		else:
			self.response.out.write( simplejson.dumps({'status':'error', 'message':'Please login to vote.'}) )
			return

		key = self.request.get('key')
		koch = db.get(key)
		vote = Like.all().filter('koch =', koch).filter('user =', user).fetch(1)
		if len( vote ) :
			self.response.out.write( simplejson.dumps({'status':'error', 'message':'Are you cheating?'}) )
			return

		votes = Like.up( koch, user )

		self.response.out.write( 
			simplejson.dumps(
				{	'status'	: 'success', 
					'message'	: 'up', 
					'votes'		:  votes
				}
			) 
		)

class DownVote(webapp.RequestHandler):
	"""docstring for DownVote"""
	def post(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
		else:
			self.response.out.write( simplejson.dumps({'status':'error', 'message':'Please login to vote.'}) )
			return
		
		key = self.request.get('key')
		koch = db.get(key)
		vote = Like.all().filter('koch =', koch).filter('user =', user).fetch(1)
		if len( vote ) :
			votes = vote[0].down()
			self.response.out.write( 
				simplejson.dumps(
					{	'status'	: 'success', 
						'message'	: 'down', 
						'votes'		:  votes
					}
				) 
			)
			return
		
		self.response.out.write( simplejson.dumps({'status':'success', 'message':'no like'}) )

		
		
		

class Image (webapp.RequestHandler):
  def get(self):
    koch = db.get(self.request.get("img_id"))
    image = Photo.all().filter('koch =', koch).fetch(1)
    image = image[0]
    if image.value:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(image.value)