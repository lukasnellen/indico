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

import time, contextlib, dateutil

from indico.ext.livesync import SyncManager, db
from indico.tests.python.unit.util import IndicoTestFeature
from indico.util.date_time import nowutc, int_timestamp
from indico.ext.livesync.tasks import LiveSyncUpdateTask

FAKE_SERVICE_PORT = 12380

class LiveSync_Feature(IndicoTestFeature):
    _requires = ['plugins.Plugins', 'util.ContextManager', 'db.Database']

    def start(self, obj):
        super(LiveSync_Feature, self).start(obj)

        with obj._context('database') as conn:
            obj._ph.getPluginType('livesync').toggleActive()
            db.updateDBStructures(conn.root._root, granularity=1)

            obj._sm = SyncManager.getDBInstance()

    def destroy(self, obj):
        super(LiveSync_Feature, self).destroy(obj)


class _TestSynchronization(object):

    _requires = ['db.DummyUser', LiveSync_Feature, 'util.RequestEnvironment']

    def _prettyActions(self, iter):

        def friendlyAction(a):
            return (a._obj, ' '.join(sorted(a._actions)))

        return set(list(friendlyAction(a) for a in iter))

    def _nextTS(self):
        time.sleep(1)
        return int_timestamp(nowutc())

    def checkActions(self, fromTS, expected):
        res = self._prettyActions(
            self._sm.getTrack().iterate(fromTS - 1, func=(lambda x: x[1])))

        self.assertEqual(expected, res)


class _TUpload(object):

    _requires = ['db.DummyUser', LiveSync_Feature, 'util.RequestEnvironment']

    @contextlib.contextmanager
    def _generateTestResult(self):

        global FAKE_SERVICE_PORT

        self._recordSet = dict()

        fakeInvenio = self._server('', FAKE_SERVICE_PORT, self._recordSet)

        agent = self._agent('test1', 'test1', 'test',
                            0, url = 'http://localhost:%s' % \
                            FAKE_SERVICE_PORT)

        with self._context('database', 'request'):
            self._sm.registerNewAgent(agent)
            agent.preActivate(0)
            agent.setActive(True)
            # execute code
            yield

        fakeInvenio.start()

        # params won't be used
        task = LiveSyncUpdateTask(dateutil.rrule.MINUTELY)

        time.sleep(3)

        try:
            with self._context('database'):
                task.run()
        finally:
            fakeInvenio.shutdown()
            fakeInvenio.join()

            # can't reuse the same port, as the OS won't have it free
            FAKE_SERVICE_PORT += 1

    def testSmallUpload(self):
        """
        Tests uploading multiple records (small)
        """
        with self._generateTestResult():
            conf1 = self._home.newConference(self._dummy)
            conf1.setTitle('Test Conference 1')
            conf2 = self._home.newConference(self._dummy)
            conf2.setTitle('Test Conference 2')

        self.assertEqual(
            self._recordSet,
            {
                'INDICO.0': {'title': 'Test Conference 1'},
                'INDICO.1': {'title': 'Test Conference 2'}
                })

    def testLargeUpload(self):
        """
        Tests uploading multiple records (large)
        """
        with self._generateTestResult():
            for nconf in range(0, 100):
                conf = self._home.newConference(self._dummy)
                conf.setTitle('Test Conference %s' % nconf)

        self.assertEqual(
            self._recordSet,
            dict(('INDICO.%s' % nconf,
                  {'title': 'Test Conference %s' % nconf}) \
                 for nconf in range(0, 100)))
