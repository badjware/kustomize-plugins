import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import common as c

def run_plugin():
    """
    execv() the configured path.
    """
    try:
        with open(sys.argv[1], 'r') as f:
            plugin_config = yaml.safe_load(f)
            path = plugin_config.get('path')
        if not path:
            c.eprint('path is required')
            raise Exception()
        os.execv(path, sys.argv)
    except Exception as e:
        if path:
            c.eprint('%s: %s' % (path, e))
        else:
            c.eprint(e)
        raise e
