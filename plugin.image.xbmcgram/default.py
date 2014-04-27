import os
import sys
import xbmc
import urllib2
import xbmcaddon
import cookielib
import xbmcplugin
import inspect
try:
    import xbmcvfs
except ImportError:
    import xbmcvfsdummy as xbmcvfs
from xbmcswift2 import Plugin
from resources.lib.instagram.client import InstagramAPI
from resources.lib import httplib2

__addon_id__ = 'plugin.image.xbmcgram'
__addon_name__ = 'xbmcgram'

plugin = Plugin(__addon_name__, __addon_id__, __file__)

# xbmc hooks
settings = xbmcaddon.Addon(id='plugin.image.xbmcgram')

# Setup the Instagram API
CONFIG = {
    'access_token': settings.getSetting("oauth2_access_token")
}

api = InstagramAPI(**CONFIG)

# load cookies
path = xbmc.translatePath(settings.getAddonInfo("profile"))
path = os.path.join(path, 'instagram-cookiejar.txt')
print("Loading cookies from :" + repr(path))
cookiejar = cookielib.LWPCookieJar(path)

cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)

@plugin.route('/')
def show_menu():
    items = [
        {'label': 'My Feed',
         'path': plugin.url_for('list_images', category='user_media_feed')},

        {'label': 'View Popular Photos',
         'path': plugin.url_for('list_images', category='media_popular')},

        {'label': 'Boston Common',
         'path': plugin.url_for('list_images', category='location_recent_media')},
    ]
    return items


@plugin.route('/user/<category>')
def list_images(category, max_id=None):

    ''' If called from the slideshow, parse the extension off of the category
        value
    '''
    (category, slideshow) = parse_args(category)

    ''' Get the max_id if it was passed in to the function '''
    try:
        max_id = plugin.request.args['max_id'][0]
    except:
        max_id = None

    kwargs = {}
    if category == 'user_media_feed':
        fxn = api.user_media_feed
    elif category == 'media_popular':
        fxn = api.media_popular
    elif category == 'location_recent_media':
        fxn = api.location_recent_media
        kwargs["location_id"] = 20724

    kwargs["count"] = settings.getSetting("perpage")
    if slideshow:
        kwargs["count"] = 100
    if max_id:
        kwargs["max_id"] = max_id

    try:
        media = fxn(**kwargs)
    except:
        print("InstagramAPIError. Most likely a bad token. Referesh token.")
        login.login()
        media = fxn(**kwargs)
        
    items = get_items(media, category)

    return plugin.finish(items)


def get_items(media, category):
    ''' Most requests return &max_id= in the second index so check that first.
    '''
    try:
        photos = media[0]
        max_id = media[1].split('max_id=')[1]
    except:
        photos = media
        max_id = media[-1].id

    items = [] 
    for photo in photos:
        ''' If the image has comments, use the first one as the caption.
            Otherwise use the username as the caption
        '''
        if photo.caption:
            caption = photo.caption.text
        else:
            caption = photo.user.username
        items.append ({
        'label': caption,
        'thumbnail': photo.images['thumbnail'].url,
        'path': photo.images['standard_resolution'].url,
        'is_playable': True,
        })
	
    items.append({
            'label': 'Next >>',
            'path': plugin.url_for('list_images', category=category, max_id=max_id)
    })

    return items


''' When running from the slideshow plugin, the URL will end in 
    '&plugin_slideshow_ss=true'. Otherwise it will just end in the category
'''
def parse_args(category):
    args = category.split('&plugin_slideshow_ss=true')
    slideshow = False
    category = args[0]
    if len(args) > 1:
        slideshow = True

    return (category, slideshow)

if __name__ == '__main__':

    ''' Check if this was called from another application, like the screensaver
        plugin. If so, don't perform the login step
    '''
    try:
        frm = inspect.stack()[1]
        slideshow = True
    except:
        slideshow = False
        
    if not slideshow:
        import CommonFunctions as common
        common.plugin = plugin
        import xbmcgramPluginSettings
        pluginsettings = xbmcgramPluginSettings.xbmcgramPluginSettings()
        import xbmcgramLogin
        login = xbmcgramLogin.xbmcgramLogin()

        if (not settings.getSetting("firstrun")):
            login.login()
            settings.setSetting("firstrun", "1")
        elif (not settings.getSetting("oauth2_access_token")):
            login.login()

    plugin.run()


