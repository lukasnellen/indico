# -*- coding: utf-8 -*-
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

# pylint: disable-msg=W0401

"""
This is the very core of indico.tests
Here is defined the TestManager class, that provides a single point of access
to the outside world.
"""

# System modules
import os, sys, shutil, signal, commands, tempfile, pkg_resources

# Database
import transaction
from MaKaC.common.db import DBMgr

# Indico
import indico
from indico.util.console import colored
from indico.tests.config import TestConfig
from indico.tests.base import TestOptionException, FakeMailThread
from indico.tests.runners import *

# Indico legacy
from MaKaC.common.Configuration import Config

TEST_RUNNERS = {'unit': UnitTestRunner,
                'functional': FunctionalTestRunner,
                'pylint': PylintTestRunner,
                'jsunit': JSUnitTestRunner,
                'jslint': JSLintTestRunner,
                'grid': GridTestRunner}


class TestManager(object):
    """
    Main class, the heart of the test API.
    Launches all the tests according to the parameters that are passed
    """

    __instance = None

    def __init__(self):
        """
        Initializes the object
        """
        self.dbmgr = None
        self.zeoServer = None
        self.tempDirs = {}
        self.dbFolder = None

    @staticmethod
    def _title(text):
        """
        Prints an title
        """
        print colored("-- " + str(text), 'yellow', attrs=['bold'])

    @staticmethod
    def _info(message):
        """
        Prints an info message
        """
        print colored("-- " + str(message), 'cyan')

    @staticmethod
    def _error(message):
        """
        Prints an info message
        """
        print colored("-- " + str(message), 'red')

    @staticmethod
    def _debug(message):
        """
        Prints an info message
        """
        print colored("-- " + str(message), 'grey')

    def main(self, testsToRun, options):
        """
        Runs the main test cycle, iterating over all the TestRunners available

         * testsToRun - a list of strings specifying which tests to run
         * options - test options (such as verbosity...)
        """
        result = False
        killself = options.pop('killself', False)

        TestManager._title("Starting test framework\n")

        self._setFakeConfig()
        self._startSMTPServer()
        self._startManageDB()

        try:
            for test in testsToRun:
                if test in TEST_RUNNERS:
                    try:
                        result = TEST_RUNNERS[test](**options).run()
                    except TestOptionException, e:
                        TestManager._error(e)
                else:
                    print colored("[ERR] Test set '%s' does not exist. "
                                  "It has to be added in the TEST_RUNNERS variable\n",
                                  'red') % test
        finally:
            # whatever happens, clean this mess up
            self._stopManageDB(killself)
            self._stopSMTPServer()

        if killself:
            # Forcefully kill ourselves. This avoids waiting for the db to shutdown (SLOW)
            self._info('Committing suicide to avoid waiting for slow database shutdown')
            os.kill(os.getpid(), 9)

        if result:
            return 0
        else:
            return -1

    def _setFakeConfig(self):
        """
        Sets a fake configuration for the current process, using a temporary directory
        """
        config = Config.getInstance()

        temp = tempfile.mkdtemp(prefix="indico_")
        self._info('Using %s as temporary dir' % temp)

        os.mkdir(os.path.join(temp, 'log'))
        os.mkdir(os.path.join(temp, 'archive'))

        indicoDist = pkg_resources.get_distribution('indico')
        htdocsDir = indicoDist.get_resource_filename('indico', 'indico/htdocs')
        etcDir = indicoDist.get_resource_filename('indico', 'etc')

        # set defaults
        config.reset({
            'BaseURL': 'http://localhost:8000',
            'BaseSecureURL': 'http://localhost:8000',
            'UseXSendFile': False,
            'AuthenticatorList': ['Local'],
            'SmtpServer': ('localhost', 58025),
            'SmtpUseTLS': 'no',
            'DBConnectionParams': ('localhost', TestConfig.getInstance().getFakeDBPort()),
            'LogDir': os.path.join(temp, 'log'),
            'XMLCacheDir': os.path.join(temp, 'cache'),
            'HtdocsDir': htdocsDir,
            'ArchiveDir': os.path.join(temp, 'archive'),
            'UploadedFilesTempDir': os.path.join(temp, 'tmp'),
            'ConfigurationDir': etcDir
            })

        Config.setInstance(config)
        self._cfg = config

        # re-configure logging and template generator, so that paths are updated
        from MaKaC.common import TemplateExec
        from MaKaC.common.logger import Logger
        TemplateExec.mako = TemplateExec._define_lookup()
        Logger.reset()


################## Start of DB Managing functions ##################
    def _startManageDB(self):
        port = TestConfig.getInstance().getFakeDBPort()

        self._info("Starting fake DB in port %s" % port)
        self._startFakeDB('localhost', port)

    def _stopManageDB(self, killself=False):
        """
        Stops the temporary DB
        """
        self._stopFakeDB(killself)

    def _startFakeDB(self, zeoHost, zeoPort):
        """
        Starts a temporary DB in a different port
        """

        print colored("-- Starting a test DB", "cyan")

        self._createNewDBFile()
        self.zeoServer = TestManager._createDBServer(
            os.path.join(self.dbFolder, "Data.fs"),
            zeoHost, zeoPort)

    def _stopFakeDB(self, killself=False):
        """
        Stops the temporary DB
        """

        print colored("-- Stopping test DB", "cyan")

        try:
            self.zeoServer.shutdown(killself)
            self._removeDBFile()
        except OSError, e:
            print ("Problem terminating ZEO Server: " + str(e))

    def _createNewDBFile(self):
        """
        Creates a new DB file for a temporary DB
        """
        from ZODB import FileStorage, DB
        savedDir = os.getcwd()
        self.dbFolder = tempfile.mkdtemp()
        os.chdir(self.dbFolder)

        storage = FileStorage.FileStorage("Data.fs")
        db = DB(storage)
        connection = db.open()

        transaction.commit()

        connection.close()
        db.close()
        storage.close()
        os.chdir(savedDir)

    def _removeDBFile(self):
        """
        Removes the files of the temporary DB
        """
        shutil.rmtree(self.dbFolder)

    @classmethod
    def _startSMTPServer(cls):
        cls._smtpd = FakeMailThread(('localhost', 58025))
        cls._smtpd.start()

    @classmethod
    def _stopSMTPServer(cls):
        cls._smtpd.close()

    @staticmethod
    def _createDBServer(dbFile, host, port):
        """
        Creates a fake DB server for testing
        """

        # run a DB in a child process
        from indico.tests.util import TestZEOServer
        server = TestZEOServer(port, dbFile, hostname = host)
        server.daemon = True
        server.start()
        return server

################## End of DB Managing functions ##################
