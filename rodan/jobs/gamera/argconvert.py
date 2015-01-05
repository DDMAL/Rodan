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

def convert_mimetype_to_pixel(mimetype):
    # Gamera pixel types can be found in gamera.enums module
    mapp = {
        'image/onebit+png': 0,
        'image/greyscale+png': 1,
        'image/grey16+png': 2,
        'image/rgb+png': 3,
        'image/float+png': 4,
        'image/complex+png': 5
    }
    return mapp[mimetype]

def convert_pixel_to_mimetype(pixel_t):
    # Gamera pixel types can be found in gamera.enums module
    mapp = {
        0: 'image/onebit+png',
        1: 'image/greyscale+png',
        2: 'image/grey16+png',
        3: 'image/rgb+png',
        4: 'image/float+png',
        5: 'image/complex+png',
    }
    return mapp[pixel_t]

def convert_to_gamera_settings(rodan_job_settings):
    settings = {}
    for s in rodan_job_settings:
        setting_name = "_".join(s['name'].split(" "))
        setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
        settings[setting_name] = setting_value
    return settings
