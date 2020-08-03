import os
import sys
import hashlib
import tempfile
import subprocess
import yaml

from types import SimpleNamespace
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import common as c

def load_config():
    """
    Load plugin configurations.
    :return: a namespace containing the configurations
    :rtype: SimpleNamespace
    """
    # load
    with open(sys.argv[1], 'r') as f:
        plugin_config = yaml.safe_load(f)
        resources = plugin_config.get('resources', [])

    # validation
    validation_fail = False
    if not resources:
        c.eprint('resources is required')
        validation_fail = True
    for resource in resources:
        if 'url' not in resource:
            c.eprint('resources.url is required')
            validation_fail = True
            break
    if validation_fail:
        raise Exception()

    return SimpleNamespace(
        resources=resources
    )

def get_resource(url, expected_sha256=None, patches=None):
    with urlopen(url) as f:
        data = f.read()
    if expected_sha256:
        sha256 = hashlib.sha256()
        sha256.update(data)
        actual_sha256 = sha256.hexdigest()
        if expected_sha256 != actual_sha256:
            c.eprint("sha256 checksum validation failed for", url)
            c.eprint("expected:", expected_sha256)
            c.eprint("actual:  ", actual_sha256)
            raise Exception()
    if patches:
        for patch in patches:
            with tempfile.NamedTemporaryFile() as data_f:
                data_f.write(data)
                data_f.flush()
                try:
                    proc = subprocess.run(
                        ['patch', '--ignore-whitespace', '--output=-', data_f.name, patch],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        encoding='utf8',
                        check=True,
                    )
                    data = proc.stdout.encode()
                except subprocess.CalledProcessError as e:
                    c.eprint(e.stderr)
                    c.eprint('failed to apply patch %s with exit status %s ' % (patch, e.returncode))
                    raise e
    return list(yaml.safe_load_all(data))

def run_plugin():
    """
    Download kubernetes resources from a remote location
    """
    config = load_config()
    all_resources = []

    try:
        for resource in config.resources:
            all_resources = all_resources + get_resource(resource['url'], resource.get('sha256'), resource.get('patches'))
    except yaml.YAMLError as e:
        c.eprint("%s: invalid yaml" % url)
        if hasattr(e, 'problem_mark'):
            c.eprint(e.problem_mark)
            c.eprint(e.problem)
            if e.context is not None:
                c.eprint(e.context)
        raise e
    except HTTPError as e:
        c.eprint("%s: %s %s" % (url, e.code, e.reason))
        raise e
    except URLError as e:
        c.eprint("%s: %s" % (url, e.reason))
        raise e
    yaml.dump_all(all_resources, sys.stdout, default_flow_style=False)
