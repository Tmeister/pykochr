from google.appengine.ext import webapp
from django.utils import simplejson
from django.core.validators import email_re
from google.appengine.api import mail
from gaesessions import get_current_session
from models import User


class Register(webapp.RequestHandler):
    def post(self):
        session = get_current_session()
        username = self.request.get('username')
        email    = self.request.get('email')
        passwd   = self.request.get('password')

        if len (username.strip()) < 3:
            return self._send_error('El user debe ser de almenos 3')

        if not email_re.match(email):
            return self._send_error('Not a valid email')

        if len (passwd.strip()) < 5:
            return self._send_error('El password debe ser de almenos 5 caracteres')

        if User.is_nickname_exists( username ):
            return self._send_error('El user ya esta tomado')
        
        if User.is_email_exists(email):
            return self._send_error('El email ya esta tomado')

        user = User( nickname=username, email=email, password= User.slow_hash(passwd) );
        user.put()

        if session.is_active():
            session.terminate()

        session.regenerate_id()
        session['user'] = user

        #TODO SEND WELCOME EMAIL
        #mail.send_mail(sender="no-reply@example.com",
        #      to="noone@tmeister.net",
        #      subject="Your account has been approved",
        #      body="test")

        self.response.out.write( simplejson.dumps({'status':'success', 'message':'Success'}) )




    def _send_error(self, message):
        out = {'status':'error', 'message':message}
        self.response.out.write( simplejson.dumps(out) )

class Login(webapp.RequestHandler):
    """docstring for Login"""
    def post(self):
        session = get_current_session()
        username = self.request.get('username').lower()
        passwd   = self.request.get('passwd')
        passwd = User.slow_hash( passwd )

        user = User.all().filter('nickname =', username).filter('password =', passwd).fetch(1)
        
        if len(user) == 1:
            if session.is_active():
                session.terminate()
            
            session.regenerate_id()
            session['user'] = user[0]
            self.response.out.write( simplejson.dumps({'status':'success'}) )
        else:
            self.response.out.write( simplejson.dumps({'status':'error', 'message':'Login or password incorrect'}) )




class Logout(webapp.RequestHandler):
    """docstring for Logout"""
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        
        session.regenerate_id()
        self.redirect('/')