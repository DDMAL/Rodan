# Adapted from http://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str

import collections


def convert_to_unicode(data):
    if isinstance(data, basestring):
        return unicode(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_unicode, data))
    else:
        return data
