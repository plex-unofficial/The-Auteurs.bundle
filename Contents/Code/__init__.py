import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *


PLUGIN_PREFIX = "/video/theauteurs"

FRONT_PAGE = "http://www.theauteurs.com/"
# view_format=expanded: meta-data on source page
# viewable=1: only show the films available in geo location
FILMS_URL = "http://www.theauteurs.com/films?page=%d&sort=%s&view_format=expanded&viewable=1"
VIDEO_PAGE_URL = "http://www.theauteurs.com%s/secure_url"
FLASH_PAGE_URL = "http://www.theauteurs.com%s/watch"
# Sort parameters: only the ones that made sense
POPULARITY = "popularity"
RECENTLY_ADDED = "recently_added"
NAME = "name"
DIRECTOR = "director"
YEAR = "year"
VIEWS = "views" # How is this different than popularity?
RUNNING_TIME = "running_time"
RATING = "rating"
COUNTRY = "country"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenuVideo, "The Auteurs", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = "The Auteurs"
  HTTP.SetCacheTime(CACHE_INTERVAL)
  

####################################################################################################
def MainMenuVideo():
  dir = MediaContainer(mediaType='video')
        
  dir.Append(Function(DirectoryItem(Films, title="Popular Films", thumb=R(ICON)), sort=POPULARITY))
  dir.Append(Function(DirectoryItem(Films, title="Recently Added", thumb=R(ICON)), sort=RECENTLY_ADDED))
  dir.Append(Function(DirectoryItem(Films, title="Highest Rated", thumb=R(ICON)), sort=RATING))
  dir.Append(Function(DirectoryItem(Films, title="Frequently Watched", thumb=R(ICON)), sort=VIEWS))
  dir.Append(Function(DirectoryItem(Films, title="Films by Title", thumb=R(ICON)), sort=NAME))
  dir.Append(Function(DirectoryItem(Films, title="Films by Director", thumb=R(ICON)), sort=DIRECTOR))
  dir.Append(Function(DirectoryItem(Films, title="Films by Year", thumb=R(ICON)), sort=YEAR))
  dir.Append(Function(DirectoryItem(Films, title="Films by Country", thumb=R(ICON)), sort=COUNTRY))
  dir.Append(Function(DirectoryItem(Films, title="Films by Running Time", thumb=R(ICON)), sort=RUNNING_TIME))
  dir.Append(PrefsItem(L("Preferences..."), thumb=R("icon-prefs.png")))
  return dir

##################################
def Films(sender, sort, page=1):
 dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
 if(not Prefs.Get('email') and not Prefs.Get('password')):
   return MessageContainer(header='Login Details', message='Please enter your email and password in the preferences.')
 
 if(not Login()):
   return MessageContainer(header='Log in Unsuccessful', message='Log in was unsuccessful. Please check your name and password in the preferences.')
 url = FILMS_URL % (page, sort)
 for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//div[@id="library"]/div[@class="item"]'):
     title = item.xpath('div/div[@class="details"]/h2[@class="film_title "]/a')[0].text
     location = item.xpath('div/div[@class="details"]/h3[@class="film_country_year"]')[0].text
     cost = item.xpath('div/div[@class="details"]//span[@class="cost"]')[0].text
     rating = item.xpath('div/div[@class="details"]//ul/li[@class="current_rating"]')[0].text
     subtitle = location + "  " +cost + "\n" + rating
     
     videoPath = item.xpath('div/div[@class="media"]/a')[0].get('href')
     summary = item.xpath('div/div[@class="synopsis"]/p')[0].text
     thumb = item.xpath('div/div[@class="media"]/a/img')[0].get('src')
     
     videoPageUrl = FLASH_PAGE_URL % videoPath
     Log(videoPageUrl)
     if(cost == 'Free'):
       dir.Append(WebVideoItem(videoPageUrl, title=title, subtitle=subtitle, summary=summary, thumb=thumb))
     
 if(XML.ElementFromURL(url, True, errors='ignore').xpath( '//div[@id="library"]/div[@class="library_pagination"]/a[@class="next_page"]')):
   dir.Append(Function(DirectoryItem(Films, title="More...",  thumb=R(ICON)), sort=sort, page=page+1))
 return dir

#################################################################
def CreatePrefs():
  Prefs.Add(id='email',    type='text', default='', label='Email')
  Prefs.Add(id='password', type='text', default='', label='Password', option='hidden')


#################################################################
def Login():
  if(XML.ElementFromURL(FRONT_PAGE, True, errors='ignore', cacheTime = 0).xpath('//ul/li/a[@href="http://www.theauteurs.com/logout"]')):
    return True
  else:
    token = XML.ElementFromURL(FRONT_PAGE, True, errors='ignore', cacheTime = 0).xpath('//div[@id="splash_login"]/form//input[@name="authenticity_token"]')[0].get('value')
    values = {
     'authenticity_token' : token,
     'email' : Prefs.Get('email'),
     'password' : Prefs.Get('password')
    }
    x = HTTP.Request(FRONT_PAGE + "session", values, cacheTime = 0)
    success = x.find('Login') == -1
    return success
    