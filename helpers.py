import htmlentitydefs, re
import random
import urllib, hashlib
import datetime
import os


from models import (User, Koch, Like, Friendship )
from django.contrib.humanize.templatetags.humanize import intcomma

def sluglify(text, separator = "-"):
  ret = ""
  for c in text.lower():
    try:
      ret += htmlentitydefs.codepoint2name[ord(c)]
    except:
      ret += c
 
  ret = re.sub("([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)", r"\1", ret)
  ret = re.sub("\W", " ", ret)
  ret = re.sub(" +", separator, ret)
 
  return ret.strip()

def paginate(entities, page=0, per_page=10):
  PAGESIZE = per_page
  max_results = 2000 
  max_pages = (max_results - PAGESIZE) / PAGESIZE 
  start = page*PAGESIZE   
  entities = entities.fetch(PAGESIZE+1, start)
  more_entities = len(entities) > PAGESIZE   
  prev_page = None   
  if page:
    prev_page = str(page - 1)   

  next_page = None   
  if more_entities:   
    next_page = str(page + 1)   
    
  return entities[:PAGESIZE], next_page, prev_page

def get_kochs_data(entities, author=None):
  kochs = []
  user = User.is_logged()
  for koch in entities:
    if user:
      alreadylike = Like.alreadylike( koch, user )
    else:
      alreadylike = False

    kochs.append({
        'koch'      : koch,
        'humanlikes'  : intcomma( int( koch.likes) ),
        'alreadylike' : alreadylike,
      })

  return kochs

def get_followers_data(entities):
  friends = []
  user  = User.is_logged()
  for friend in entities:
    if not friend.fan.usegravatar and friend.fan.avatar:
      avatar = "/avatar/?user_id=%s" %(friend.fan.key())
    else:
      avatar = get_gravatar( friend.fan.email )  

    friendship = False
    if user:
      friendship = Friendship.alreadyfollow( friend.fan, user )
     
    friends.append({
      'fan': friend.fan,
      'avatar' : avatar,
      'friend' : friendship
    })
  return friends

def get_following_data(entities):
  friends = []
  user  = User.is_logged()
  for friend in entities:
    if not friend.star.usegravatar and friend.star.avatar:
      avatar = "/avatar/?user_id=%s" %(friend.star.key())
    else:
      avatar = get_gravatar( friend.star.email )  

    friendship = False
    if user:
      friendship = Friendship.alreadyfollow( user, friend.star ) 
     
    friends.append({
      'fan': friend.star,
      'avatar' : avatar,
      'friend' : friendship
    })
  return friends


def get_gravatar(email, size=90):
  if not email:
    email =""
  default = "http://localhost:8080/static/images/chef-thumb.png"
  gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
  gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
  return gravatar_url

def random_string(wordLen=3):
  word = ''
  for i in range(wordLen):
    word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
  return word
