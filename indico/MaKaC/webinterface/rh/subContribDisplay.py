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

import MaKaC.webinterface.pages.subContributions as subContributions
import MaKaC.webinterface.urlHandlers as urlHandlers
from MaKaC.webinterface.rh.base import RHDisplayBaseProtected,\
    RoomBookingDBMixin
from MaKaC.webinterface.rh.conferenceBase import RHSubContributionBase
from MaKaC.common import Config
from MaKaC.errors import ModificationError



class RHSubContributionDisplayBase( RHSubContributionBase, RHDisplayBaseProtected ):

    def _checkParams( self, params ):
        RHSubContributionBase._checkParams( self, params )

    def _checkProtection( self ):
        RHDisplayBaseProtected._checkProtection( self )


class RHSubContributionDisplay( RoomBookingDBMixin, RHSubContributionDisplayBase ):
    _uh = urlHandlers.UHSubContributionDisplay

    def _process( self ):
        p = subContributions.WPSubContributionDisplay( self, self._subContrib )
        wf=self.getWebFactory()
        if wf is not None:
                p = wf.getSubContributionDisplay( self, self._subContrib)
        return p.display()

class RHSubContributionToMarcXML(RHSubContributionDisplayBase):

    def _process( self ):
        filename = "%s - Subcontribution.xml"%self._subContrib.getTitle().replace("/","")
        from MaKaC.common.xmlGen import XMLGen
        from MaKaC.common.output import outputGenerator
        xmlgen = XMLGen()
        xmlgen.initXml()
        outgen = outputGenerator(self.getAW(), xmlgen)
        xmlgen.openTag("marc:record", [["xmlns:marc","http://www.loc.gov/MARC21/slim"],["xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance"],["xsi:schemaLocation", "http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"]])
        outgen.subContribToXMLMarc21(self._subContrib, xmlgen)
        xmlgen.closeTag("marc:record")
        data = xmlgen.getXml()
        self._req.headers_out["Content-Length"] = "%s"%len(data)
        cfg = Config.getInstance()
        mimetype = cfg.getFileTypeMimeType( "XML" )
        self._req.content_type = """%s"""%(mimetype)
        self._req.headers_out["Content-Disposition"] = """inline; filename="%s\""""%filename.replace("\r\n"," ")
        return data
