from google.appengine.ext import webapp
from django.utils import simplejson
from django.core.validators import email_re
from google.appengine.api import mail
from gaesessions import get_current_session
from models import User
from google.appengine.ext.webapp import util, template


class Register(webapp.RequestHandler):
    def post(self):
        session = get_current_session()
        username = self.request.get('username').lower()
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

class Overview(webapp.RequestHandler):
    """docstring for Overview"""
    def get(self):
        session = get_current_session()
        if session.has_key('user'):
            user            = session['user']
            profile_updated = session.pop('profile_updated')
            profile_fail = session.pop('profile_fail')
            profile_errors = session.pop('profile_errors')
            self.response.out.write(template.render('templates/profile.html', locals()))
        else:
            self.redirect('/')

    def post(self):
        session = get_current_session()
        if session.has_key('user'):
            user = session['user']

        r = self.request
        email       = r.get('email')
        pass1       = r.get('passwd')
        pass2       = r.get('re_passwd')
        fname       = r.get('firstname')
        lname       = r.get('lastname')
        about       = r.get('about')
        twitter     = r.get('twitter')
        location    = r.get('location')
        error = []

        if len(pass1):
            if len(pass2):
                if len(pass2):
                    if pass1 == pass2:
                        if len(pass1.strip()) >= 5:
                            user.password = User.slow_hash( pass1 )
                        else:
                            error.append('The password must be at least 6 characters')
                    else:
                        error.append('Password do not match.')
        

        if email_re.match(email):
            if email != user.email:
                if User.is_email_exists(email):
                    error.append('El email ya esta tomado')
                else:
                    user.email = email
        else:
            error.append('Not a valid email')

        if len(error):
            session['profile_fail'] = True;
            session['profile_errors'] = error;
        else:
            user.firstname  = fname
            user.lastname   = lname
            user.about      = about
            user.twitter    = twitter
            user.location   = location
            user.put()
            session['profile_updated'] = True;
        
        self.redirect('/account')