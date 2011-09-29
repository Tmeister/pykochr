from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from django.utils import simplejson
from models import *
from gaesessions import get_current_session

from handlers import (account, profile, koch, site)

application = webapp.WSGIApplication(
                [
                    ('/'                        , site.Home),
                    ('/ajax/register'           , account.Register),
                    ('/ajax/login'              , account.Login),
                    ('/login/facebook'          , account.Facebook),
                    ('/avatar/'                 , account.Avatar),
                    ('/account/change-avatar'   , account.SaveAvatar),
                    ('/logout'                  , account.Logout),
                    ('/profile'                 , account.Edit),
                    ('/account'                 , account.Overview),
                    ('/ajax/follow'             , account.Follow),
                    ('/ajax/unfollow'           , account.Unfollow),
                    ('/followers/(.+)'          , account.Followers), 
                    ('/following/(.+)'          , account.Following), 
                    ('/ajax/up-vote'            , koch.UpVote),
                    ('/ajax/down-vote'          , koch.DownVote),
                    ('/create'                  , koch.Create),
                    ('/cook/(.+)'               , koch.ListByAuthor),
                    ('/tag/(.+)'                , koch.ListByTag),
                    ('/explore'                 , koch.ListByDate),
                    ('/details/(.+)'            , koch.Detail),
                    ('/image/'                  , koch.Image),
                    ('/edit/(.+)'               , koch.Edit),
                ],
                debug=True)

def main():
    run_wsgi_app(application)

if( __name__ ) == '__main__':
    main()

