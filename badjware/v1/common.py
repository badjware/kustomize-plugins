import sys
from base64 import b64encode, b64decode

def eprint(*args, **kwargs):
    """
    Print to stderr.
    """
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def resource_match_selectors(resource, resource_selectors):
    """
    Check if a resource match a resourceSelector
    :param dict resource: a dict representation of the resource to match
    :param list resource_selectors: a list of dict representing the selectors
    :returns: a tuple with the first value being a bool set to true if it's a match, and the second value being a dict with the metadata of the resource 
    :rtype: tuple of (bool, dict)
    """

    # extract all the fields for selector matching
    resource_component = resource.get('apiVersion').split('/')
    if len(resource_component) == 1:
        group = ''
        version = resource_component[0]
    else:
        group = resource_component[0]
        version = resource_component[1]
    
    resource_metadata = {
        'group': group,
        'version': version,
        'kind': resource.get('kind'),
        'name': resource.get('metadata').get('name'),
        'namespace': resource.get('metadata').get('namespace')
    }

    do_placeholder_replacements = False
    if resource_selectors:
        # check if the resource match a selector
        for selector in resource_selectors:
            match = True
            for selector_name, selector_value in selector.items():
                if resource_metadata.get(selector_name) != selector_value:
                    # no match, we break out
                    match = False
                    break
            if match:
                # we have a match, we can perform placeholder replacement
                do_placeholder_replacements = True
                break
    else:
        # if there is no selector, we perform replacement in all the resources
        do_placeholder_replacements = True
    
    return do_placeholder_replacements, resource_metadata

def get_default_replacement_func(placeholders):
    """
    Get a default function for use by perform_placeholder_replacements()
    :param dict placeholders: a dict of placeholders for the replacements
    :returns: a function that seach the placeholder dict for a replacement
    :rtype: function
    """
    return lambda m: placeholders.get(m.group(1), m.group(0))

def perform_placeholder_replacements(data, placeholder_prog, replacement_func, is_secret):
    """
    Recursively perform placeholder replacement to arbitrary data.
    :param any data: the data to operate on. can be of any type, but replacement will only be performed on list, dict or str
    :param Pattern placeholder_prog: a compiled regex pattern with a capture group designating what need to be replaced
    :param function replacement_func: a function taking the match object as a parameter and return the replacement
    :param bool is_secret: true if the the data is from a secret that need to be base64 decoded
    :rtype: same type then data
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = perform_placeholder_replacements(value, placeholder_prog, replacement_func, is_secret)
        return result
    elif isinstance(data, list):
        result = []
        for value in data:
            result.append(perform_placeholder_replacements(value, placeholder_prog, replacement_func, is_secret))
        return result
    elif isinstance(data, str):
        if is_secret:
            return b64encode(placeholder_prog.sub(replacement_func, b64decode(data).decode()).encode()).decode()
        else:
            return placeholder_prog.sub(replacement_func, data)
    else:
        return data
