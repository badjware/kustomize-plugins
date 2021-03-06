import unittest
import os
import sys
import io
import contextlib

import yaml

from badjware.v1.placeholdertransformer import plugin

class TestPlaceholderTransformer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_wd = os.getcwd()
        # change workdir
        os.chdir('tests/plugins/kustomize/placeholdertransformer')

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

    def test_placeholdertransformer(self):
        plugin_input = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: ${foo}
            bar: ${bar}
        """
        expected_result = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: my_first_placeholder
            bar: my_second_placeholder
        """

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            sys.argv.append('placeholder-example.yaml')
            self.stdin.write(plugin_input)
            self.stdin.seek(0)
            plugin.run_plugin()

        self.assertEqual(yaml.safe_load(stdout.getvalue()), yaml.safe_load(expected_result))
