This plugin lets you view your Instagram pictures via XBMC. 

To make this work with your account, you need an authorization token. To get a
token follow these steps:

1. Copy and paste this URL into your browser:
https://api.instagram.com/oauth/authorize/?client_id=4f9c1bcfa3e743b0b0e176b424974c68&redirect_uri=http://127.0.0.1&response_type=token

2. You should be asked to login to your Instagram Account

3. After logging in, you should now be redirected to the following URL:
http://127.0.0.1/#access_token=<token>

4. Copy the <token> value from the URL into the file <xbmc_addons>/plugin.image.xbmcgram/default.py, 
so that the CONFIG portion of that file looks like:

CONFIG = {
    'access_token': '<token>'
}


To get this to work with the Plugin Screensaver, you need to make one modification. 
In the file <xbmc_addons>/screensaver.plugin.slideshow edit line 107 (right after the else: statment)

Change line 107 from ITEMS.append(u) to ITEMS.append({'url':u.encode('utf-8'),'title':l.getLabel()})

That portion of the code should now look like this:

	for u,l,f in items:
		if f:
			FOLDERS.append(u)
		else:
			ITEMS.append({'url':u.encode('utf-8'),'title':l.getLabel()})
	return bool
