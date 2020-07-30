import unittest
import os
import sys
import io
import contextlib
import copy

import yaml

from badjware.v1.environmentplaceholdertransformer import plugin

class TestEnvironmentPlaceholderTransformer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_wd = os.getcwd()
        # change workdir
        os.chdir('tests/plugins/kustomize/environmentplaceholdertransformer')

    def setUp(self):
        self.stdin = io.StringIO()
        sys.stdin = self.stdin
        self.old_environ = copy.deepcopy(os.environ)

    def tearDown(self):
        sys.stdin = sys.__stdin__
        sys.argv = sys.argv[1:]
        os.environ = self.old_environ

    @classmethod
    def tearDownClass(cls):
        # restore workdir
        os.chdir(cls.old_wd)

    def test_environmentplaceholdertransformer(self):
        plugin_input = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: ${env:foo}
        """
        expected_result = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: my_secret
        """

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            sys.argv.append('env-example.yaml')
            self.stdin.write(plugin_input)
            self.stdin.seek(0)
            os.environ['foo'] = 'my_secret'
            plugin.run_plugin()

        self.assertEqual(yaml.safe_load(stdout.getvalue()), yaml.safe_load(expected_result))
