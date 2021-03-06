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

import urllib
from xml.sax.saxutils import quoteattr
from datetime import datetime
import MaKaC.conference as conference
import MaKaC.webinterface.wcomponents as wcomponents
import MaKaC.webinterface.linking as linking
import MaKaC.webinterface.urlHandlers as urlHandlers
import MaKaC.webinterface.navigation as navigation
import MaKaC.webinterface.materialFactories as materialFactories
import MaKaC.webinterface.timetable as timetable
from MaKaC.webinterface.pages.conferences import WPConfModifScheduleGraphic, WPConferenceBase, WPConferenceModifBase, WPConferenceDefaultDisplayBase
from MaKaC.webinterface.pages.main import WPMainBase
from MaKaC.webinterface.common.person_titles import TitlesRegistry
from MaKaC.common import Config
from MaKaC.common.utils import isStringHTML, formatDateTime
from MaKaC.common import info
from MaKaC.i18n import _
from indico.util.i18n import i18nformat
from MaKaC import user
from pytz import timezone
import MaKaC.common.timezoneUtils as timezoneUtils
from MaKaC.common.fossilize import fossilize
from MaKaC.user import Avatar, AvatarHolder


class WPContributionBase( WPMainBase, WPConferenceBase ):

    def __init__( self, rh, contribution, hideFull = 0 ):
        self._contrib = self._target = contribution
        WPConferenceBase.__init__( self, rh, self._contrib.getConference() )
        self._navigationTarget = contribution
        self._hideFull = hideFull


class WPContributionDefaultDisplayBase( WPConferenceDefaultDisplayBase, WPContributionBase ):

    def getJSFiles(self):
        return WPConferenceDefaultDisplayBase.getJSFiles(self) + \
            self._includeJSPackage('Management') + \
               self._includeJSPackage('MaterialEditor')

    def __init__( self, rh, contribution, hideFull = 0 ):
        WPContributionBase.__init__( self, rh, contribution, hideFull )


class WContributionDisplayBase(wcomponents.WTemplated):

    def __init__(self, aw, contrib, hideFull = 0):
        self._aw = aw
        self._contrib = contrib
        self._hideFull = hideFull

    def _getHTMLRow( self, title, body):
        if body.strip() == "":
            return ""
        str = """
                <tr>
                    <td align="right" valign="top" class="displayField" nowrap><b>%s:</b></td>
                    <td width="100%%" valign="top">%s</td>
                </tr>"""%(title, body)
        return str

    def _getAdditionalFieldsHTML(self):
        html=""
        afm = self._contrib.getConference().getAbstractMgr().getAbstractFieldsMgr()
        for f in afm.getActiveFields():
            id = f.getId()
            caption = f.getName()
            html+=self._getHTMLRow(caption, self.htmlText(self._contrib.getField(id)))
        return html

    def _getSubContributionItem(self, sc, modifURL):
        modifyItem = ""
        url = urlHandlers.UHSubContributionDisplay.getURL(sc)
        if sc.canModify( self._aw ):
            modifyItem = i18nformat("""
                          <a href="%s"><img src="%s" border="0" alt='_("Jump to the modification interface")'></a>
                         """)%(modifURL, Config.getInstance().getSystemIconURL( "modify" ) )
        return """
                <tr>
                <td valign="middle">
                            %s<b>&nbsp;<a href=%s>%s</a></b>
                        </td>
                </tr>
               """%(modifyItem, quoteattr(str(url)), sc.getTitle())

    def _getWithdrawnNoticeHTML(self):
        res=""
        if isinstance(self._contrib.getCurrentStatus(),conference.ContribStatusWithdrawn):
            res= i18nformat("""
                <tr>
                    <td colspan="2" align="center"><b>--_("WITHDRAWN")--</b></td>
                </tr>
                """)
        return res

    def _getSubmitButtonHTML(self):
        res=""
        status=self._contrib.getCurrentStatus()
        if not isinstance(status,conference.ContribStatusWithdrawn) and \
                            self._contrib.canUserSubmit(self._aw.getUser()):
            res= i18nformat("""<input type="submit" class="btn" value="_("manage material")">""")
        return res

    def _getModifIconHTML(self):
        res=""
        if self._contrib.canModify(self._aw):
            res="""<a href="%s"><img src="%s" border="0" alt="Jump to the modification interface"></a>""" % (urlHandlers.UHContributionModification.getURL(self._contrib), Config.getInstance().getSystemIconURL( "modify" ))
        return res

    def _getSubmitIconHTML(self):
        res=""
        if self._contrib.canUserSubmit(self._aw.getUser()):
            res="""<a href="%s"><img src="%s" border="0" alt="Upload files"></a>""" % ('FIXME', Config.getInstance().getSystemIconURL( "submit" ))
        return res

    def _getMaterialHTML(self):
        lm=[]
        paper=self._contrib.getPaper()
        if paper is not None:
            lm.append("""<a href=%s><img src=%s border="0" alt="paper"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(paper))),
                quoteattr(str(materialFactories.PaperFactory().getIconURL())),
                self.htmlText(materialFactories.PaperFactory().getTitle())) )
        slides=self._contrib.getSlides()
        if slides is not None:
            lm.append("""<a href=%s><img src=%s border="0" alt="slide"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(slides))),
                quoteattr(str(materialFactories.SlidesFactory().getIconURL())),
                self.htmlText(materialFactories.SlidesFactory().getTitle())))
        poster=self._contrib.getPoster()
        if poster is not None:
            lm.append("""<a href=%s><img src=%s border="0" alt="poster"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(poster))),
                quoteattr(str(materialFactories.PosterFactory().getIconURL())),
                self.htmlText(materialFactories.PosterFactory().getTitle())))
        video=self._contrib.getVideo()
        if video is not None:
            lm.append("""<a href=%s><img src=%s border="0" alt="video"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(video))),
                quoteattr(str(materialFactories.VideoFactory().getIconURL())),
                self.htmlText(materialFactories.VideoFactory().getTitle())))
        iconURL=quoteattr(str(Config.getInstance().getSystemIconURL("material")))
        minutes=self._contrib.getMinutes()
        if minutes is not None:
            lm.append("""<a href=%s><img src=%s border="0" alt="minutes"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(minutes))),
                quoteattr(str(materialFactories.MinutesFactory().getIconURL())),
                self.htmlText(materialFactories.MinutesFactory().getTitle())))
        iconURL=quoteattr(str(Config.getInstance().getSystemIconURL("material")))
        for material in self._contrib.getMaterialList():
            url=urlHandlers.UHMaterialDisplay.getURL(material)
            lm.append("""<a href=%s><img src=%s border="0" alt=""> %s</a>"""%(
                quoteattr(str(url)),iconURL,self.htmlText(material.getTitle())))
        return self._getHTMLRow("Material","<br>".join(lm))

    def _getReviewingMaterialsHTML(self):
        rm=[]
        reviewing=self._contrib.getReviewing()
        if reviewing is not None:
            rm.append("""<a href=%s><img src=%s border="0" alt="reviewing"> %s</a>"""%(
                quoteattr(str(urlHandlers.UHMaterialDisplay.getURL(reviewing))),
                quoteattr(str(materialFactories.ReviewingFactory().getIconURL())),
                self.htmlText(materialFactories.ReviewingFactory().getTitle())) )
        return self._getHTMLRow("Reviewing Material","<br>".join(rm))

    def getVars( self ):
        vars = wcomponents.WTemplated.getVars( self )
        vars["contribXML"]=quoteattr(str(urlHandlers.UHContribToXML.getURL(self._contrib)))
        vars["contribPDF"]=quoteattr(str(urlHandlers.UHContribToPDF.getURL(self._contrib)))
        vars["contribiCal"]=quoteattr(str(urlHandlers.UHContribToiCal.getURL(self._contrib)))
        vars["xmlIconURL"]=quoteattr(str(Config.getInstance().getSystemIconURL("xml")))
        vars["printIconURL"]=quoteattr(str(Config.getInstance().getSystemIconURL("pdf")))
        vars["icalIconURL"]=quoteattr(str(Config.getInstance().getSystemIconURL("ical")))

        vars["title"] = self.htmlText(self._contrib.getTitle())
        if isStringHTML(self._contrib.getDescription()):
            vars["description"] = self._contrib.getDescription()
        else:
            vars["description"] = """<table class="tablepre"><tr><td><pre>%s</pre></td></tr></table>""" % self._contrib.getDescription()
        vars["additionalFields"] = self._getAdditionalFieldsHTML()
        vars["id"]=self.htmlText(self._contrib.getId())
        vars["startDate"] = i18nformat("""--_("not yet scheduled")--""")
        vars["startTime"] = ""
        if self._contrib.isScheduled():
            tzUtil = timezoneUtils.DisplayTZ(self._aw,self._contrib.getOwner())
            tz = tzUtil.getDisplayTZ()
            sDate = self._contrib.getStartDate().astimezone(timezone(tz))
            vars["startDate"]=self.htmlText(sDate.strftime("%d-%b-%Y"))
            vars["startTime"]=self.htmlText(sDate.strftime("%H:%M") + " (" + tz + ")")
        vars["location"]=""
        loc=self._contrib.getLocation()
        if loc is not None:
            vars["location"]="<i>%s</i>"%(self.htmlText(loc.getName()))
            if loc.getAddress() is not None and loc.getAddress()!="":
                vars["location"]="%s <pre>%s</pre>"%(vars["location"],loc.getAddress())
        room=self._contrib.getRoom()
        if room is not None:
            roomLink=linking.RoomLinker().getHTMLLink(room,loc)
            vars["location"]= i18nformat("""%s<br><small> _("Room"):</small> %s""")%(\
                vars["location"],roomLink)
            if self._contrib.getBoardNumber()!="":
                vars["location"]= i18nformat("""%s - _("board #"): %s""")%(vars["location"],self._contrib.getBoardNumber())
        else:
            if self._contrib.getBoardNumber()!="":
                vars["location"]= i18nformat("""%s <br> _("board #"): %s""")%(vars["location"],self._contrib.getBoardNumber())

        vars["location"]=self._getHTMLRow( _("Place"),vars["location"])

        authIndex = self._contrib.getConference().getAuthorIndex()

        l=[]
        for speaker in self._contrib.getSpeakerList():
            l.append(self.htmlText(speaker.getFullName()))
        vars["speakers"]=self._getHTMLRow( _("Presenters"),"<br>".join(l))

        pal = []
        for pa in self._contrib.getPrimaryAuthorList():
            authURL=urlHandlers.UHContribAuthorDisplay.getURL(self._contrib)
            authURL.addParam("authorId", pa.getId())
            authCaption="<a href=%s>%s</a>"%(quoteattr(str(authURL)), self.htmlText(pa.getFullName()))
            if pa.getAffiliation()!="":
                authCaption="%s (%s)"%(authCaption,self.htmlText(pa.getAffiliation()))
            pal.append(authCaption)
        vars["primaryAuthors"]=self._getHTMLRow( _("Primary Authors"),"<br>".join(pal))
        cal = []
        for ca in self._contrib.getCoAuthorList():
            authCaption="%s"%ca.getFullName()
            if ca.getAffiliation()!="":
                authCaption="%s (%s)"%(authCaption,ca.getAffiliation())
            cal.append(self.htmlText(authCaption))
        vars["coAuthors"]=self._getHTMLRow( _("Co-Authors"),"<br>".join(cal))
        vars["contribType"]=""
        if self._contrib.getType() != None:
            vars["contribType"]=self._getHTMLRow( _("Contribution type"),self.htmlText(self._contrib.getType().getName()))

        #TODO: fuse this two lines into one, so that they are not both executed...
        #but the 1st line generates a lot of HTML in Python...
        vars["material"]=self._getMaterialHTML()
        vars["revmaterial"]=self._getReviewingMaterialsHTML()

        vars["MaterialList"] = wcomponents.WShowExistingMaterial(self._contrib, showTitle=False).getHTML()
        vars["ReviewingMatList"] = wcomponents.WShowExistingReviewingMaterial(self._contrib, False, True).getHTML()

        vars["duration"]=""
        if self._contrib.getDuration() is not None:
            vars["duration"]=(datetime(1900,1,1)+self._contrib.getDuration()).strftime("%M'")
            if (datetime(1900,1,1)+self._contrib.getDuration()).hour>0:
                vars["duration"]=(datetime(1900,1,1)+self._contrib.getDuration()).strftime("%Hh%M'")
        vars["inSession"]=""
        if self._contrib.getSession() is not None:
            url=urlHandlers.UHSessionDisplay.getURL(self._contrib.getSession())
            sessionCaption="%s"%self._contrib.getSession().getTitle()
            vars["inSession"]="""<a href=%s>%s</a>"""%(\
                quoteattr(str(url)),self.htmlText(sessionCaption))
        vars["inSession"]=self._getHTMLRow( _("Included in session"),vars["inSession"])
        vars["inTrack"]=""
        if self._contrib.getTrack():
            trackCaption=self._contrib.getTrack().getTitle()
            vars["inTrack"]="""%s"""%(self.htmlText(trackCaption))
        vars["inTrack"]=self._getHTMLRow( _("Included in track"),vars["inTrack"])
        scl = []
        for sc in self._contrib.getSubContributionList():
            url=urlHandlers.UHSubContributionModification.getURL(sc)
            scl.append(self._getSubContributionItem(sc,url))
        vars["subConts"]=""
        if scl:
            scl.insert(0,"""<table align="left" valign="top" width="100%%" border="0" cellpadding="3" cellspacing="3">""")
            scl.append("</table>")
            vars["subConts"]=self._getHTMLRow( _("Sub-contributions"),"".join(scl))
        vars["withdrawnNotice"] = self._getWithdrawnNoticeHTML()
        vars["isWithdrawn"] = isinstance(self._contrib.getCurrentStatus(),conference.ContribStatusWithdrawn)
        vars["submitBtn"]=self._getSubmitButtonHTML()
        vars["submitURL"]=quoteattr('FIXME')
        vars["modifIcon"] = self._getModifIconHTML()
        vars["Contribution"] = self._contrib
        import contributionReviewing
        vars["ConfReview"] = self._contrib.getConference().getConfPaperReview()
        vars["reviewingStuffDisplay"]= contributionReviewing.WContributionReviewingDisplay(self._contrib).getHTML({"ShowReviewingTeam" : False})
        vars["reviewingHistoryStuffDisplay"]= contributionReviewing.WContributionReviewingHistory(self._contrib).getHTML({"ShowReviewingTeam" : False})
        if self._contrib.getSession():
            vars["sessionType"] = self._contrib.getSession().getScheduleType()
        else:
            vars["sessionType"] = 'none'

        if self._hideFull == 1:
            vars["hideInfo"] = True
        else:
            vars["hideInfo"] = False
        return vars


class WContributionDisplayFull(WContributionDisplayBase):
    pass


class WContributionDisplayMin(WContributionDisplayBase):
    pass


class WContributionDisplay:

    def __init__(self, aw, contrib, hideFull = 0):
        self._aw = aw
        self._contrib = contrib
        self._hideFull = hideFull

    def getHTML(self,params={}):
        if self._contrib.canAccess( self._aw ):
            c = WContributionDisplayFull( self._aw, self._contrib, self._hideFull)
            return c.getHTML( params )
        if self._contrib.canView( self._aw ):
            c = WContributionDisplayMin( self._aw, self._contrib)
            return c.getHTML( params )
        return ""


class WPContributionDisplay( WPContributionDefaultDisplayBase ):
    navigationEntry = navigation.NEContributionDisplay

    def _defineToolBar(self):
        edit=wcomponents.WTBItem( _("manage this contribution"),
            icon=Config.getInstance().getSystemIconURL("modify"),
            actionURL=urlHandlers.UHContributionModification.getURL(self._contrib),
            enabled=self._target.canModify(self._getAW()))
        pdf=wcomponents.WTBItem( _("get PDF of this contribution"),
            icon=Config.getInstance().getSystemIconURL("pdf"),
            actionURL=urlHandlers.UHContribToPDF.getURL(self._contrib))
        xml=wcomponents.WTBItem( _("get XML of this contribution"),
            icon=Config.getInstance().getSystemIconURL("xml"),
            actionURL=urlHandlers.UHContribToXML.getURL(self._contrib))
        ical=wcomponents.WTBItem( _("get ICal of this contribution"),
            icon=Config.getInstance().getSystemIconURL("ical"),
            actionURL=urlHandlers.UHContribToiCal.getURL(self._contrib))
        self._toolBar.addItem(edit)
        self._toolBar.addItem(pdf)
        self._toolBar.addItem(xml)
        self._toolBar.addItem(ical)

    def _getBody( self, params ):
        wc=WContributionDisplay( self._getAW(), self._contrib, self._hideFull )
        return wc.getHTML()


class WPContributionModifBase( WPConferenceModifBase  ):

    def __init__( self, rh, contribution ):
        WPConferenceModifBase.__init__( self, rh, contribution.getConference() )
        self._contrib = self._target = contribution
        from MaKaC.webinterface.rh.reviewingModif import RCPaperReviewManager
        self._isPRM = RCPaperReviewManager.hasRights(rh)
        self._canModify = self._conf.canModify(rh.getAW())

    def _getEnabledControls(self):
        return False

    def _getNavigationDrawer(self):
        pars = {"target": self._contrib , "isModif": True}
        return wcomponents.WNavigationDrawer( pars, bgColor="white" )

    def _createTabCtrl( self ):

        self._tabCtrl = wcomponents.TabControl()
        self._tabMain = self._tabCtrl.newTab( "main", _("Main"), \
                urlHandlers.UHContributionModification.getURL( self._target ) )
        self._tabMaterials = self._tabCtrl.newTab( "materials", _("Material"), \
                urlHandlers.UHContribModifMaterials.getURL( self._target ) )
        #self._tabMaterials = self._tabCtrl.newTab( "materials", _("Files"), \
        #        urlHandlers.UHContribModifMaterials.getURL( self._target ) )
        self._tabSubCont = self._tabCtrl.newTab( "subCont", _("Sub Contribution"), \
                urlHandlers.UHContribModifSubCont.getURL( self._target ) )
        if self._canModify:
            self._tabAC = self._tabCtrl.newTab( "ac", _("Protection"), \
                urlHandlers.UHContribModifAC.getURL( self._target ) )
            self._tabTools = self._tabCtrl.newTab( "tools", _("Tools"), \
                urlHandlers.UHContribModifTools.getURL( self._target ) )

        hasReviewingEnabled = self._contrib.getConference().hasEnabledSection('paperReviewing')
        paperReviewChoice = self._contrib.getConference().getConfPaperReview().getChoice()

        if hasReviewingEnabled and paperReviewChoice != 1:

            if self._canModify or self._isPRM or self._contrib.getReviewManager().isReferee(self._rh._getUser()):
                self._subtabReviewing = self._tabCtrl.newTab( "reviewing", "Paper Reviewing", \
                urlHandlers.UHContributionModifReviewing.getURL( self._target ) )
            else:
                if self._contrib.getReviewManager().isEditor(self._rh._getUser()):
                    self._subtabReviewing = self._tabCtrl.newTab( "reviewing", "Paper Reviewing", \
                    urlHandlers.UHContributionEditingJudgement.getURL( self._target ) )
                elif self._contrib.getReviewManager().isReviewer(self._rh._getUser()):
                    self._subtabReviewing = self._tabCtrl.newTab( "reviewing", "Paper Reviewing", \
                    urlHandlers.UHContributionGiveAdvice.getURL( self._target ) )


            if self._canModify or self._isPRM or self._contrib.getReviewManager().isReferee(self._rh._getUser()):
                self._subTabAssign = self._subtabReviewing.newSubTab( "assign", _("Assign Team"), \
                urlHandlers.UHContributionModifReviewing.getURL( self._target ) )
                if self._contrib.getReviewManager().isReferee(self._rh._getUser()) and not (paperReviewChoice == 3 or paperReviewChoice == 1):
                    self._subTabJudgements = self._subtabReviewing.newSubTab( "final", _("Final Judgement"), \
                    urlHandlers.UHContributionReviewingJudgements.getURL( self._target ) )
                else:
                    self._subTabJudgements = self._subtabReviewing.newSubTab( "Judgements", _("Judgements"), \
                    urlHandlers.UHContributionReviewingJudgements.getURL( self._target ) )

            if (paperReviewChoice == 3 or paperReviewChoice == 4) and \
                self._contrib.getReviewManager().isEditor(self._rh._getUser()) and \
                (not self._contrib.getReviewManager().getLastReview().getRefereeJudgement().isSubmitted() or paperReviewChoice == 3) and \
                self._contrib.getReviewManager().getLastReview().isAuthorSubmitted():

                self._tabJudgeEditing = self._subtabReviewing.newSubTab( "editing", "Judge Layout", \
                urlHandlers.UHContributionEditingJudgement.getURL(self._target) )

            if (paperReviewChoice == 2 or paperReviewChoice == 4) and \
                self._contrib.getReviewManager().isReviewer(self._rh._getUser()) and \
                not self._contrib.getReviewManager().getLastReview().getRefereeJudgement().isSubmitted():

                self._tabGiveAdvice = self._subtabReviewing.newSubTab( "advice", "Judge Content", \
                                      urlHandlers.UHContributionGiveAdvice.getURL(self._target))

            if self._canModify or self._isPRM or self._contrib.getReviewManager().isInReviewingTeamforContribution(self._rh._getUser()):
                self._subTabRevMaterial = self._subtabReviewing.newSubTab( "revmaterial", _("Material to Review"), \
                urlHandlers.UHContribModifReviewingMaterials.getURL( self._target ) )

            if self._canModify or self._isPRM or self._contrib.getReviewManager().isReferee(self._rh._getUser()) or \
            len(self._contrib.getReviewManager().getVersioning()) > 1 or self._contrib.getReviewManager().getLastReview().getRefereeJudgement().isSubmitted():
                self._subTabReviewingHistory = self._subtabReviewing.newSubTab( "reviewing_history", "History", \
                                            urlHandlers.UHContributionModifReviewingHistory.getURL( self._target ) )

        self._setActiveTab()
        self._setupTabCtrl()

    def _setActiveTab( self ):
        pass

    def _setupTabCtrl(self):
        pass

    def _setActiveSideMenuItem(self):
        if self._target.isScheduled():
            self._timetableMenuItem.setActive(True)
        else:
            self._contribListMenuItem.setActive(True)

    def _getPageContent( self, params ):
        self._createTabCtrl()
        #TODO: check if it comes from the timetable or the contribution list
        # temp solution: isScheduled.
        banner = ""
        if self._canModify or self._isPRM:
            banner = wcomponents.WContribListBannerModif(self._target).getHTML()
        else:
            if self._conf.getConfPaperReview().isRefereeContribution(self._rh._getUser(), self._contrib):
                banner = wcomponents.WListOfPapersToReview(self._target, "referee").getHTML()
            if self._conf.getConfPaperReview().isReviewerContribution(self._rh._getUser(), self._contrib):
                banner = wcomponents.WListOfPapersToReview(self._target, "reviewer").getHTML()
            if self._conf.getConfPaperReview().isEditorContribution(self._rh._getUser(), self._contrib):
                banner = wcomponents.WListOfPapersToReview(self._target, "editor").getHTML()
        if banner == "":
            banner = wcomponents.WTimetableBannerModif(self._getAW(), self._target).getHTML()

        body = wcomponents.WTabControl( self._tabCtrl, self._getAW() ).getHTML( self._getTabContent( params ) )
        return banner + body

class WPContribModifMain( WPContributionModifBase ):

    def _setActiveTab( self ):
        self._tabMain.setActive()

class WPContributionModifTools( WPContributionModifBase ):

    def _setActiveTab( self ):
        self._tabTools.setActive()

    def _getTabContent( self, params ):
        wc = wcomponents.WContribModifTool( self._target )
        pars = { \
"deleteContributionURL": urlHandlers.UHContributionDelete.getURL( self._target ), \
"MoveContributionURL": urlHandlers.UHContributionMove.getURL( self._target ) }
        return wc.getHTML( pars )

class WPContributionModifMaterials( WPContributionModifBase ):

    _userData = ['favorite-user-list']

    def __init__(self, rh, contribution):
        WPContributionModifBase.__init__(self, rh, contribution)

    def _setActiveTab( self ):
        self._tabMaterials.setActive()

    def _getTabContent( self, pars ):
        wc=wcomponents.WShowExistingMaterial(self._target, mode='management', showTitle=True)
        return wc.getHTML( pars )


class WAuthorTable(wcomponents.WTemplated):

    def __init__(self, authList, contrib):
        self._list = authList
        self._conf = contrib.getConference()
        self._contrib = contrib

    def getVars(self):
        vars=wcomponents.WTemplated.getVars(self)
        urlGen=vars.get("modAuthorURLGen",None)
        l = []
        for author in self._list:
            authCaption=author.getFullName()
            if author.getAffiliation()!="":
                authCaption="%s (%s)"%(authCaption,author.getAffiliation())
            if urlGen:
                authCaption="""<a href=%s>%s</a>"""%(urlGen(author),self.htmlText(authCaption))
            href ="\"\""
            if author.getEmail() != "":
                mailtoSubject = """[%s] _("Contribution") %s: %s"""%( self._conf.getTitle(), self._contrib.getId(), self._contrib.getTitle() )
                mailtoURL = "mailto:%s?subject=%s"%( author.getEmail(), urllib.quote( mailtoSubject ) )
                href = quoteattr( mailtoURL )
            emailHtml = """ <a href=%s><img src="%s" style="border:0px" alt="email"></a> """%(href, Config.getInstance().getSystemIconURL("smallEmail"))
            upURLGen=vars.get("upAuthorURLGen",None)
            up=""
            if upURLGen is not None:
                up="""<a href=%s><img src=%s border="0" alt="up"></a>"""%(quoteattr(str(upURLGen(author))),quoteattr(str(Config.getInstance().getSystemIconURL("upArrow"))))
            downURLGen=vars.get("downAuthorURLGen",None)
            down=""
            if downURLGen is not None:
                down="""<a href=%s><img src=%s border="0" alt="down"></a>"""%(quoteattr(str(downURLGen(author))),quoteattr(str(Config.getInstance().getSystemIconURL("downArrow"))))
            l.append("""<input type="checkbox" name="selAuthor" value=%s>%s%s%s %s"""%(quoteattr(author.getId()),up,down,emailHtml,authCaption))
        vars["authors"] = "<br>".join(l)
        vars["remAuthorsURL"] = vars.get("remAuthorsURL","")
        vars["addAuthorsURL"] = vars.get("addAuthorsURL","")
        vars["searchAuthorURL"] = vars.get("searchAuthorURL","")
        return vars

class WContribModifClosed(wcomponents.WTemplated):

    def __init__(self):
        pass

    def getVars(self):
        vars = wcomponents.WTemplated.getVars(self)
        vars["closedIconURL"] = Config.getInstance().getSystemIconURL("closed")
        return vars

class WContribModifMain(wcomponents.WTemplated):

    def __init__( self, contribution, mfRegistry, eventType = "conference" ):
        self._contrib = contribution
        self._mfRegistry = mfRegistry
        self._eventType = eventType

    def _getAbstractHTML( self ):
        if not self._contrib.getConference().getAbstractMgr().isActive() or not self._contrib.getConference().hasEnabledSection("cfa"):
            return ""
        abs = self._contrib.getAbstract()
        if abs is not None:
            html = i18nformat("""
             <tr>
                <td class="dataCaptionTD"><span class="dataCaptionFormat"> _("Abstract")</span></td>
                <td bgcolor="white" class="blacktext"><a href=%s>%s - %s</a></td>
            </tr>
            <tr>
                <td colspan="3" class="horizontalLine">&nbsp;</td>
            </tr>
                """)%( quoteattr(str(urlHandlers.UHAbstractManagment.getURL(abs))),\
                    self.htmlText(abs.getId()), abs.getTitle() )
        else:
            html = i18nformat("""
             <tr>
                <td class="dataCaptionTD"><span class="dataCaptionFormat"> _("Abstract")</span></td>
                <td bgcolor="white" class="blacktext">&nbsp;&nbsp;&nbsp;<font color="red"> _("The abstract associated with this contribution has been removed")</font></td>
            </tr>
            <tr>
                <td colspan="3" class="horizontalLine">&nbsp;</td>
            </tr>
                """)
        return html

    def _getChangeTracksHTML(self):
        res=[]
        if not self._contrib.getTrack() is None:
            res=[ i18nformat("""<option value="">--_("none")--</option>""")]
        for track in self._contrib.getConference().getTrackList():
            if self._contrib.getTrack()==track:
                continue
            res.append("""<option value=%s>%s</option>"""%(quoteattr(str(track.getId())),self.htmlText(track.getTitle())))
        return "".join(res)

    def _getChangeSessionsHTML(self):
        res=[]
        if not self._contrib.getSession() is None:
            res=[ i18nformat("""<option value="">--_("none")--</option>""")]
        for session in self._contrib.getConference().getSessionListSorted():
            if self._contrib.getSession()==session:
                continue
            from MaKaC.common.TemplateExec import truncateTitle
            res.append("""<option value=%s>%s</option>"""%(quoteattr(str(session.getId())),self.htmlText(truncateTitle(session.getTitle(), 60))))
        return "".join(res)

    def _getWithdrawnNoticeHTML(self):
        res=""
        status=self._contrib.getCurrentStatus()
        if isinstance(status,conference.ContribStatusWithdrawn):
            res= i18nformat("""
                <tr>
                    <td align="center"><b>--_("WITHDRAWN")--</b></td>
                </tr>
                """)
        return res

    def _getWithdrawnInfoHTML(self):
        status=self._contrib.getCurrentStatus()
        if not isinstance(status,conference.ContribStatusWithdrawn):
            return ""
        comment=""
        if status.getComment()!="":
            comment="""<br><i>%s"""%self.htmlText(status.getComment())
        d=self.htmlText(status.getDate().strftime("%Y-%b-%D %H:%M"))
        resp=""
        if status.getResponsible() is not None:
            resp="by %s"%self.htmlText(status.getResponsible().getFullName())
        html = i18nformat("""
     <tr>
        <td class="dataCaptionTD"><span class="dataCaptionFormat"> _("Withdrawal information")</span></td>
        <td bgcolor="white" class="blacktext"><b> _("WITHDRAWN")</b> _("on") %s %s%s</td>
    </tr>
    <tr>
        <td colspan="3" class="horizontalLine">&nbsp;</td>
    </tr>
            """)%(d,resp,comment)
        return html

    def _getAdditionalFieldsHTML(self):
        html=""
        if self._contrib.getConference().getAbstractMgr().isActive() and self._contrib.getConference().hasEnabledSection("cfa") and self._contrib.getConference().getAbstractMgr().hasAnyEnabledAbstractField():
            for f in self._contrib.getConference().getAbstractMgr().getAbstractFieldsMgr().getFields():
                if f.isActive():
                    id = f.getId()
                    caption = f.getName()
                    html+="""
                    <tr>
                        <td class="dataCaptionTD"><span class="dataCaptionFormat">%s</span></td>
                        <td bgcolor="white" class="blacktext"><table class="tablepre"><tr><td><pre>%s</pre></td></tr></table></td>
                    </tr>"""%(caption, self.htmlText( self._contrib.getField(id) ))
        return html

    def _getParticipantsList(self, participantList):
        result = []
        for part in participantList:
            partFossil = fossilize(part)
            # var to control if we have to show the entry in the author menu to allow add submission rights
            isSubmitter = False
            av = AvatarHolder().match({"email": part.getEmail()}, forceWithoutExtAuth=True, exact=True)
            if not av:
                if part.getEmail() in self._contrib.getSubmitterEmailList():
                    isSubmitter = True
            elif (av[0] in self._contrib.getSubmitterList() or self._contrib.getConference().getPendingQueuesMgr().isPendingSubmitter(part)):
                isSubmitter = True
            partFossil["showSubmitterCB"] = not isSubmitter
            result.append(partFossil)
        return result

    def getVars( self ):
        vars = wcomponents.WTemplated.getVars( self )
        vars["eventType"] = self._eventType
        vars["withdrawnNotice"]=self._getWithdrawnNoticeHTML()
        vars["locator"] = self._contrib.getLocator().getWebForm()
        vars["title"] = self._contrib.getTitle()
        if isStringHTML(self._contrib.getDescription()):
            vars["description"] = self._contrib.getDescription()
        else:
            vars["description"] = """<table class="tablepre"><tr><td><pre>%s</pre></td></tr></table>""" % self._contrib.getDescription()
        vars["additionalFields"] = self._getAdditionalFieldsHTML()
        vars["rowspan"]="6"
        vars["place"] = ""
        if self._contrib.getLocation():
            vars["place"]=self.htmlText(self._contrib.getLocation().getName())
        room=self._contrib.getRoom()
        if room is not None and room.getName().strip()!="":
            vars["place"]= i18nformat("""%s <br> _("Room"): %s""")%(vars["place"],self.htmlText(room.getName()))
        if self._eventType == "conference" and self._contrib.getBoardNumber()!="" and self._contrib.getBoardNumber() is not None:
            vars["place"]= i18nformat("""%s<br> _("Board #")%s""")%(vars["place"],self.htmlText(self._contrib.getBoardNumber()))
        vars["id"] = self.htmlText( self._contrib.getId() )
        vars["dataModificationURL"] = str( urlHandlers.UHContributionDataModification.getURL( self._contrib ) )
        vars["duration"]=""
        if self._contrib.getDuration() is not None:
            vars["duration"]=(datetime(1900,1,1)+self._contrib.getDuration()).strftime("%Hh%M'")
        vars["type"] = ""
        if self._contrib.getType():
            vars["type"] = self.htmlText( self._contrib.getType().getName() )
        vars["track"] = i18nformat("""--_("none")--""")
        if self._contrib.getTrack():
            vars["track"] = """<a href=%s>%s</a>"""%(quoteattr(str(urlHandlers.UHTrackModification.getURL(self._contrib.getTrack()))),self.htmlText(self._contrib.getTrack().getTitle()))
        vars["session"] = ""
        if self._contrib.getSession():
            vars["session"]="""<a href=%s>%s</a>"""%(quoteattr(str(urlHandlers.UHSessionModification.getURL(self._contrib.getSession()))),self.htmlText(self._contrib.getSession().getTitle()))
        vars["abstract"] = ""
        if isinstance(self._contrib, conference.AcceptedContribution):
            vars["abstract"] = self._getAbstractHTML()
        vars["contrib"] = self._contrib
        vars["selTracks"]=self._getChangeTracksHTML()
        vars["setTrackURL"]=quoteattr(str(urlHandlers.UHContribModSetTrack.getURL(self._contrib)))
        vars["selSessions"]=self._getChangeSessionsHTML()
        vars["setSessionURL"]=quoteattr(str(urlHandlers.UHContribModSetSession.getURL(self._contrib)))
        vars["contribXML"]=urlHandlers.UHContribToXMLConfManager.getURL(self._contrib)
        vars["contribPDF"]=urlHandlers.UHContribToPDFConfManager.getURL(self._contrib)
        vars["printIconURL"] = Config.getInstance().getSystemIconURL("pdf")
        vars["xmlIconURL"]=Config.getInstance().getSystemIconURL("xml")
        vars["withdrawURL"]=quoteattr(str(urlHandlers.UHContribModWithdraw.getURL(self._contrib)))
        vars["withdrawnInfo"]=self._getWithdrawnInfoHTML()
        vars["withdrawDisabled"]=False
        if isinstance(self._contrib.getCurrentStatus(),conference.ContribStatusWithdrawn):
            vars["withdrawDisabled"]=True
        vars["reportNumbersTable"]=wcomponents.WReportNumbersTable(self._contrib,"contribution").getHTML()
        vars["keywords"]=self._contrib.getKeywords()
        if self._contrib.getSession():
            vars["sessionType"] = self._contrib.getSession().getScheduleType()
        else:
            vars["sessionType"] = 'none'
        vars["primaryAuthors"] = self._getParticipantsList(self._contrib.getPrimaryAuthorList())
        vars["coAuthors"] = self._getParticipantsList(self._contrib.getCoAuthorList())
        vars["speakers"] = self._getParticipantsList(self._contrib.getSpeakerList())
        return vars


class WPContributionModification( WPContribModifMain ):

    def _getTabContent( self, params ):
        wc = WContribModifMain( self._contrib, materialFactories.ContribMFRegistry() )
        return wc.getHTML()

class WPContributionModificationClosed( WPContribModifMain ):

    def _createTabCtrl( self ):
        self._tabCtrl = wcomponents.TabControl()
        self._tabMain = self._tabCtrl.newTab( "main", _("Main"), "")

    def _getTabContent( self, params ):
        wc = WContribModifClosed()
        return wc.getHTML()


class WContribModWithdraw(wcomponents.WTemplated):

    def __init__(self,contrib):
        self._contrib=contrib

    def getVars(self):
        vars=wcomponents.WTemplated.getVars(self)
        vars["postURL"]=quoteattr(str(urlHandlers.UHContribModWithdraw.getURL(self._contrib)))
        vars["comment"]=self.htmlText("")
        return vars

class WPModWithdraw(WPContribModifMain):

    def _getTabContent(self,params):
        wc=WContribModWithdraw(self._target)
        return wc.getHTML()

class WContribModifAC(wcomponents.WTemplated):

    def __init__( self, contrib ):
        self._contrib = contrib

    def _getManagersList(self):
        result = fossilize(self._contrib.getManagerList())
        # get pending users
        for email in self._contrib.getAccessController().getModificationEmail():
            pendingUser = {}
            pendingUser["email"] = email
            pendingUser["pending"] = True
            result.append(pendingUser)
        return result

    def _getSubmittersList(self):
        result = []
        for submitter in self._contrib.getSubmitterList():
            submitterFossil = fossilize(submitter)
            if isinstance(submitter, Avatar):
                isSpeaker = False
                if self._contrib.getConference().getType() == "conference":
                    isPrAuthor = False
                    isCoAuthor = False
                    if self._contrib.isPrimaryAuthorByEmail(submitter.getEmail()):
                        isPrAuthor = True
                    if self._contrib.isCoAuthorByEmail(submitter.getEmail()):
                        isCoAuthor = True
                    submitterFossil["isPrAuthor"] = isPrAuthor
                    submitterFossil["isCoAuthor"] = isCoAuthor
                if self._contrib.isSpeakerByEmail(submitter.getEmail()):
                    isSpeaker = True
                submitterFossil["isSpeaker"] = isSpeaker
            result.append(submitterFossil)
        # get pending users
        for email in self._contrib.getSubmitterEmailList():
            pendingUser = {}
            pendingUser["email"] = email
            pendingUser["pending"] = True
            result.append(pendingUser)
        return result

    def getVars( self ):
        vars=wcomponents.WTemplated.getVars( self )
        mcf=wcomponents.WModificationControlFrame()
        vars["modifyControlFrame"] = mcf.getHTML(self._contrib)
        acf=wcomponents.WAccessControlFrame()
        visURL=urlHandlers.UHContributionSetVisibility.getURL()

        if isinstance(self._contrib.getOwner(), conference.Session):
            vars["accessControlFrame"]=acf.getHTML(self._contrib, visURL, "InSessionContribution")
        else :
            vars["accessControlFrame"]=acf.getHTML(self._contrib, visURL, "Contribution")

        if not self._contrib.isProtected():
            df=wcomponents.WDomainControlFrame( self._contrib )
            addDomURL=urlHandlers.UHContributionAddDomain.getURL()
            remDomURL=urlHandlers.UHContributionRemoveDomain.getURL()
            vars["accessControlFrame"] += "<br>%s"%df.getHTML(addDomURL,remDomURL)
        vars["confId"] = self._contrib.getConference().getId()
        vars["contribId"] = self._contrib.getId()
        vars["eventType"] = self._contrib.getConference().getType()
        vars["managers"] = self._getManagersList()
        vars["submitters"] = self._getSubmittersList()
        return vars


class WPContribModifAC( WPContributionModifBase ):

    def _setActiveTab( self ):
        self._tabAC.setActive()

    def _getTabContent( self, params ):
        wc=WContribModifAC(self._target)
        return wc.getHTML()


class WPContribModifSC( WPContributionModifBase ):

    def _setActiveTab( self ):
        self._tabSubCont.setActive()


    def _getTabContent( self, params ):

        wc = wcomponents.WContribModifSC( self._target )
        pars = { \
            "moveSubContribURL": urlHandlers.UHSubContribActions.getURL(self._contrib), \
            "addSubContURL": urlHandlers.UHContribAddSubCont.getURL(self._contrib), \
            "subContModifURL": urlHandlers.UHSubContribModification.getURL, \
            "subContUpURL": urlHandlers.UHContribUpSubCont.getURL(), \
            "subContDownURL": urlHandlers.UHContribDownSubCont.getURL()}
        return wc.getHTML( pars )

#-----------------------------------------------------------------------------

class WSubContributionCreation(wcomponents.WTemplated):

    def __init__( self, target ):
        self.__owner = target
        self._contribution = target

    def getVars( self ):
        vars = wcomponents.WTemplated.getVars( self )
        vars["title"] = vars.get("title","")
        vars["description"] = vars.get("description","")
        vars["durationHours"] = vars.get("durationHours","0")
        vars["durationMinutes"] = vars.get("durationMinutes","15")
        vars["keywords"] = vars.get("keywords","")
        vars["locator"] = self.__owner.getLocator().getWebForm()
        vars["authors"] = fossilize(self._contribution.getAllAuthors())
        vars["eventType"] = self._contribution.getConference().getType()
        return vars


class WPContribAddSC( WPContributionModifBase ):

    def _setActiveTab( self ):
        self._tabSubCont.setActive()

    def _getTabContent( self, params ):

        wc = WSubContributionCreation( self._target )
        pars = { \
            "postURL": urlHandlers.UHContribCreateSubCont.getURL()}
        params.update(pars)

        return wc.getHTML( params )


#---------------------------------------------------------------------------

class WPContributionSelectAllowed( WPContribModifAC ):

    def _getTabContent( self, params ):
        searchExt = params.get("searchExt","")
        if searchExt != "":
            searchLocal = False
        else:
            searchLocal = True
        wc = wcomponents.WPrincipalSelection( urlHandlers.UHContributionSelectAllowed.getURL(), forceWithoutExtAuth=searchLocal )
        params["addURL"] = urlHandlers.UHContributionAddAllowed.getURL()
        return wc.getHTML( params )


class WContributionDataModificationBoard(wcomponents.WTemplated):

    def __init__(self):
        pass

    def getVars( self ):
        vars=wcomponents.WTemplated.getVars(self)
        return vars

class WContributionDataModificationType(wcomponents.WTemplated):

    def __init__(self):
        pass

    def getVars( self ):
        vars=wcomponents.WTemplated.getVars(self)
        return vars

class WContributionDataModification(wcomponents.WTemplated):

    def __init__( self, contribution, conf, rh = None ):
        self._contrib = contribution
        self._owner = self._contrib.getOwner()
        self._conf = conf
        self._rh = rh

    def _getTypeItemsHTML(self):
        res = ["""<option value=""></option>"""]
        conf=self._contrib.getConference()
        for type in conf.getContribTypeList():
            selected=""
            if self._contrib.getType()==type:
                selected=" selected"
            res.append("""<option value=%s%s>%s</option>"""%(\
                quoteattr(str(type.getId())),selected,\
                self.htmlText(type.getName())))
        return "".join(res)

    def _getAdditionalFieldsHTML(self):
        html=""
        if self._contrib.getConference().getAbstractMgr().isActive() and \
                self._contrib.getConference().hasEnabledSection("cfa") and \
                self._contrib.getConference().getType() == "conference" and \
                self._contrib.getConference().getAbstractMgr().hasAnyEnabledAbstractField():
            for f in self._contrib.getConference().getAbstractMgr().getAbstractFieldsMgr().getFields():
                if f.isActive():
                    id = f.getId()
                    caption = f.getName()
                    html+="""
                    <tr>
                        <td nowrap class="titleCellTD">
                            <span class="titleCellFormat">%s</span>
                        </td>
                        <td bgcolor="white" width="100%%" valign="top" class="blacktext">
                            <textarea name="%s" cols="65" rows="10">%s</textarea>
                        </td>
                    </tr>"""%(caption, "f_%s"%id, self.htmlText(self._contrib.getField(id)))
        return html

    def getContribId(self):
        if isinstance(self._owner, conference.Session):
            return "s" +  self._owner.id + "c" + self._contrib.id
        else:
            return "c" + self._contrib.id

    def getVars( self ):
        vars = wcomponents.WTemplated.getVars( self )
        defaultDefinePlace = defaultDefineRoom = ""
        defaultInheritPlace = defaultInheritRoom = "checked"
        locationName, locationAddress, roomName, defaultExistRoom = "", "", "",""
        vars["conference"] = self._conf
        vars["boardNumber"]=quoteattr(str(self._contrib.getBoardNumber()))
        vars["contrib"] = self._contrib
        vars["title"] = quoteattr(self._contrib.getTitle())
        vars["description"] = self.htmlText(self._contrib.getDescription())
        vars["additionalFields"] = self._getAdditionalFieldsHTML()
        vars["day"],vars["month"],vars["year"]="","",""
        vars["sHour"],vars["sMinute"]="",""
        sDate=self._contrib.getStartDate()
        if sDate is not None:
            vars["day"]=quoteattr(str(sDate.day))
            vars["month"] = quoteattr(str(sDate.month))
            vars["year"] = quoteattr(str(sDate.year))
            vars["sHour"] = quoteattr(str(sDate.hour))
            vars["sMinute"] = quoteattr(str(sDate.minute))
        if self._contrib.getStartDate():
            vars["dateTime"] = formatDateTime(self._contrib.getAdjustedStartDate())
        else:
            vars["dateTime"] = ""
        vars["duration"] = self._contrib.getDuration().seconds/60
        if self._contrib.getDuration() is not None:
            vars["durationHours"]=quoteattr(str((datetime(1900,1,1)+self._contrib.getDuration()).hour))
            vars["durationMinutes"]=quoteattr(str((datetime(1900,1,1)+self._contrib.getDuration()).minute))
        if self._contrib.getOwnLocation():
            defaultDefinePlace = "checked"
            defaultInheritPlace = ""
            locationName = self._contrib.getLocation().getName()
            locationAddress = self._contrib.getLocation().getAddress()

        if self._contrib.getOwnRoom():
            defaultDefineRoom= "checked"
            defaultInheritRoom = ""
            defaultExistRoom=""
            roomName = self._contrib.getRoom().getName()
        vars["defaultInheritPlace"] = defaultInheritPlace
        vars["defaultDefinePlace"] = defaultDefinePlace
        vars["confPlace"] = ""
        confLocation = self._owner.getLocation()
        if self._contrib.isScheduled():
            confLocation=self._contrib.getSchEntry().getSchedule().getOwner().getLocation()
        if self._contrib.getSession() and not self._contrib.getConference().getEnableSessionSlots():
            confLocation = self._contrib.getSession().getLocation()
        if confLocation:
            vars["confPlace"] = confLocation.getName()
        vars["locationName"] = locationName
        vars["locationAddress"] = locationAddress
        vars["defaultInheritRoom"] = defaultInheritRoom
        vars["defaultDefineRoom"] = defaultDefineRoom
        vars["defaultExistRoom"] = defaultExistRoom
        vars["confRoom"] = ""
        confRoom = self._owner.getRoom()
        rx=[]
        roomsexist = self._conf.getRoomList()
        roomsexist.sort()
        for room in roomsexist:
            sel=""
            rx.append("""<option value=%s%s>%s</option>"""%(quoteattr(str(room)),
                        sel,self.htmlText(room)))
        vars ["roomsexist"] = "".join(rx)
        if self._contrib.isScheduled():
            confRoom=self._contrib.getSchEntry().getSchedule().getOwner().getRoom()
        if self._contrib.getSession() and not self._contrib.getConference().getEnableSessionSlots():
            confRoom = self._contrib.getSession().getRoom()
        if confRoom:
            vars["confRoom"] = confRoom.getName()
        vars["roomName"] = quoteattr(roomName)
        vars["parentType"] = "conference"
        if self._contrib.getSession() is not None:
            vars["parentType"] = "session"
            if self._contrib.isScheduled() and self._contrib.getConference().getEnableSessionSlots():
                vars["parentType"]="session slot"
        vars["postURL"] = urlHandlers.UHContributionDataModif.getURL(self._contrib)
        vars["types"]=self._getTypeItemsHTML()
        vars["keywords"]=self._contrib.getKeywords()
        import MaKaC.webinterface.webFactoryRegistry as webFactoryRegistry
        wr = webFactoryRegistry.WebFactoryRegistry()
        wf = wr.getFactory(self._conf)
        if wf != None:
            type = wf.getId()
        else:
            type = "conference"
        if type == "conference":
            vars["Type"]=WContributionDataModificationType().getHTML(vars)
            vars["Board"]=WContributionDataModificationBoard().getHTML(vars)
        else:
            vars["Type"]=""
            vars["Board"]=""

        minfo = info.HelperMaKaCInfo.getMaKaCInfoInstance()
        vars["useRoomBookingModule"] = minfo.getRoomBookingModuleActive()
        if self._contrib.getSession():
            vars["sessionType"] = self._contrib.getSession().getScheduleType()
        else:
            vars["sessionType"] = 'none'
        return vars


class WPEditData(WPContribModifMain):

    def _getTabContent( self, params ):
        wc = WContributionDataModification(self._target, self._conf)

        pars = {"postURL": urlHandlers.UHConfPerformAddContribution.getURL(), \
        "calendarIconURL": Config.getInstance().getSystemIconURL( "calendar" ), \
        "calendarSelectURL":  urlHandlers.UHSimpleCalendar.getURL() }
        return wc.getHTML( pars )


class WPContribAddMaterial( WPContribModifMain ):

    def __init__( self, rh, contrib, mf ):
        WPContribModifMain.__init__( self, rh, contrib )
        self._mf = mf

    def _getTabContent( self, params ):
        if self._mf:
            comp = self._mf.getCreationWC( self._target )
        else:
            comp = wcomponents.WMaterialCreation( self._target )
        pars = { "postURL": urlHandlers.UHContributionPerformAddMaterial.getURL() }
        return comp.getHTML( pars )

class WPContributionDeletion( WPContributionModifTools ):

    def _getTabContent( self, params ):
        wc = wcomponents.WContributionDeletion( [self._target] )
        return wc.getHTML( urlHandlers.UHContributionDelete.getURL( self._target ) )


class WContributionMove(wcomponents.WTemplated):

    def __init__(self, contrib, conf ):
        self._contrib = contrib
        self._conf = conf

    def getVars( self ):
        vars = wcomponents.WTemplated.getVars( self )
        sesList = ""
        if self._contrib.getOwner() != self._conf:
            sesList = i18nformat("""<option value=\"CONF\" > _("Conference") : %s</option>\n""")%self._conf.getTitle()
        for ses in self._conf.getSessionListSorted():
            if self._contrib.getOwner() != ses:
                sesList = sesList + i18nformat("""<option value=\"%s\" > _("Session") : %s</option>\n""")%(ses.getId(), ses.getTitle())
        vars["sessionList"] = sesList
        vars["confId"] = self._conf.getId()
        vars["contribId"] = self._contrib.getId()
        return vars


class WPcontribMove( WPContributionModifTools ):

    def _getTabContent( self, params ):
        wc = WContributionMove( self._target, self._target.getConference() )
        params["cancelURL"] = urlHandlers.UHContribModifTools.getURL( self._target )
        params["moveURL"] = urlHandlers.UHContributionPerformMove.getURL()
        return wc.getHTML( params )


class WPContributionDisplayRemoveMaterialsConfirm( WPContributionDefaultDisplayBase ):

    def __init__(self,rh, conf, mat):
        WPContributionDefaultDisplayBase.__init__(self,rh,conf)
        self._mat=mat

    def _getBody(self,params):
        wc=wcomponents.WDisplayConfirmation()
        msg= i18nformat(""" _("Are you sure you want to delete the following material")?<br>
        <b><i>%s</i></b>
        <br>""")%self._mat.getTitle()
        url=urlHandlers.UHContributionDisplayRemoveMaterial.getURL(self._mat.getOwner())
        return wc.getHTML(msg,url,{"deleteMaterial":self._mat.getId()})

class WPContributionReportNumberEdit(WPContributionModifBase):

    def __init__(self, rh, contribution, reportNumberSystem):
        WPContributionModifBase.__init__(self, rh, contribution)
        self._reportNumberSystem=reportNumberSystem

    def _getTabContent( self, params):
        wc=wcomponents.WModifReportNumberEdit(self._target, self._reportNumberSystem, "contribution")
        return wc.getHTML()
