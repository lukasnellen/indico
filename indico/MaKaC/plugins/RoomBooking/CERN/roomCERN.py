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

from MaKaC.plugins.RoomBooking.default.room import Room

# Branch name in ZODB root
_ROOMS = 'Rooms'

class RoomCERN( Room ):
    """
    ZODB specific implementation.

    For documentation of methods see base class.
    """

    vcList = ["Built-in (MCU) Bridge",
              "Vidyo",
              "EVO",
              "ESnet MCU",
              "CERN MCU",
              "H323 point2point",
              "Audio Conference",
              "I don't know"]

    def __eq__( self, other ):
        try:
            if self.id != None  and  other.id != None:
                return self.id == other.id
            else:
                return self.name == other.name and self.building == other.building \
                    and self.floor == other.floor and self.locationName == other.locationName

        except AttributeError:
            if self is None and other is None:
                return True
            else:
                return False

