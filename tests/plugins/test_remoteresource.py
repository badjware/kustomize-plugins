import unittest
import os
import sys
import io
import contextlib

import yaml

from badjware.v1.remoteresources import plugin

class TestRemoteResources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_wd = os.getcwd()
        # change workdir
        os.chdir('tests/plugins/kustomize/remoteresources')

    @classmethod
    def tearDownClass(cls):
        # restore workdir
        os.chdir(cls.old_wd)

    def setUp(self):
        self.stdin = io.StringIO()
        sys.stdin = self.stdin

    def tearDown(self):
        sys.stdin = sys.__stdin__
        sys.argv = sys.argv[1:]

    def test_remoteresources_valid(self):
        expected_result = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: bar
        """

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            sys.argv.append('remoteresources-example.yaml')
            plugin.run_plugin()

        self.assertEqual(yaml.safe_load(stdout.getvalue()), yaml.safe_load(expected_result))

    def test_remoteresources_invalid(self):
        with self.assertRaises(Exception):
            sys.argv.append('remoteresources-example-invalid.yaml')
            plugin.run_plugin()
