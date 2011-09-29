from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import mail
from google.appengine.api import images
from google.appengine.ext import db

from django.utils import simplejson
from django.core.validators import email_re

from gaesessions import get_current_session

from models import User, Friendship, Koch
from libs import Mailing, facebook
import helpers


class Register(webapp.RequestHandler):
    def post(self):
        session = get_current_session()
        username = self.request.get('username').lower()
        email    = self.request.get('email')
        passwd   = self.request.get('password')

        if len (username.strip()) < 3 or len (username.strip()) > 12:
            return self._send_error('The username must be between 3 and 12 chars')

        if not email_re.match(email):
            return self._send_error('Sorry, is not a valid email address')

        if len (passwd.strip()) < 6:
            return self._send_error('The password must be at least 6 chars')

        if User.is_nickname_exists( username ):
            return self._send_error('Sorry, that user is already taken')
        
        if User.is_email_exists(email):
            return self._send_error('Sorry, this email is already in use')

        user = User( nickname=username, email=email, password= User.slow_hash(passwd) );
        user.put()

        if session.is_active():
            session.terminate()

        session.regenerate_id()
        session['user'] = user

        body = 'Hello %s,<br/>Your account has been created and is ready to use.<br/><br/>Your login details are:<br/><br/>Username <strong>%s</strong><br/>Password <strong>%s</strong><br/><br/>Thanks and bon appetit!' %  ( username, username, passwd )

        mail =  Mailing.Notification()
        mail.send(email, 'Welcome to Kochster', body)

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
            self.response.out.write( simplejson.dumps({'status':'error', 'message':'Sorry, Login or password incorrect'}) )


class Logout(webapp.RequestHandler):
    """docstring for Logout"""
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        
        session.regenerate_id()
        self.redirect('/')

class SaveAvatar(webapp.RequestHandler):
    """docstring for Avatar"""
    def post(self):
        session = get_current_session()
        user = User.is_logged(self)
        if not user:
            self.redirect('/account')

        if self.request.get('photo'):
            try:
                img_data = self.request.POST.get('photo').file.read()
                img = images.Image(img_data)
                img.im_feeling_lucky()
                png_data = img.execute_transforms(images.PNG)
                img.resize(80, 80)
                thumb = img.execute_transforms(images.PNG)
                user.avatar = thumb
                user.usegravatar = False
                user.put()
                session['profile_updated'] = True;
                self.redirect('/account')


            except images.BadImageError:
                pass
            except images.NotImageError:
                pass
            except images.LargeImageError:
                pass
        else:
            session['profile_fail'] = True;
            session['profile_errors'] = ['Please select a image.'];
            self.redirect('/account')


class Overview(webapp.RequestHandler):
    """docstring for Overview"""
    def get(self):
        session = get_current_session()
        if session.has_key('user'):
            user            = session['user']
            profile_updated = session.pop('profile_updated')
            profile_fail    = session.pop('profile_fail')
            profile_errors  = session.pop('profile_errors')
            if not user.usegravatar and user.avatar:
                avatar = "/avatar/?user_id=%s" %(user.key())
            else:
                avatar = helpers.get_gravatar( user.email, 90 )
            
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
                            error.append('The password must be at least 6 chars')
                    else:
                        error.append('Password do not match.')
        

        if email_re.match(email):
            if email != user.email:
                if User.is_email_exists(email):
                    error.append('Sorry, this email is already in use')
                else:
                    user.email = email
        else:
            error.append('Sorry, is not a valid email address')

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

class Avatar (webapp.RequestHandler):
    def get(self):
        user = db.get(self.request.get("user_id"))
        if user:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(user.avatar)     


class Edit(webapp.RequestHandler):
    """docstring for Edit"""
    def get(self):
        session = get_current_session()
        if session.has_key('user'):
            user = session['user']
            self.response.out.write(template.render('templates/home.html', locals()))
        else:
            self.response.out.write('Nonono')
        
class Follow(webapp.RequestHandler):
    """docstring for Follow"""
    def post(self):
        fan = db.get( self.request.get('fan') )
        star = db.get( self.request.get('star') )
        already = Friendship.all().filter('fan =', fan).filter('star =', star).fetch(1)
        if fan and star and len( already ) == 0:
            follow = Friendship.follow( fan, star )
            if follow:
                self.response.out.write( 
                    simplejson.dumps(
                        {   
                            'status'    : 'success', 
                            'message'   : 'follow',
                            'star'      : star.nickname,
                            'star_key'  : self.request.get('star'),
                            'fan_key'   : self.request.get('fan'),
                            'star_followers' : follow.star.followers
                        }
                    ) 
                )
            else:
                self.response.out.write( 
                    simplejson.dumps(
                        {   
                            'status'    : 'error', 
                            'message'   : 'follow'
                        }
                    ) 
                )
           


class Unfollow(webapp.RequestHandler):
    """docstring for Unfollow"""
    def post(self):
        fan = db.get( self.request.get('fan') )
        star = db.get( self.request.get('star') )
        if fan and star:
            query = Friendship.all().filter('fan =', fan).filter('star =', star).fetch(1)
            if len( query ) == 1:
                follow = query[0]
                if follow:
                    follow.unfollow()
                    self.response.out.write( 
                        simplejson.dumps(
                            {   
                                'status'    : 'success', 
                                'message'   : 'unfollow',
                                'star'      : star.nickname,
                                'star_key'  : self.request.get('star'),
                                'fan_key'   : self.request.get('fan'),
                                'star_followers' : follow.star.followers
                            }
                        ) 
                    )
                else:
                    self.response.out.write( 
                        simplejson.dumps(
                            {   
                                'status'    : 'error', 
                                'message'   : 'unfollow'
                            }
                        ) 
                    ) 

class Followers(webapp.RequestHandler):
    """docstring for Followers"""
    def get(self, star):
        user = User.is_logged(self)
        query = User.all().filter('nickname =', star.lower()).fetch(1)
        if len( query ) == 1:
            star = query[0]
            title = "%s's followers" % ( star.nickname )
            subhead = "on Kochster"
            page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
            foll_tmp, next_page, prev_page = helpers.paginate( Friendship.all().filter('star =', star).order('-created'), page, 12 ) 
            followers = helpers.get_followers_data( foll_tmp )
            last_from_all = Koch.get_random()
            self.response.out.write(template.render('templates/followers.html', locals()))

class Following(webapp.RequestHandler):
    """docstring for Followers"""
    def get(self, star):
        user = User.is_logged(self)
        query = User.all().filter('nickname =', star.lower()).fetch(1)
        if len( query ) == 1:
            fan = query[0]
            title = "%s is following" % ( fan.nickname )
            subhead = "Favorites cooks"
            page = self.request.get_range('page', min_value=0, max_value=1000, default=0)
            foll_tmp, next_page, prev_page = helpers.paginate( Friendship.all().filter('fan =',  fan).order('-created'), page, 12 ) 
            followers = helpers.get_following_data( foll_tmp )
            last_from_all = Koch.get_random()
            self.response.out.write(template.render('templates/followers.html', locals()))

class Facebook(webapp.RequestHandler):
    """docstring for Facebook"""
    
    def get(self):
        fbcookie = facebook.get_user_from_cookie(self.request.cookies)
        if not fbcookie:
            self.redirect('/')
            return
        
        user = User.is_logged(self)
        graph = facebook.GraphAPI(fbcookie["access_token"])
        profile = graph.get_object("me")
        if not user:
            password = helpers.random_string(8)
            user = User(nickname = profile['username'], password = User.slow_hash(password));
            user.fb_access_token = fbcookie["access_token"]
            try: user.about = profile['bio'] 
            except: pass

            try: user.location = profile['location']['name'] 
            except: pass    

            try: user.firstname = profile['first_name'] 
            except: pass    

            try: user.lastname = profile['last_name'] 
            except: pass    

            try: user.fb_profile_url = profile['link']
            except: pass    

            try: user.fb_ui = profile['id']
            except: pass    

            user.put()

            session = get_current_session()
            session.regenerate_id()
            session['user'] = user
            self.redirect('/')
        else:
            if str(user.fb_ui) == str(profile['id']):
                self.redirect('/')
            else:
                #TODO
                #USUARIO CAMBIO DE ID?? o ESTA VINCULANDO A CUENTA EXISTENTE
                pass


        
                
