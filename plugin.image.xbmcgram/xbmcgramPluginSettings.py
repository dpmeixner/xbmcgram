import sys

class xbmcgramPluginSettings():

    def __init__(self):
        self.settings = sys.modules["__main__"].settings
        #self.dbg = sys.modules["__main__"].dbg

    def itemsPerPage(self):
        return (10, 15, 20, 25, 30, 40, 50)[int(self.settings.getSetting("perpage"))]

    def userName(self):
        return self.settings.getSetting("username")

    def userPassword(self):
        return self.settings.getSetting("user_password")

