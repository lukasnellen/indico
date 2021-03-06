# -*- coding: utf-8 -*-
##
##
## This file is part of CDS Indico.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Indico; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import MaKaC.webinterface.wcomponents as wcomponents
import MaKaC.webinterface.urlHandlers as urlHandlers
from MaKaC.common.Configuration import Config
from MaKaC.common.contextManager import ContextManager
from MaKaC.common.info import HelperMaKaCInfo
from MaKaC.i18n import _
from indico.util.i18n import i18nformat

from MaKaC.plugins.base import OldObservable


class WPBase(OldObservable):
    """
    """
    _title = "Indico"

    # required user-specific "data packages"
    _userData = []

    def __init__( self, rh ):
        self._rh = rh
        self._locTZ = ""

        #store page specific CSS and JS
        self._extraCSS = []
        self._extraJS = []

    def _includeJSPackage(self, packageName, module = 'indico', path=None):
        info = HelperMaKaCInfo().getMaKaCInfoInstance()

        if info.isDebugActive():
            return ['js/%s/%s/Loader.js' % (module, packageName)]
        else:
            return ['js/%s/pack/%s.js.pack' % (module, packageName)]

    def _includeJQuery(self):
        info = HelperMaKaCInfo().getMaKaCInfoInstance()
        files = ['underscore', 'jquery', 'jquery-ui', 'jquery.form', 'jquery.custom',
                 'jquery.daterange', 'jquery.qtip', 'jquery.dttbutton', 'jquery.colorbox',
                 'jquery.menu']
        if info.isDebugActive():
            # We can't use Loader.js as jQuery is included before any indico js
            return ['js/jquery/%s.js' % f for f in files]
        else:
            return ['js/jquery/pack/jquery.js.pack']

    def _includeJSFile(self, path, filename):
        info = HelperMaKaCInfo().getMaKaCInfoInstance()

        if info.isDebugActive():
            return ['%s/%s.js' % (path, filename)]
        else:
            return ['%s/%s.js.pack' % (path, filename)]

    def _includePresentationFiles(self):
        info = HelperMaKaCInfo().getMaKaCInfoInstance()

        if info.isDebugActive():
            return ['js/presentation/Loader.js', 'js/indico/jquery/defaults.js', 'js/indico/jquery/global.js']
        else:
            return ['js/presentation/pack/Presentation.js.pack', 'js/indico/jquery/defaults.js', 'js/indico/jquery/global.js']

    def _getBaseURL( self ):
        if self._rh._req.is_https() and Config.getInstance().getBaseSecureURL():
            baseurl = Config.getInstance().getBaseSecureURL()
        else:
            baseurl = Config.getInstance().getBaseURL()
        return baseurl

    def _getTitle( self ):
        return self._title

    def _setTitle( self, newTitle ):
        self._title = newTitle.strip()

    def getCSSFiles(self):
        return []

    def getJSFiles(self):
        return self._includeJQuery() + \
               self._includePresentationFiles() + \
               self._includeJSPackage('Core') + \
               self._includeJSPackage('Legacy') + \
               self._includeJSPackage('Common')

    def _getJavaScriptInclude(self, scriptPath):
        return '<script src="'+ scriptPath +'" type="text/javascript"></script>\n'

    def _getJavaScriptUserData(self):
        """
        Returns structured data that should be passed on to the client side
        but depends on user data (can't be in vars.js.tpl)
        """

        user = self._getAW().getUser();

        from MaKaC.webinterface.asyndico import UserDataFactory

        userData = dict((packageName,
                         UserDataFactory(user).build(packageName))
                        for packageName in self._userData)

        return userData

    def _getHeadContent( self ):
        """
        Returns _additional_ content between <head></head> tags.
        Please note that <title>, <meta> and standard CSS are always included.

        Override this method to add your own, page-specific loading of
        JavaScript, CSS and other legal content for HTML <head> tag.
        """
        return ""

    def _getWarningMessage(self):
        return ""

    def _getHTMLHeader( self ):
        from MaKaC.webinterface.pages.conferences import WPConfSignIn
        from MaKaC.webinterface.pages.signIn import WPSignIn
        from MaKaC.webinterface.pages.registrationForm import WPRegistrationFormSignIn
        from MaKaC.webinterface.rh.base import RHModificationBaseProtected
        from MaKaC.webinterface.rh.admins import RHAdminBase

        area=""
        if isinstance(self._rh, RHModificationBaseProtected):
            area=i18nformat(""" - _("Management area")""")
        elif isinstance(self._rh, RHAdminBase):
            area=i18nformat(""" - _("Administrator area")""")

        info = HelperMaKaCInfo().getMaKaCInfoInstance()
        websession = self._getAW().getSession()
        if websession:
            language = websession.getLang()
        else:
            language = info.getLang()

        return wcomponents.WHTMLHeader().getHTML({
            "area": area,
            "baseurl": self._getBaseURL(),
            "conf": Config.getInstance(),
            "page": self,
            "extraCSS": self.getCSSFiles(),
            "extraJSFiles": self.getJSFiles(),
            "extraJS": self._extraJS,
            "language": language,
            "social": info.getSocialAppConfig()
            })

    def _getHTMLFooter( self ):
        return """
    </body>
</html>
               """

    def _display( self, params ):
        """
        """
        return _("no content")

    def _getAW( self ):
        return self._rh.getAW()

    def display( self, **params ):
        """
        """
        return "%s%s%s"%( self._getHTMLHeader(), \
                            self._display( params ), \
                            self._getHTMLFooter() )


    def addExtraJSFile(self, filename):
        self._extraJSFiles.append(filename)

    def addExtraJS(self, jsCode):
        self._extraJS.append(jsCode)

    # auxiliar functions
    def _escapeChars(self, text):
        # Not doing anything right now - it used to convert % to %% for old-style templates
        return text


class WPDecorated( WPBase ):

    def _getSiteArea(self):
        return "DisplayArea"

    def getLoginURL( self ):
        return urlHandlers.UHSignIn.getURL("%s"%self._rh.getCurrentURL())

    def getLogoutURL( self ):
        return urlHandlers.UHSignOut.getURL("%s"%self._rh.getCurrentURL())


    def _getHeader( self ):
        """
        """
        wc = wcomponents.WHeader( self._getAW(), isFrontPage=self._isFrontPage(), currentCategory=self._currentCategory(), locTZ=self._locTZ )

        return wc.getHTML( { "subArea": self._getSiteArea(), \
                             "loginURL": self._escapeChars(str(self.getLoginURL())),\
                             "logoutURL": self._escapeChars(str(self.getLogoutURL())) } )

    def _getTabControl(self):
        return None

    def _getFooter( self):
        """
        """
        wc = wcomponents.WFooter(isFrontPage=self._isFrontPage())
        return wc.getHTML({ "subArea": self._getSiteArea() })

    def _applyDecoration( self, body ):
        """
        """
        return "<div class=\"wrapper\"><div class=\"main\">%s%s</div></div>%s"%( self._getHeader(), body, self._getFooter() )

    def _display( self, params ):

        return self._applyDecoration( self._getBody( params ) )

    def _getBody( self, params ):
        """
        """
        pass

    def _getNavigationDrawer(self):
        return None

    def _isFrontPage(self):
        """
            Welcome page class overloads this, so that additional info (news, policy)
            is shown.
        """
        return False

    def _isRoomBooking(self):
        return False

    def _currentCategory(self):
        """
            Whenever in category display mode this is overloaded with the current category
        """
        return None

    def _getSideMenu(self):
        """
            Overload and return side menu whenever there is one
        """
        return None

class WPNotDecorated( WPBase ):

    def getLoginURL( self ):
        return urlHandlers.UHSignIn.getURL("%s"%self._rh.getCurrentURL())

    def getLogoutURL( self ):
        return urlHandlers.UHSignOut.getURL("%s"%self._rh.getCurrentURL())

    def _display( self, params ):
        return self._getBody( params )

    def _getBody( self, params ):
        """
        """
        pass

    def _getNavigationDrawer(self):
        return None



