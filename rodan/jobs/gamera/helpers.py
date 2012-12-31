# some helper functions for working with Gamera plugins
from rodan.models.job import Job


def convert_arg_list(arglist):
    if not arglist:
        return None
    ret = []
    for a in arglist:
        arg = a.__dict__
        if 'klass' in arg.keys():
            del arg['klass']

        # so we don't have to use Gamera's NoneType
        if str(arg['default']) == 'None':
            arg['default'] = None
        ret.append(arg)
    return ret


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


def create_job_from_plugins(plugin_classes, existing_plugins, plugin_category):
    for fn in plugin_classes:
        if not fn.return_type:
            # For now, we'll only deal with plugins that
            # actually return something
            continue
        if str(fn) in existing_plugins:
            # we've already loaded this. Let's skip it.
            continue
        print "Loading ", str(fn)
        input_types = convert_input_type(fn.self_type)
        output_types = convert_output_type(fn.return_type)
        arguments = convert_arg_list(fn.args.list)
        j = Job(
                name=str(fn),
                author=fn.author,
                input_types=input_types,
                output_types=output_types,
                arguments=arguments,
                is_enabled=True,
                is_automatic=False,
                is_required=True,
                category=plugin_category
            )
        j.save()
