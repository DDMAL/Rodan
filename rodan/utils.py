def remove_prefixes(s):
    """Removes everything before the last .

    So jobs.rotation.Rotate would become Rotate.

    Preserves case.
    """
    print s
    return s[s.rfind('.')+1:]
