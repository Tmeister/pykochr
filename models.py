from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp, db
import hashlib
import keys


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
		


class Koch(db.Model):
	"""docstring for Koch"""

	LEVELS_CHOICES = (
		(u'easy', u'Easy'),
		(u'medium', u'Medium'),
		(u'advanced', u'Advanced')
	)

	STATUS_CHOICES = (
		(u'publish', u'Publish'),
		(u'draft', u'Draft'),
		(u'trash', u'Trash')
	)

	#author 		= db.ReferenceProperty(User, related_name='kochs', null=True	)
	title		= db.StringProperty(required=True)
	prep_time	= db.StringProperty(required=True)
	cook_time	= db.StringProperty(required=True)
	level		= db.StringProperty(choices=LEVELS_CHOICES)
	likes		= db.IntegerProperty(default=0)
	created		= db.DateTimeProperty(auto_now_add=True)
	status		= db.StringProperty(default='publish', choices=STATUS_CHOICES)
	private		= db.BooleanProperty(default=False);
	slug		= db.StringProperty()





class Photo(db.Model):
	"""docstring for Photos"""
	koch = db.ReferenceProperty(Koch)
	path = db.StringProperty(required=True)

class Ingredient(db.Model):
	"""docstring for Ingredients"""
	koch = db.ReferenceProperty(Koch)
	ingredient = db.StringProperty(required=True)

class Direction(db.Model):
	"""docstring for Directions"""
	koch = db.ReferenceProperty(Koch)
	directions = db.TextProperty(required=True)

class Tag(db.Model):
	"""docstring for Photos"""
	koch = db.ReferenceProperty(Koch)
	tag = db.StringProperty(required=True)
