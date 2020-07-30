import unittest
import os
import sys
import io
import contextlib
import copy

import yaml
import boto3

from botocore.stub import Stubber

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
from badjware.v1.ssmparameterplaceholdertransformer import plugin


class TestSSMParameterPlaceholderTransformer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_wd = os.getcwd()
        # change workdir
        os.chdir('tests/plugins/kustomize/ssmparameterplaceholdertransformer')

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

    def test_ssmparameterplaceholdertransformer(self):
        plugin_input = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: ${ssm:foo}
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
            sys.argv.append('ssm-example.yaml')
            self.stdin.write(plugin_input)
            self.stdin.seek(0)
            with Stubber(plugin.ssm) as stubber:
                stubber.add_response(
                    'get_parameter',
                    {
                        'Parameter': {
                            'Value': 'my_secret'
                        },
                    },
                    {
                        'Name': 'foo',
                        'WithDecryption': True
                    },
                )
                plugin.run_plugin()

        self.assertEqual(yaml.safe_load(stdout.getvalue()), yaml.safe_load(expected_result))
