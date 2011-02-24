#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

# Python
import logging
import stat
import sys
import os
import time
import unittest
import shutil

try:
    import json
except ImportError:
    import simplejson as json

# Pulp
srcdir = os.path.abspath(os.path.dirname(__file__)) + "/../../src/"
sys.path.insert(0, srcdir)

commondir = os.path.abspath(os.path.dirname(__file__)) + '/../common/'
sys.path.insert(0, commondir)

import pymongo.json_util

from pulp.server.api.package import PackageApi
from pulp.server.api.repo import RepoApi
from pulp.server.db.model import RepoSource
from pulp.server.util import random_string
from pulp.server.util import get_rpm_information
from pulp.client.utils import generatePakageProfile
from pulp.server.util import top_repos_location
from pulp.server.auth.cert_generator import SerialNumber
from pulp.server import constants
from pulp.server.pexceptions import PulpException
import testutil

logging.root.setLevel(logging.ERROR)
qpid = logging.getLogger('qpid.messaging')
qpid.setLevel(logging.ERROR)

class TestYumRepoSync(unittest.TestCase):

    def clean(self):
        self.rapi.clean()
        self.papi.clean()
        testutil.common_cleanup()
        shutil.rmtree(constants.LOCAL_STORAGE, ignore_errors=True)
        sn = SerialNumber()
        sn.reset()

    def setUp(self):
        self.config = testutil.load_test_config()
        self.data_path = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        self.rapi = RepoApi()
        self.papi = PackageApi()
        self.clean()

    def tearDown(self):
        self.clean()

    
    def test_local_sync_callback(self):
        # We need report to be accesible for writing by the callback
        global report
        report = None
        def callback(r):
            global report
            report = r
        repo = self.rapi.create('some-id', 'some name', 'i386',
                'yum:http://jmatthews.fedorapeople.org/repo_resync_a')
        self.rapi._sync(repo['id'], progress_callback=callback)
        found = self.rapi.repository(repo['id'])
        packages = found['packages']
        print report

        self.assertTrue(packages is not None)
        self.assertTrue(len(packages) == 3)
        self.assertEqual(report["num_download"], 3)
        self.assertEqual(report["num_error"], 0)
        self.assertEqual(report["num_success"], 3)
        self.assertEqual(report["items_total"], 3)
        self.assertEqual(report["size_left"], 0)
        self.assertEqual(report["items_left"], 0)
        self.assertEqual(report["size_total"], 6791)
        rpm_details = report["details"]["rpm"]
        self.assertEqual(rpm_details["total_count"], 3)
        self.assertEqual(rpm_details["num_error"], 0)
        self.assertEqual(rpm_details["num_success"], 3)
        self.assertEqual(rpm_details["items_left"], 0)
        self.assertEqual(rpm_details["total_size_bytes"], 6791)
        self.assertEqual(rpm_details["size_left"], 0)

if __name__ == '__main__':
    unittest.main()
