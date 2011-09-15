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
        session = get_current_session()
        if session.has_key('user'):
            user = session['user']

        loop = range(243)
        self.response.out.write(template.render('templates/home.html', locals()))

        

application = webapp.WSGIApplication(
                [
                    ('/', Home),
                    ('/ajax/register'           , account.Register),
                    ('/ajax/login'              , account.Login),
                    ('/avatar/'                 , account.Avatar),
                    ('/account/change-avatar'   , account.SaveAvatar),
                    ('/logout'                  , account.Logout),
                    ('/profile'                 , account.Edit),
                    ('/account'                 , account.Overview),
                    ('/ajax/follow'             , account.Follow),
                    ('/ajax/unfollow'           , account.Unfollow),
                    ('/ajax/up-vote'            , koch.UpVote),
                    ('/ajax/down-vote'          , koch.DownVote),
                    ('/create'                  , koch.Create),
                    ('/cook/(.+)'               , koch.ListByAuthor),
                    ('/tag/(.+)'                , koch.ListByTag),
                    ('/explore'                 , koch.ListByDate),
                    ('/details/(.+)'            , koch.Detail),
                    ('/image/'                  , koch.Image),
                    
                ],
                debug=True)

def main():
    run_wsgi_app(application)

if( __name__ ) == '__main__':
    main()

