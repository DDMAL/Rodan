import re


def check_uuid(string):
    """ Checks a string to see if it's a valid UUID. Returns True if it is, False otherwise.
        Regex from: http://stackoverflow.com/questions/136505/searching-for-uuids-in-text-with-regex
        Modified to not check for dashes, since we don't really use them in Rodan.
    """
    re_uuid = re.compile("[0-F]{8}[0-F]{4}[0-F]{4}[0-F]{4}[0-F]{12}", re.I)
    if re.match(re_uuid, string):
        return True
    return False
