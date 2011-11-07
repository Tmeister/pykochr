import base, helpers, time
from base import BaseHandler
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db

from google.appengine.api import mail
from google.appengine.api import images


from django.utils import simplejson
from django.core.validators import email_re
from django.contrib.humanize.templatetags.humanize import intcomma

from gaesessions import get_current_session
from models import (User, Koch, Like, Tag, Friendship)


class Create(BaseHandler):
	"""docstring for Create"""
	def get(self):
		user = User.is_logged(self)
		if user:
			current = "add"
			self.response.out.write(template.render('templates/new_koch.html', locals()))
		else:
			self.redirect('/')
		
	def post(self):
		user = User.is_logged(self)
		if not user:
			self.redirect('/')

		key 		= self.request.get('edit')
		tags        = [a.lower() for a in self.request.get_all('tags[]')]
		user        = user
		ingredients = self.request.get_all('ingredients[]')
		directions  = self.request.get_all('directions[]')
		tags        = tags
		name        = self.request.get('name')
		notes       = self.request.get('notes')
		prep        = self.request.get('prep_time')
		cook        = self.request.get('cook_time')
		level       = self.request.get('level')
		private     = True if self.request.get('private') == "1" else False
		slug        = helpers.sluglify( name )
		thumb       = None
		tinythumb   = None

		slug_exists = Koch.all().filter('slug =', slug).fetch(1)

		if len ( slug_exists ) == 1:
			#alreadyexists
			slug = "%s-%s" % (slug, helpers.random_string())

		if self.request.get('photo'):
			try:
				img_data = self.request.POST.get('photo').file.read()

				img = images.Image(img_data)
				img.im_feeling_lucky()
				png_data = img.execute_transforms(images.JPEG)
				img.resize(620,420)
				thumb = img.execute_transforms(images.JPEG)

				thmb = images.Image(img_data)
				thmb.im_feeling_lucky()
				png_data = thmb.execute_transforms(images.JPEG)
				thmb.resize(0, 80)
				tinythumb = thmb.execute_transforms(images.JPEG)				

			except images.BadImageError:
				pass
			except images.NotImageError:
				pass
			except images.LargeImageError:
				pass

		if key:
			koch       = Koch.get( key )
			koch.title = name 
		else:
			koch = Koch(slug=slug, title=name, author=user)
		
		koch.notes       = notes
		koch.prep_time   = prep
		koch.cook_time   = cook
		koch.level       = level
		koch.private     = private
		koch.tags        = tags
		koch.ingredients = ingredients
		koch.directions  = directions
					
		
		if thumb is not None:
			koch.photo = thumb
			koch.thumb = tinythumb
		
		for tag in tags:
			Tag.up(tag)

		if key:
			user.recipes += 1
			user.put() 
		
		koch.put()
		self.redirect('/cook/%s' % (user.nickname))

class ListByAuthor(BaseHandler):
	"""docstring for MyKochs"""
	def get(self, cook):
		user = User.is_logged(self)
		author = User.all().filter('nickname =', cook.lower()).fetch(1)

		if not len( author ):
			self.error(404)
			return

		author = author[0]
			
		if user:
			alreadyfollow = Friendship.alreadyfollow( user, author  )
		
		title = "%s's CookBook" %(author.nickname)
		subhead = "Discover what %s has shared"  % (author.nickname)
		author_recipes_count = Koch.all().filter('author =', author).count();
		

		if author.fb_profile_url:
			avatar = "https://graph.facebook.com/%s/picture" % (author.nickname)
		elif not author.usegravatar and author.avatar:
			avatar = "/avatar/?user_id=%s" %(author.key())
		else:
			avatar = helpers.get_gravatar( author.email, 90 )
		
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().filter('author =', author).order('-created'), page ) 
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_kochs = Koch.all().filter('author =', author).order('-created').fetch(5);
		last_from_all = Koch.get_random()
		current = "explore"
		self.response.out.write(template.render('templates/list_kochs.html', locals()))
		

class ListByTag(BaseHandler):
	"""docstring for ListByTag"""
	def get(self, tag):
		user = User.is_logged(self)
		tag = helpers.sluglify(tag)
		tag = tag.replace('-', ' ')
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
		title = "Explore %s" %(tag)
		subhead = "You can find hidden treasures."
		current = "explore"
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().filter('tags =', tag).order('-created'), page ) 
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_from_all = Koch.get_random()
		self.response.out.write(template.render('templates/list_kochs.html', locals()))

class ListByDate(BaseHandler):
	"""docstring for ListByDate"""
	def get(self):
		user = User.is_logged(self)
		page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
		title = "Explore Recipes"
		subtitle = ""
		subhead = "You can find hidden treasures."
		current = "explore"
  		tmp_kochs, next_page, prev_page = helpers.paginate( Koch.all().order('-created'), page )
		kochs = helpers.get_kochs_data(tmp_kochs)
		last_from_all = Koch.get_random()
		self.response.out.write(template.render('templates/list_kochs.html', locals()))		
		

class Detail(BaseHandler):
	"""docstring for Detail"""
	def get(self, slug):
		user = User.is_logged(self)
		query = Koch.all().filter( 'slug =', slug).fetch(1)
		if len( query ):
			koch = query[0];
			alreadylike = False
			alreadyfollow = False
			likesusers = []
			koch.views += 1
			koch.put()
			
			author = koch.author
			
			avatar = helpers.get_gravatar( author.email, 90 )
			
			author_recipes_count = Koch.all().filter('author =', author).count();
			for like in Like.all().filter( 'koch =', koch ):
				if like.user.fb_profile_url:
					lavatar = "https://graph.facebook.com/%s/picture" % (like.user.nickname)
				elif not like.user.usegravatar and like.user.avatar:
					lavatar = "/avatar/?user_id=%s" %(like.user.key())
				else:
					lavatar = helpers.get_gravatar( like.user.email, 90 )

				likesusers.append({
					'nickname' : like.user.nickname,
					'avatar'   : lavatar
				})

			if user:
				alreadylike = Like.alreadylike( koch, user )
				alreadyfollow = Friendship.alreadyfollow( user, author  )
				is_owner = True if user.key() == author.key() else False

			if author.fb_profile_url:
				avatar = "https://graph.facebook.com/%s/picture" % (author.nickname)
			elif not author.usegravatar and author.avatar:
				avatar = "/avatar/?user_id=%s" %(author.key())
			else:
				avatar = helpers.get_gravatar( author.email, 90 )

			last_kochs = Koch.all().filter('author =', author).order('-created').fetch(5);
			last_from_all = Koch.get_random()
			current = "explore"

			humanlikes = intcomma( int( koch.likes) )

			self.response.out.write(template.render('templates/details_koch.html', locals()))
		else:
			self.error(404)
		
class Edit(BaseHandler):
	"""docstring for Edit"""
	def get(self, key):
		user = User.is_logged(self)
		if not user:
			self.error(404)
			return

		try:
			koch = Koch.get( key )
		except db.BadKeyError:
			self.error(404)
			return	
	
		is_editing = True
		self.response.out.write( template.render('templates/new_koch.html', locals()))
		



class UpVote(BaseHandler):
	"""docstring for vote"""
	def post(self):
		user = User.is_logged(self)
		if not user:
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

class DownVote(BaseHandler):
	"""docstring for DownVote"""
	def post(self):
		user = User.is_logged(self)
		if not user:
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

class Images (BaseHandler):
	def get(self):
		koch = db.get(self.request.get("img_id"))
		if koch:
			self.response.headers['Content-Type'] = "image/jpeg"
			size = self.request.get("size")
			if size == 'thumb':
				img = koch.photo
				thumb = images.Image(img)
				thumb.resize(0, 80)
				self.response.out.write( thumb.execute_transforms(images.JPEG) )
			elif size == 'thumb-home':
				img = koch.photo
				thumb = images.Image(img)
				thumb.resize(0, 70)
				self.response.out.write( thumb.execute_transforms(images.JPEG) )
			elif size == "slider-home":
				img = koch.photo
				thumb = images.Image(img)
				thumb.resize(610)
				self.response.out.write( thumb.execute_transforms(images.JPEG) )
			else :
				img = koch.photo
				thumb = images.Image(img)
				thumb.resize(450)
				self.response.out.write( thumb.execute_transforms(images.JPEG) )