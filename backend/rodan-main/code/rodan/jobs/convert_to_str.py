# Adapted from http://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str  # noqa
import six
import collections
from builtins import str



def convert_to_str(data):
    if isinstance(data, six.string_types):
        # Python2 idiom `unicode` is now `str` in python3
        return str(data)  # noqa
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_str, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_str, data))
    else:
        return data
