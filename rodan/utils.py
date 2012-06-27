import os

from django.shortcuts import get_object_or_404, render


def remove_prefixes(s):
    """Removes everything before the last .

    So jobs.rotation.Rotate would become Rotate.

    Preserves case.
    """
    return s[s.rfind('.') + 1:]


def rodan_view(*models):
    def outer_function(f):
        def inner_function(request, **kwargs):
            model_instances = []

            for model in models:
                pk = kwargs[model.pk_name]
                del kwargs[model.pk_name]
                model_instance = get_object_or_404(model, pk=pk)
                model_instances.append(model_instance)

            output = f(request, *model_instances, **kwargs)

            try:
                breadcrumbs = []
                model = model_instances[0]
                while hasattr(model, "get_parent"):
                    breadcrumbs.append(model)
                    model = model.get_parent()

                breadcrumbs.append(model)

                title, context = output

                dir_name = f.__module__
                # Get rid of everything before the last .
                dir_name = dir_name[dir_name.rindex('.') + 1:]
                template_name = f.__name__
                template_file = os.path.join(dir_name, template_name + '.html')

                context['title'] = title
                context['model'] = model_instance
                context['template_file'] = template_file
                context['breadcrumbs'] = reversed(breadcrumbs)

                for model_instance in model_instances:
                    model_name = model_instance.__class__.__name__.lower()
                    context[model_name] = model_instance

                return render(request, 'detail.html', context)
            except ValueError:
                return output

        return inner_function
    return outer_function
