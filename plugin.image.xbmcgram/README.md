This plugin lets you view your Instagram pictures via XBMC. 

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
