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

from MaKaC.webinterface.pages import authors
from MaKaC.webinterface import urlHandlers
from MaKaC.webinterface.rh.contribDisplay import RHContributionDisplayBase
from MaKaC.errors import MaKaCError

class RHAuthorDisplayBase( RHContributionDisplayBase ):

    def _checkParams( self, params ):
        RHContributionDisplayBase._checkParams( self, params )
        self._authorId = params.get( "authorId", "" ).strip()
        if self._authorId == "":
            raise MaKaCError(_("Author ID not found. The URL you are trying to access might be wrong."))


class RHAuthorDisplay( RHAuthorDisplayBase ):
    _uh = urlHandlers.UHContribAuthorDisplay

    def _process( self ):
        p = authors.WPAuthorDisplay( self, self._contrib, self._authorId )
        return p.display()



