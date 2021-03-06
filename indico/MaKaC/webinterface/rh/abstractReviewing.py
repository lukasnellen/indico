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


from MaKaC.webinterface.rh.conferenceModif import RHConfModifCFABase
import MaKaC.webinterface.urlHandlers as urlHandlers
import MaKaC.review as review
from MaKaC.webinterface.pages.abstractReviewing import WPAbstractReviewingSetup, WPAbstractReviewingTeam, WPModCFANotifTplNew, \
    WPConfModifAbstractsReviewingNotifTplList, NotifTplToAddrsFactory, NotifTplConditionsFactory, WPModCFANotifTplPreview, \
    WPModCFANotifTplDisplay, WPModCFANotifTplEdit
from MaKaC.webinterface.locators import WebLocator
from MaKaC.webinterface.common.abstractNotificator import EmailNotificator



class RHAbstractReviewingSetup(RHConfModifCFABase):

    def _process(self):
        p = WPAbstractReviewingSetup(self, self._target)
        return p.display()

class RHAbstractReviewingTeam(RHConfModifCFABase):

    def _process(self):
        p = WPAbstractReviewingTeam(self, self._target)
        return p.display()


class RHNotifTpl(RHConfModifCFABase):

    def _process(self):
        p = WPConfModifAbstractsReviewingNotifTplList(self, self._target)
        return p.display()


class RHCFANotifTplNew(RHConfModifCFABase):

    def _checkParams( self, params):
        RHConfModifCFABase._checkParams( self, params)
        self._title = params.get("title", "")
        self._description = params.get("description","")
        self._subject = params.get("subject","")
        self._body = params.get("body","")
        self._fromAddr = params.get("fromAddr","")
        self._toList = self._normaliseListParam(params.get("toAddrs",[]))
        auxCCList = params.get("CCAddrs","")
        # replace to have only one separator
        auxCCList = auxCCList.replace(" ", ",").replace(";", ",").split(",")
        # clean the list in order to avoid empty emails, for instance, comma at the end
        cleanList = []
        for email in auxCCList:
            if email != "":
                cleanList.append(email)
        self._ccList = cleanList
        self._CAasCCAddr = params.has_key("CAasCCAddr")
        self._cancel = params.get("cancel", None)
        self._save = params.get("save", None)
        self._tplCondition = params.get("condType", None)
        # If the condition is accepted, get the contribution type id and the track id parameters, otherwise set them by default
        if self._tplCondition == "accepted":
            cTypeId = params.get("contribType", "")
            track = params.get("track", "--any--")
        else:
            cTypeId = ""
            track = "--any--"
        if cTypeId in ("--none--", "--any--", ""):
            cType = cTypeId
        else:
            cType = self._conf.getContribTypeById(cTypeId)
        if track not in ["--any--", "--none--"]:
            track = self._conf.getTrackById(track)
        self._otherData = {"contribType":cType, "track":track}

    def _process(self):
        error = []
        if self._cancel:
            self._redirect(urlHandlers.UHAbstractReviewingNotifTpl.getURL( self._conf )  )
            return
        elif self._save:
            if len(self._toList) <= 0:
                error.append( _("""At least one "To Address" must be selected"""))
            elif self._tplCondition is None:
                #TODO: translate
                error.append( _("Choose a condition"))
            else:
                tpl = review.NotificationTemplate()
                tpl.setName(self._title)
                tpl.setDescription(self._description)
                tpl.setTplSubject(self._subject, EmailNotificator.getVarList())
                tpl.setTplBody(self._body, EmailNotificator.getVarList())
                tpl.setFromAddr(self._fromAddr)
                tpl.setCCAddrList(self._ccList)
                tpl.setCAasCCAddr(self._CAasCCAddr)

                for toAddr in self._toList:
                    toAddrWrapper = NotifTplToAddrsFactory.getToAddrById(toAddr)
                    if toAddrWrapper:
                        toAddrWrapper.addToAddr(tpl)
                self._conf.getAbstractMgr().addNotificationTpl(tpl)

                # Add the condition
                condWrapper = NotifTplConditionsFactory.getConditionById(self._tplCondition)
                if condWrapper:
                    condWrapper.addCondition(tpl, **self._otherData)
                self._redirect(urlHandlers.UHAbstractModNotifTplDisplay.getURL(tpl))
                return
        p = WPModCFANotifTplNew(self,self._target)
        return p.display(title = self._title,\
                        description = self._description,\
                        subject = self._subject,\
                        body = self._body,\
                        fromAddr = self._fromAddr,\
                        toList = self._toList,\
                        ccList = self._ccList,\
                        errorList = error)


class RHCFANotifTplRem(RHConfModifCFABase):

    def _checkParams( self, params):
        RHConfModifCFABase._checkParams( self, params)
        self._tplIds = self._normaliseListParam( params.get( "selTpls", [] ) )

    def _process(self):
        absMgr = self._conf.getAbstractMgr()
        for id in self._tplIds:
            tpl = absMgr.getNotificationTplById(id)
            absMgr.removeNotificationTpl(tpl)
        self._redirect(urlHandlers.UHAbstractReviewingNotifTpl.getURL(self._conf))


class RHNotificationTemplateModifBase(RHConfModifCFABase):

    def _checkParams( self, params):
        RHConfModifCFABase._checkParams( self, params)
        l = WebLocator()
        l.setNotificationTemplate(params)
        self._notifTpl = self._target = l.getObject()


class RHCFANotifTplUp(RHNotificationTemplateModifBase):

    def _process(self):
        self._conf.getAbstractMgr().moveUpNotifTpl(self._target)
        self._redirect(urlHandlers.UHAbstractReviewingNotifTpl.getURL(self._conf))


class RHCFANotifTplDown(RHNotificationTemplateModifBase):

    def _process(self):
        self._conf.getAbstractMgr().moveDownNotifTpl(self._target)
        self._redirect(urlHandlers.UHAbstractReviewingNotifTpl.getURL(self._conf))


class RHCFANotifTplDisplay(RHNotificationTemplateModifBase):

    def _process(self):
        p = WPModCFANotifTplDisplay(self, self._target)
        return p.display()


class RHCFANotifTplPreview(RHNotificationTemplateModifBase):

    def _process(self):
        p = WPModCFANotifTplPreview(self, self._target)
        return p.display()


class RHCFANotifTplEdit(RHNotificationTemplateModifBase):

    def _checkParams( self, params):
        RHNotificationTemplateModifBase._checkParams(self, params)
        self._cancel=params.get("cancel", None)
        self._save=params.get("save", None)
        if self._save is not None:
            self._title=params.get("title", "")
            self._description=params.get("description","")
            self._subject=params.get("subject","")
            self._body=params.get("body","")
            self._fromAddr=params.get("fromAddr","")
            self._toList=self._normaliseListParam(params.get("toAddrs",[]))
            auxCCList = params.get("CCAddrs","")
            # replace to have only one separator
            auxCCList = auxCCList.replace(" ", ",").replace(";", ",").split(",")
            # clean the list in order to avoid empty emails, for instance, comma at the end
            cleanList = []
            for email in auxCCList:
                if email != "":
                    cleanList.append(email)
            self._ccList = cleanList
            self._CAasCCAddr = params.get("CAasCCAddr","")

    def _process(self):
        error=[]
        if self._cancel:
            self._redirect(urlHandlers.UHAbstractModNotifTplDisplay.getURL(self._target))
            return
        elif self._save:
            if len(self._toList)<=0:
                error.append( _("""At least one "To Address" must be seleted """))
                p=WPModCFANotifTplEdit(self, self._target)
                return p.display(errorList=error, \
                                    title=self._title, \
                                    subject=self._subject, \
                                    body=self._body, \
                                    fromAddr=self._fromAddr, \
                                    toList=self._toList, \
                                    ccList=self._ccList)
            else:
                self._notifTpl.setName(self._title)
                self._notifTpl.setDescription(self._description)
                self._notifTpl.setTplSubject(self._subject, EmailNotificator.getVarList())
                self._notifTpl.setTplBody(self._body, EmailNotificator.getVarList())
                self._notifTpl.setFromAddr(self._fromAddr)
                self._notifTpl.setCCAddrList(self._ccList)
                self._notifTpl.setCAasCCAddr(self._CAasCCAddr)
                self._notifTpl.clearToAddrs()
                for toAddr in self._toList:
                    toAddrWrapper=NotifTplToAddrsFactory.getToAddrById(toAddr)
                    if toAddrWrapper:
                        toAddrWrapper.addToAddr(self._notifTpl)
                self._redirect(urlHandlers.UHAbstractModNotifTplDisplay.getURL(self._target))
                return
        else:
            p=WPModCFANotifTplEdit(self, self._target)
            return p.display()


class RHNotifTplConditionNew(RHNotificationTemplateModifBase):

    def _checkParams(self,params):
        RHNotificationTemplateModifBase._checkParams(self,params)
        self._action = "OK"
        if params.has_key("CANCEL"):
            self._action = "CANCEL"
        self._condType = params.get("condType", None)
        # If the condition is accepted, get the contribution type id and the track id parameters, otherwise set them by default
        if self._condType == "accepted":
            cTypeId = params.get("contribType", "")
            track = params.get("track", "--any--")
        else:
            cTypeId = ""
            track = "--any--"
        if cTypeId in ("--none--", "--any--", ""):
            cType = cTypeId
        else:
            cType = self._target.getConference().getContribTypeById(cTypeId)
        if track not in ["--any--", "--none--"]:
            track = self._target.getConference().getTrackById(track)
        self._otherData = {"contribType":cType, "track":track}

    def _process(self):
        if self._action == "OK":
            condWrapper = NotifTplConditionsFactory.getConditionById(self._condType)
            if condWrapper:
                condWrapper.addCondition(self._target,**self._otherData)
        self._redirect(urlHandlers.UHAbstractModNotifTplDisplay.getURL(self._target))


class RHNotifTplConditionRem(RHNotificationTemplateModifBase):

    def _checkParams(self,params):
        RHNotificationTemplateModifBase._checkParams(self,params)
        self._conds=[]
        for id in self._normaliseListParam(params.get("selCond",[])):
            cond=self._target.getConditionById(id)
            if cond:
                self._conds.append(cond)

    def _process(self):
        for cond in self._conds:
            self._target.removeCondition(cond)
        self._redirect(urlHandlers.UHAbstractModNotifTplDisplay.getURL(self._target))



