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

# pylint: disable-msg=W0611

"""
indico.tests provides a common framework for all the different libraries and
technologies used for different types of testing.

 * Python/JS Unit Tests - using nosetest and JSUnit
 * Python Coverage Tests - using figleaf
 * Functional Tests - using selenium, nose and selenium grid
 * Code conventions, standards, smells - Pylint and JSlint

"""

# API classes
from indico.tests.config import TestConfig
from indico.tests.core import TestManager, UnitTestRunner, TEST_RUNNERS
from indico.tests.base import BaseTestRunner
