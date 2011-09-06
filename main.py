from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from django.utils import simplejson
from models import *
from gaesessions import get_current_session

from handlers import (account, profile, koch)

class Home(webapp.RequestHandler):
    def get(self):
        #user = User( nickname='tmeister', password='321321321', email='tmeister@gmail.com' )
        #user.put()
        session = get_current_session()
        if session.has_key('user'):
            user = session['user']
        self.response.out.write(template.render('templates/home.html', locals()))

        

application = webapp.WSGIApplication(
                                        [
                                            ('/', Home),
                                            ('/ajax/register', account.Register),
                                            ('/ajax/login', account.Login),
                                            ('/logout', account.Logout),
                                            ('/profile', profile.Edit),
                                            ('/account', account.Overview),
                                            ('/create/save', koch.Save),
                                            ('/create', koch.Create),

                                        ],
                                        debug=True)

def main():
    run_wsgi_app(application)

if( __name__ ) == '__main__':
    main()

