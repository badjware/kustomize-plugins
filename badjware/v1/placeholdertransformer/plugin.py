import os
import sys
import yaml
import re

from types import SimpleNamespace
from base64 import b64encode, b64decode

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import common as c

PLACEHOLDER_PROG = re.compile(r'\$\{\s*(\w+)\s*\}')

def load_config():
    """
    Load plugin configurations.
    :return: a namespace containing the configurations
    :rtype: SimpleNamespace
    """
    # load
    with open(sys.argv[1], 'r') as f:
        plugin_config = yaml.safe_load(f)
        placeholders = plugin_config.get('placeholders')
        placeholders_file = plugin_config.get('placeholdersFile')
        resource_selectors = plugin_config.get('resourceSelectors', [])

    # validation
    validation_fail = False
    if not placeholders_file:
        c.eprint('One of placeholders or placeholdersFile is required')
        validation_fail = True
    if validation_fail:
        raise Exception()

    return SimpleNamespace(
        placeholders=placeholders,
        placeholders_file=placeholders_file,
        resource_selectors=resource_selectors
    )

def parse_dotenv(filename):
    """
    Load and parse a file in the dotenv format. Exit on error.
    :param str filename: the path the the file to load
    :return: a dict of key/value loaded from the file
    :rtype: dict
    """
    values = {}
    linenum = 0
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                linenum += 1
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    values[key] = value
    except ValueError:
        c.eprint('%s: line %s: invalid format' % (filename, linenum))
        raise Exception()
    return values

def run_plugin():
    """
    Perform arbitrary key/value replacements in kubernetes resources.
    """
    # load config
    config = load_config()
    all_resources = []

    # load placeholders
    if config.placeholders:
        placeholders = config.placeholders
    else:
        placeholders = {}
    if config.placeholders_file:
        placeholders.update(parse_dotenv(config.placeholders_file))

    for resource in yaml.safe_load_all(sys.stdin.read()):
        is_resource_match, resource_metadata = c.resource_match_selectors(resource, config.resource_selectors)
        if is_resource_match:
            for key, value in resource.items():
                # secret is a special case
                if(resource_metadata['kind'] == 'Secret'):
                    if 'data' in resource:
                        resource['data'] = c.perform_placeholder_replacements(resource['data'], PLACEHOLDER_PROG, c.get_default_replacement_func(placeholders), True)
                    if 'tls' in resource:
                        resource['tls'] = c.perform_placeholder_replacements(resource['tls'], PLACEHOLDER_PROG, c.get_default_replacement_func(placeholders), True)
                # exclude these top-level fields from placeholder replacement
                elif key not in ('apiVersion', 'kind', 'metadata'):
                    resource[key] = c.perform_placeholder_replacements(value, PLACEHOLDER_PROG, c.get_default_replacement_func(placeholders), False)

        all_resources.append(resource)
    yaml.dump_all(all_resources, sys.stdout, default_flow_style=False)
