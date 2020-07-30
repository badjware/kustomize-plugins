import os
import sys
import yaml
import re

from types import SimpleNamespace
from base64 import b64encode, b64decode
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import common as c

PLACEHOLDER_PROG = re.compile(r'\$\{\s*ssm:([a-zA-Z0-9_.\-/]+)\s*\}')

ssm = boto3.client('ssm')

def load_config():
    """
    Load plugin configurations.
    :return: a namespace containing the configurations
    :rtype: SimpleNamespace
    """
    # load
    with open(sys.argv[1], 'r') as f:
        plugin_config = yaml.safe_load(f)
        resource_selectors = plugin_config.get('resourceSelectors', [])

    return SimpleNamespace(
        resource_selectors=resource_selectors
    )

@lru_cache(maxsize=None)
def get_ssm_parameter(parameter_name):
    """
    Fetch a parameter in SSM
    :param str param_name: the name of the parameter to fetch
    :return: the value of the parameter, or None if the parameter doesn't exists
    :rtype: str
    """
    try:
        return ssm.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )['Parameter']['Value']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return None
        else:
            c.print(e)
            raise e

def ssm_replacement_func(match):
    """
    Perform the replacement. If the matched value is absent from the parameters, no replacement is performed
    :param Match match: the match object with a single capture group
    :return: the replacement
    :rtype: str
    """
    placeholder = get_ssm_parameter(match.group(1))
    if placeholder is not None:
        return placeholder
    else:
        return match.group(0)

def run_plugin():
    """
    Perform arbitrary key/value replacements in kubernetes resources.
    """
    config = load_config()
    all_resources = []

    for resource in yaml.safe_load_all(sys.stdin.read()):
        is_resource_match, resource_metadata = c.resource_match_selectors(resource, config.resource_selectors)
        if is_resource_match:
            for key, value in resource.items():
                # secret is a special case
                if(resource_metadata['kind'] == 'Secret'):
                    if 'data' in resource:
                        resource['data'] = c.perform_placeholder_replacements(resource['data'], PLACEHOLDER_PROG, ssm_replacement_func, True)
                    if 'tls' in resource:
                        resource['tls'] = c.perform_placeholder_replacements(resource['tls'], PLACEHOLDER_PROG, ssm_replacement_func, True)
                # exclude these top-level fields from placeholder replacement
                elif key not in ('apiVersion', 'kind', 'metadata'):
                    resource[key] = c.perform_placeholder_replacements(value, PLACEHOLDER_PROG, ssm_replacement_func, False)

        all_resources.append(resource)
    yaml.dump_all(all_resources, sys.stdout, default_flow_style=False)
