import helpers
import time

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db

from google.appengine.api import mail
from google.appengine.api import images


from django.utils import simplejson
from django.core.validators import email_re
from django.contrib.humanize.templatetags.humanize import intcomma

from gaesessions import get_current_session
from models import (User, Koch, Like, Tag)


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

		tags =  [a.lower() for a in self.request.get_all('tags[]')]

		user = session['user']
		ingredients	= self.request.get_all('ingredients[]')
		directions	= self.request.get_all('directions[]')
		tags		= tags
		name		= self.request.get('name')
		notes		= self.request.get('notes')
		prep 		= self.request.get('prep_time')
		cook 		= self.request.get('cook_time')
		level 		= self.request.get('level')
		private 	= True if self.request.get('private') == "1" else False
		slug 		= helpers.sluglify( name )
		thumb 		= None
		tinythumb 	= None



		if self.request.get('photo'):
			try:
				img_data = self.request.POST.get('photo').file.read()

				img = images.Image(img_data)
				img.im_feeling_lucky()
				png_data = img.execute_transforms(images.PNG)
				img.resize(450)
				thumb = img.execute_transforms(images.PNG)

				thmb = images.Image(img_data)
				thmb.im_feeling_lucky()
				png_data = thmb.execute_transforms(images.PNG)
				thmb.resize(80, 80)
				tinythumb = thmb.execute_transforms(images.PNG)				

			except images.BadImageError:
				pass
			except images.NotImageError:
				pass
			except images.LargeImageError:
				pass

		koch = Koch(
						author		= user, 
						title		= name, 
						notes		= notes,
						prep_time	= prep,
						cook_time	= cook,
						level		= level,
						private 	= private,
						slug 		= slug,
						tags 		= tags,
						ingredients = ingredients,
						directions  = directions
					)
		
		if thumb is not None:
			koch.photo = thumb
			koch.thumb = tinythumb
		
		for tag in tags:
			Tag.up(tag)

		koch.put()
		self.redirect('/')

class ListByAuthor(webapp.RequestHandler):
	"""docstring for MyKochs"""
	def get(self, cook):
		user = User.is_logged()
		author = User.all().filter('nickname =', cook.lower()).fetch(1)
		if len( author ) == 0:
			self.redirect('/')

		author = author[0]
		title = "%s's CookBook" %(author.nickname)
		subhead = "Another main text..."
		author_recipes_count = Koch.all().filter('author =', author).count();
		if not author.usegravatar and author.avatar:
			avatar = "/avatar/?user_id=%s" %(author.key())
		else:
			avatar = helpers.get_gravatar( author.email, 90 )
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().filter('author =', author).order('-created'), page ) 
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_kochs = Koch.all().filter('author =', author).fetch(5);
		last_from_all = Koch.all().fetch(5);
		self.response.out.write(template.render('templates/list_kochs.html', locals()))
		

class ListByTag(webapp.RequestHandler):
	"""docstring for ListByTag"""
	def get(self, tag):
		user = User.is_logged()
		tag = tag.replace('-', ' ')
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
		title = "Explore %s" %(tag)
		subhead = "Another main text..."
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().filter('tags =', tag).order('-created'), page ) 
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_from_all = Koch.all().fetch(5);
		self.response.out.write(template.render('templates/list_kochs.html', locals()))

class ListByDate(webapp.RequestHandler):
	"""docstring for ListByDate"""
	def get(self):
		user = User.is_logged()
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
		title = "Explore Recipes"
		subtitle = "Explore recipes from all cooks"
		subhead = "Another main text..."
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().order('-created'), page )
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_from_all = Koch.all().fetch(5);
		self.response.out.write(template.render('templates/list_kochs.html', locals()))		
		

class Detail(webapp.RequestHandler):
	"""docstring for Detail"""
	def get(self, slug):
		user = User.is_logged()
		query = Koch.all().filter( 'slug =', slug).fetch(1)
		if len( query ):
			koch = query[0];
			if user:
				alreadylike = Like.alreadylike( koch, user )
			else:
				alreadylike = False
			
			author = koch.author
			author_recipes_count = Koch.all().filter('author =', author).count();
			
			if not author.usegravatar and author.avatar:
				avatar = "/avatar/?user_id=%s" %(author.key())
			else:
				avatar = helpers.get_gravatar( author.email, 90 )

			last_kochs = Koch.all().filter('author =', author).fetch(5);
			last_from_all = Koch.all().fetch(5);

			humanlikes = intcomma( int( koch.likes) )
			self.response.out.write(template.render('templates/details_koch.html', locals()))
		else:
			print '404'


class UpVote(webapp.RequestHandler):
	"""docstring for vote"""
	def post(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
		else:
			self.response.out.write( simplejson.dumps({'status':'error', 'message':'In order to vote you must sign in.'}) )
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
			self.response.out.write( simplejson.dumps({'status':'error', 'message':'In order to vote you must sign in.'}) )
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
		
		self.response.out.write( simplejson.dumps({'status':'success', 'message':'An error occurred please contact the developer'}) )

class Image (webapp.RequestHandler):
	def get(self):
		koch = db.get(self.request.get("img_id"))
		if koch:
			self.response.headers['Content-Type'] = "image/png"
			if self.request.get("size") == 'thumb':
				self.response.out.write(koch.thumb)
			else:
				self.response.out.write(koch.photo)
