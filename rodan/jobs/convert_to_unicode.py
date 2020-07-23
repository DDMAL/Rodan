# Adapted from http://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str  # noqa
import six
import collections


def convert_to_unicode(data):
    if isinstance(data, six.string_types):
        # Python2 idiom `unicode` is now `str` in python3
        return unicode(data)  # noqa
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_unicode, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_unicode, data))
    else:
        return data
