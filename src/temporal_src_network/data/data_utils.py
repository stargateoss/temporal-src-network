import collections
import copy
import os
import re
import unicodedata

def log_value(value):
    """
    Get log value surrounded with a single backtick '`' if its `str` object,
    otherwise return value as is as a `str`.
    """

    if value is not None and isinstance(value, str):
        return "`" + str(value) + "`"
    else:
        return str(value)

def log_private_value(value):
    """
    Get private log value as `***` if not `None`, otherwise literal `None`.
    """

    if value is not None :
        return "***"
    else:
        return str(value)



def get_list_string(list_value):
    "Get a string representation of a list."

    # If directly printed, python used repr() on each element, which
    # escapes backslashes like "\" with "\\", which would not be real
    # value of list items.

    if not list_value or not isinstance(list_value, list) or not list_value: return []
    return "['%s']" % "', '".join(map(str, list_value)) # pylint: disable=consider-using-f-string



def remove_escape_characters(string):
    "Remove 7-bit ansi escape sequence characters from string."

    # https://stackoverflow.com/a/38662876
    if string is None: return string
    return re.sub(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]', '', string)


def remove_control_characters(string):
    "Remove control sequence characters from string except '\n' and '\t'."

    # https://stackoverflow.com/a/19016117
    if string is None: return string
    return "".join(ch for ch in string if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"])

def sanitize_illegal_chars_from_dict(obj, is_value=True):
    "Sanitize illegal characters in dictionary keys and values."

    if isinstance(obj, dict):
        new_obj = collections.OrderedDict()
        for key, value in obj.items():
            if isinstance(value, dict):
                new_obj[sanitize_illegal_chars_from_dict(key, False)] = \
                    collections.OrderedDict(sanitize_illegal_chars_from_dict(value, True))
            else:
                new_obj[sanitize_illegal_chars_from_dict(key, False)] = \
                    sanitize_illegal_chars_from_dict(value, True)
        obj = new_obj
    elif isinstance(obj, list):
        obj = [sanitize_illegal_chars_from_dict(value, True) for value in obj]
    elif isinstance(obj, str):
        # If not is_value:
        # print("'" + repr(obj) + "'")
        obj = remove_escape_characters(obj)
        obj = remove_control_characters(obj)
        # print("'" + repr(obj) + "'")
    else:
        pass

    return obj



def delete_keys_from_dict(obj, keys_to_delete, replacement_pair=None):
    """
    Return a new dictionary with specified keys deleted.
    If `replacement_pair` `list` is passed, then instead of deleting,
    the value will be replaced with `replacement_pair[0]` if `null`,
    otherwise with `replacement_pair[1]`
    """

    if isinstance(obj, dict):
        new_obj = collections.OrderedDict()
        keys_to_delete_set = set(keys_to_delete)
        for key, value in obj.items():
            if key not in keys_to_delete_set:
                if isinstance(value, (dict, list)):
                    new_obj[key] = collections.OrderedDict(delete_keys_from_dict(value, keys_to_delete, replacement_pair))
                else:
                    new_obj[key] = copy.deepcopy(value)
            else:
                if replacement_pair and isinstance(replacement_pair, list) and len(replacement_pair) == 2:
                    if obj[key] is None:
                        new_obj[key] = replacement_pair[0]
                    else:
                        new_obj[key] = replacement_pair[1]
        obj = new_obj
    elif isinstance(obj, list):
        obj = [delete_keys_from_dict(value, keys_to_delete, replacement_pair) for value in obj]
    else:
        pass

    return obj



def get_str_from_env_or_dict(dict_obj, env_key, dict_key):
    "Get key value from env defined by the variable in env_key of dict or get value from dict_key."

    if dict_obj and env_key in dict_obj and dict_obj[env_key] and isinstance(dict_obj[env_key], str):
        return (True, os.environ.get(re.sub(r"^[$]", "", dict_obj[env_key])))
    elif dict_obj and dict_key in dict_obj and dict_obj[dict_key] and isinstance(dict_obj[dict_key], str):
        return (True, dict_obj.get(dict_key))
    else:
        return (False, None)



def get_value_from_dict(dict_objs, key):
    """
    If dict_objs is a dict, then get key value from it if key exists,
    otherwise if dict_objs is a list of dict, then get key value from
    first dict in which the key exists.
    @returns (found, value) The `found` will be `true` is value is found,
                            otherwise `false`. The `value` will be the
                            value found, otherwise `None`.
    """

    if not dict_objs:
        return (False, None)

    if isinstance(dict_objs, dict):
        if key in dict_objs:
            return (True, dict_objs[key])
    elif isinstance(dict_objs, list):
        for dict_obj in dict_objs:
            if dict_obj and isinstance(dict_obj, dict) and key in dict_obj:
                return (True, dict_obj[key])

    return (False, None)


def get_bool_from_dict(dict_objs, key, default):
    "Get bool key value from dict_objs if it exists, otherwise default."

    (found, value) = get_value_from_dict(dict_objs, key)
    if not found:
        return default

    if value is not None and isinstance(value, bool):
        return value
    else:
        return default

def get_str_from_dict(dict_objs, key, default):
    "Get str key value from dict_objs if it exists, otherwise default."

    (found, value) = get_value_from_dict(dict_objs, key)
    if not found:
        return default

    if value is not None and isinstance(value, str):
        return value
    else:
        return default

def get_int_from_dict(dict_objs, key, default):
    "Get int key value from dict_objs if it exists, otherwise default."

    (found, value) = get_value_from_dict(dict_objs, key)
    if not found:
        return default

    if value is not None and isinstance(value, int):
        return value
    else:
        return default

def get_dict_from_dict(dict_objs, key, default):
    "Get dict key value from dict_objs if it exists, otherwise default."

    (found, value) = get_value_from_dict(dict_objs, key)
    if not found:
        return default

    if value is not None and isinstance(value, dict):
        return value
    else:
        return default

def get_ordered_dict_from_dict(dict_objs, key, default):
    "Get OrderedDict key value from dict_objs if it exists, otherwise default."

    (found, value) = get_value_from_dict(dict_objs, key)
    if not found:
        return default

    if value is not None and isinstance(value, dict):
        return collections.OrderedDict(value)
    else:
        return default

def get_comma_separated_list_from_dict(dict_objs, key, default, unique):
    """
    Get str key value as a list from dict_objs if it exists who value is
    a comma separated list, otherwise default as list.
    Empty values will be removed.
    """

    value_list = None
    value = get_str_from_dict(dict_objs, key, default)
    if value:
        value = re.sub(r"[,]+", ",", value)
        value = re.sub(r"^,|,$", "", value)
        if value:
            value_list = value.split(',')

    if value_list:
        if unique:
            return list(set(value_list))
        else:
            return value_list
    else:
        return []
