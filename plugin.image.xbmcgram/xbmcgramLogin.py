'''
    Instagram plugin for XBMC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import urllib
import urllib2

# ERRORCODES:
# 0 = Ignore
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

class xbmcgramLogin():
    BASE_URL = "https://instagram.com"
    CLIENT_ID = "4f9c1bcfa3e743b0b0e176b424974c68"
    REDIRECT_URI = "https://github.com/dpmeixner"
    API_URL = "https://instagram.com/oauth/authorize/?client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&response_type=token"

    def __init__(self):
        self.xbmc = sys.modules["__main__"].xbmc

        self.pluginsettings = sys.modules["__main__"].pluginsettings
        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.common = sys.modules["__main__"].common

    def login(self, params={}):
        get = params.get
        self.common.log("")

        old_user_name = self.pluginsettings.userName()
        old_user_password = self.pluginsettings.userPassword()
        self.settings.openSettings()

        user_name = self.pluginsettings.userName()
        user_password = self.pluginsettings.userPassword()

        result = ""
        status = 500

        if not user_name:
            return (result, 200)
            
        self.authorize()

    def authorize(self):
        self.common.log("token not refreshed, or new uname or password")
        self.settings.setSetting("oauth2_access_token", "")
        self._apiLogin()


    def _apiLogin(self):
        self.common.log("")

        ret = {}
        link = self.BASE_URL
        
        self.common.log("Fetching instagram.com...")
        
        '''
        Load instagram.com
        '''
        request = urllib2.Request(link)
        request.add_header('User-Agent', self.common.USERAGENT)
        con = urllib2.urlopen(request)
        ret["content"] = con.read()
        ret["location"] = link
        con.close()
        
        self.common.log("Retrieved content")
        
        newurl = self.common.parseDOM(ret["content"], "a", attrs={"href": "\"/accounts/login/\""}, ret="href")
        if len(newurl) > 0:
            newurl[0] = self.BASE_URL + newurl[0]
            # Start login procedure
            fetch_options = {"link": newurl[0], "referer": ret["location"]}
            print("Part A : " + repr(fetch_options))
        else:
            self.common.log("ERROR: Instagram.com content not found")
            
        self.common.log("Fetching login page...")
        
        '''
        Load login page
        '''
        request = urllib2.Request(fetch_options.get("link"))
        request.add_header('User-Agent', self.common.USERAGENT)
        con = urllib2.urlopen(request)
        ret["content"] = con.read()
        ret["location"] = fetch_options.get("link")
        con.close()

        print "Retrieved content"

        newurl = self.common.parseDOM(ret["content"], "form", attrs={"id": "login-form"}, ret="action")
        if len(newurl) > 0:
            newurl[0] = self.BASE_URL + newurl[0]
            url_data = self._fillLoginInfo(ret)
            if len(url_data) > 0:
                fetch_options = {"link": newurl[0], "url_data": url_data, "hidden": "true", "referer": ret["location"]}
                self.common.log("Part B : " + repr(fetch_options), 10)  # WARNING, SHOWS LOGIN INFO/PASSWORD
        
        '''
        Post loging data
        '''
        request = urllib2.Request(fetch_options.get("link"), urllib.urlencode(fetch_options.get("url_data")))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', self.common.USERAGENT)
        request.add_header('Referer', fetch_options.get("referer"))
        
        con = urllib2.urlopen(request)
        ret["content"] = con.read()
        ret["location"] = fetch_options.get("link")
        con.close()
        
        print "Retrieved content..."
        #print ret["content"]
        
        nick = self.common.parseDOM(ret["content"], "script", attrs={"type": "text/javascript"})
        if len(nick) > 0:# and nick[0] != "Sign In":
            print("Logged in. Parsing data: ")# + repr(nick))
            sys.modules["__main__"].cookiejar.save()
            
            
        '''
        API Login
        '''
        
        link = self.API_URL
        request = urllib2.Request(link)
        request.add_header('User-Agent', self.common.USERAGENT)
        con = urllib2.urlopen(request)
        ret["content"] = con.read()
        ret["location"] = link
        redirect = con.geturl()
        con.close()
      
        newurl = self.common.parseDOM(ret["content"], "form", attrs={"method": "POST"}, ret="action")
        token = self.common.parseDOM(ret["content"], "input", attrs={"name": "csrfmiddlewaretoken"}, ret="value")

        if len(newurl) > 0 and len(token) > 0:
            newurl[0] = self.BASE_URL + newurl[0].replace("&amp;", "&")
            url_data = {"csrfmiddlewaretoken": token[0],
                        "allow": "Authorize"}                        
            fetch_options = {"link": newurl[0].replace("&amp;", "&"), "url_data": url_data, "referer": ret["location"]}
            
            print("Press 'Accept' button" + repr(fetch_options))
            
        '''
        Post accept data
        '''
        request = urllib2.Request(fetch_options.get("link"), urllib.urlencode(fetch_options.get("url_data")))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', self.common.USERAGENT)
        request.add_header('Referer', fetch_options.get("referer"))
        
        try:
            con = urllib2.urlopen(request)
            url = con.geturl()
            ret["content"] = con.read()
            ret["location"] = fetch_options.get("link")
            con.close()
            
            ''' If the user already authrozied this application, then the token is found in the
                redirect link from a step earlier.
            '''
            if (url.find("#access_token=") > -1):
                self.settings.setSetting("oauth2_access_token", url.split("#access_token=")[1])
            else:
                self.settings.setSetting("oauth2_access_token", redirect.split("#access_token=")[1])
        except urllib2.HTTPError, e:
            cont = False
            err = str(e)
            msg = e.read()

            print("HTTPError : " + err)
            if e.code == 400 or True:
                self.common.log("Unhandled HTTPError : [%s] %s " % (e.code, msg), 1)

    def _fillLoginInfo(self, ret):
        self.common.log("")
        content = ret["content"]

        url_data = {}

        for name in self.common.parseDOM(content, "input", ret="name"):
            for val in self.common.parseDOM(content, "input", attrs={"name": name}, ret="value"):
                url_data[name] = val

        self.common.log("Extracted url_data: " + repr(url_data))
        url_data["username"] = self.pluginsettings.userName()
        url_data["password"] = self.pluginsettings.userPassword()

        self.common.log("Done")
        return url_data
