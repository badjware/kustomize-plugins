import unittest
import os
import subprocess

import yaml

class TestExec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_wd = os.getcwd()
        # change workdir
        os.chdir('tests/plugins/kustomize/exec')

    @classmethod
    def tearDownClass(cls):
        # restore workdir
        os.chdir(cls.old_wd)

    def test_exec(self):
        expected_results = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: example-configmap
        data:
            foo: bar
        """

        p = subprocess.run(['../../../../badjware/v1/exec/Exec', 'exec-example.yaml'],
            stdout=subprocess.PIPE,
            encoding='utf8',
            check=True)

        self.assertEqual(yaml.safe_load(p.stdout), yaml.safe_load(expected_results))
