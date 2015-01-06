from gamera import enums

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

    # convert pixel types to Rodan mimetypes
    dict_repr['resource_types'] = []
    for pt in dict_repr['pixel_types']:
        if pt == enums.ONEBIT:
            dict_repr['resource_types'].append('image/onebit+png')
        elif pt == enums.GREYSCALE:
            dict_repr['resource_types'].append('image/greyscale+png')
        elif pt == enums.GREY16:
            dict_repr['resource_types'].append('image/grey16+png')
        elif pt == enums.RGB:
            dict_repr['resource_types'].append('image/rgb+png')
        # Drop COMPLEX and FLOAT pixel types, as they are only Gamera's internal representation and cannot be saved to a PNG file.
    return dict_repr

convert_output_type = convert_input_type


def convert_mimetype_to_pixel(mimetype):
    mapp = {
        'image/onebit+png': enums.ONEBIT,
        'image/greyscale+png': enums.GREYSCALE,
        'image/grey16+png': enums.GREY16,
        'image/rgb+png': enums.RGB
    }
    return mapp[mimetype]


def convert_to_gamera_settings(rodan_job_settings):
    settings = {}
    for s in rodan_job_settings:
        setting_name = "_".join(s['name'].split(" "))
        setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
        settings[setting_name] = setting_value
    return settings
