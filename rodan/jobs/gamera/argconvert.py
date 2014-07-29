def convert_arg_list(arglist):
    if not arglist:
        return []
    ret = []
    for a in arglist:
        arg = a.__dict__
        if 'klass' in arg.keys():
            del arg['klass']

        arg['type'] = str(a).strip('<>').lower()

        # so we don't have to use Gamera's NoneType
        if str(arg['default']) == 'None':
            arg['default'] = None
        ret.append(arg)
    return ret


def convert_to_arg_type(atype, value):
    if atype in ['float', 'real']:
        return float(value)
    elif atype in ['int']:
        return int(value)
    elif atype in ['complex']:
        return complex(value)
    elif atype in ['str']:
        return str(value)
    elif atype in ['choice']:
        return int(value)
    else:
        return value


def convert_input_type(input_type):
    dict_repr = input_type.__dict__
    if 'klass' in dict_repr.keys():
        del dict_repr['klass']
    return dict_repr


def convert_output_type(output_type):
    dict_repr = output_type.__dict__
    if 'klass' in dict_repr.keys():
        del dict_repr['klass']
    return dict_repr
