import unittest
import io
import contextlib
import copy
import re
import base64

import badjware.v1.common as c

class TestCommon(unittest.TestCase):
    def setUp(self):
        self.configmap_resource = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': 'example-configmap',
                'namespace': 'example',
                'labels': {
                    'foo': 'bar',
                },
            },
            'data': {},
        }
        self.secret_resource = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': 'example-secret',
                'namespace': 'example',
                'labels': {
                    'foo': 'bar',
                },
            },
            'data': {},
        }
        self.deployment_resource = {
            'apiVersion': 'app/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'example-deployment',
                'namespace': 'example',
                'labels': {
                    'foo': 'bar',
                },
            },
            'spec': {}, # not important for the purpose of the test
        }
        self.placeholder_prog = re.compile('(foo)')

    def test_eprint(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with contextlib.redirect_stderr(stderr):
                c.eprint('foo')

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), 'foo\n')
    
    def test_resource_match_selectors_nogroup_all(self):
        configmap_resource = copy.deepcopy(self.configmap_resource)
        is_match, match_metadata = c.resource_match_selectors(configmap_resource, [])

        self.assertTrue(is_match)
        self.assertDictEqual(self.configmap_resource, configmap_resource)
        self.assertDictEqual({
            'group': '',
            'version': 'v1',
            'kind': 'ConfigMap',
            'name': 'example-configmap',
            'namespace': 'example',
        }, match_metadata)

    def test_resource_match_selectors_group_all(self):
        deployment_resource = copy.deepcopy(self.deployment_resource)
        is_match, match_metadata = c.resource_match_selectors(deployment_resource, [])

        self.assertTrue(is_match)
        self.assertDictEqual(self.deployment_resource, deployment_resource)
        self.assertDictEqual({
            'group': 'app',
            'version': 'v1',
            'kind': 'Deployment',
            'name': 'example-deployment',
            'namespace': 'example',
        }, match_metadata)
    
    def test_resource_match_kind(self):
        selector = [{
            'kind': 'ConfigMap'
        }]
        is_configmap_match, _ = c.resource_match_selectors(self.configmap_resource, selector)
        is_deployment_match, _ = c.resource_match_selectors(self.deployment_resource, selector)

        self.assertTrue(is_configmap_match)
        self.assertFalse(is_deployment_match)

    def test_resource_match_kind_and_name(self):
        selector = [{
            'name': 'example1',
            'kind': 'ConfigMap',
        }]
        configmap_resource1 = copy.deepcopy(self.configmap_resource)
        configmap_resource1['metadata']['name'] = 'example1'
        configmap_resource2 = copy.deepcopy(self.configmap_resource)
        configmap_resource2['metadata']['name'] = 'example2'
        is_configmap1_match, _ = c.resource_match_selectors(configmap_resource1, selector)
        is_configmap2_match, _ = c.resource_match_selectors(configmap_resource2, selector)

        self.assertTrue(is_configmap1_match)
        self.assertFalse(is_configmap2_match)

    def test_resource_match_kind_multi(self):
        selector = [{
            'kind': 'ConfigMap',
        },
        {
            'kind': 'Deployment',
        }]
        is_configmap_match, _ = c.resource_match_selectors(self.configmap_resource, selector)
        is_deployment_match, _ = c.resource_match_selectors(self.deployment_resource, selector)

        self.assertTrue(is_configmap_match)
        self.assertTrue(is_deployment_match)

    def test_get_default_replacement_func(self):
        replacement_func = c.get_default_replacement_func({'foo': 'bar'})
        replacement_result = self.placeholder_prog.sub(replacement_func, 'foo')

        self.assertEqual(replacement_result, 'bar')

    def test_perform_placeholder_replacements_nosecret_dict(self):
        replacement_func = lambda x: 'bar'
        result = c.perform_placeholder_replacements({'foobar': 'foobar', 'baz': 'baz'}, self.placeholder_prog, replacement_func, False)

        self.assertEqual(result, {'foobar': 'barbar', 'baz': 'baz'})

    def test_perform_placeholder_replacements_nosecret_list(self):
        replacement_func = lambda x: 'bar'
        result = c.perform_placeholder_replacements(['foobar', 'baz'], self.placeholder_prog, replacement_func, False)

        self.assertEqual(result, ['barbar', 'baz'])

    def test_perform_placeholder_replacements_nosecret_str(self):
        replacement_func = lambda x: 'bar'
        result = c.perform_placeholder_replacements('foobar', self.placeholder_prog, replacement_func, False)

        self.assertEqual(result, 'barbar')

    def test_perform_placeholder_replacements_nosecret_int(self):
        replacement_func = lambda x: 'bar'
        result = c.perform_placeholder_replacements(42, self.placeholder_prog, replacement_func, False)

        self.assertEqual(result, 42)

    def test_perform_placeholder_replacements_secret_str(self):
        replacement_func = lambda x: 'bar'
        result = c.perform_placeholder_replacements(base64.b64encode(b'foobar').decode('utf8'), self.placeholder_prog, replacement_func, True)

        self.assertEqual(result, base64.b64encode(b'barbar').decode())