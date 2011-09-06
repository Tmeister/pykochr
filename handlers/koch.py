from google.appengine.ext import webapp
from django.utils import simplejson
from django.core.validators import email_re
from google.appengine.api import mail
from gaesessions import get_current_session
from models import (User, Koch, Ingredient, Direction, Tag)
from google.appengine.ext.webapp import util, template

class Create(webapp.RequestHandler):
	"""docstring for Create"""
	def get(self):
		session = get_current_session()
		if session.has_key('user'):
			user = session['user']
			self.response.out.write(template.render('templates/new_koch.html', locals()))
		else:
			self.redirect('/')
	
class Save(webapp.RequestHandler):
	"""docstring for Save"""
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

		print self.request.get('photos')
		return
		koch = Koch(author=user, title=name, notes=notes)
		koch.put()

		for ingredient in ingredients:
			ingr = Ingredient(koch=koch, ingredient=ingredient)
			ingr.put()

		for direction in directions:
			dire = Direction(koch=koch, direction=direction)
			dire.put()
		
		for tag in tags:
			tgs = Tag(koch=koch, tag=tag)
			tgs.put()
		
		self.response.out.write( simplejson.dumps({'status':'success', 'message':'Saved'}) )