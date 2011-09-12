from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp, db
import hashlib
import keys
from gaesessions import get_current_session


class User(db.Model):
	nickname            = db.StringProperty(required=True)
	password            = db.StringProperty(required=True)
	created             = db.DateTimeProperty(auto_now_add=True)
	about               = db.TextProperty(required=False)
	location            = db.StringProperty(required=False, default="")
	twitter             = db.StringProperty(required=False, default="")
	email               = db.EmailProperty(required=False)
	admin               = db.BooleanProperty(default=False)
	active				= db.BooleanProperty(default=False)
	avatar				= db.StringProperty(required=False, default="")
	firstname			= db.StringProperty(required=False, default="")
	lastname			= db.StringProperty(required=False, default="")

	@staticmethod
	def is_nickname_exists(user):
		return True if User.all().filter( 'nickname =', user.lower() ).count() > 0 else False

	@staticmethod
	def is_email_exists(email):
		return True if User.all().filter( 'email =', email ).count() > 0 else False
	
	@staticmethod
	def slow_hash(password, iterations=1000):
		h = hashlib.sha1()
		h.update(unicode(password).encode("utf-8"))
		h.update(keys.salt_key)
		for x in range(iterations):
		  h.update(h.digest())
		return h.hexdigest()
	
	@staticmethod
	def is_logged():
		session = get_current_session()
		if session.has_key('user'):
			return session['user']
		else:
			return False


class Koch(db.Model):
	"""docstring for Koch"""

	author 		= db.ReferenceProperty(User,required=True)
	title		= db.StringProperty(required=True)
	prep_time	= db.StringProperty(required=False)
	cook_time	= db.StringProperty(required=False)
	level		= db.StringProperty(default='easy')
	likes		= db.IntegerProperty(default=0)
	created		= db.DateTimeProperty(auto_now_add=True)
	status		= db.StringProperty(default='publish')
	private		= db.BooleanProperty(default=False)
	slug		= db.StringProperty(required=True)
	notes		= db.TextProperty()
	tags 		= db.StringListProperty()
	ingredients	= db.StringListProperty()
	directions  = db.StringListProperty()
	photo 		= db.BlobProperty()

class Tag(db.Model):
	"""docstring for Tag"""
	name = db.StringProperty(required=True)
	counter = db.IntegerProperty(default=1)

	@staticmethod
	def up(name):
		tag = Tag.all().filter('name =', name).fetch(1)
		if len(tag) == 1:
			tag = tag[0]
			tag.counter += 1	
		else:
			tag = Tag(name=name)

		tag.put()

class Like(db.Model):
	"""docstring for Likes"""
	koch = db.ReferenceProperty(Koch)
	user = db.ReferenceProperty(User)
	created = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def up(koch, user):
		upvote = Like( koch = koch, user = user )
		upvote.put()
		koch.likes += 1
		koch.put()
		return koch.likes
	
	def down(self):
		self.koch.likes -= 1
		self.koch.put()
		self.delete()
		return self.koch.likes
	
	@staticmethod
	def alreadylike(koch, user):
		like = Like.all().filter('koch =', koch).filter('user =', user).fetch(1)
		return True if len( like ) else False

	
		