from rest_framework import permissions
from rest_framework.filters import BaseFilterBackend
from guardian.shortcuts import get_objects_for_user


class ObjectPermissionsFilter(BaseFilterBackend):
    """
    Scope list querysets to objects the user has `view_<model>` permission on.

    Faithful replacement for DRF's `DjangoObjectPermissionsFilter`, which was
    removed from `rest_framework.filters` in DRF 3.9. Relies on django-guardian
    object permissions, which Rodan assigns per-object to each project's
    admin/worker groups (see `assign_perms_project`/`assign_perms_others` in
    `rodan/models/__init__.py`). `get_objects_for_user` keeps `with_superuser=True`
    (superusers still see everything) and `use_groups=True` (project-group
    membership grants scope).
    """

    perm_format = "%(app_label)s.view_%(model_name)s"

    def filter_queryset(self, request, queryset, view):
        model = queryset.model
        permission = self.perm_format % {
            "app_label": model._meta.app_label,
            "model_name": model._meta.model_name,
        }
        return get_objects_for_user(request.user, permission, queryset)


class CustomObjectPermissions(permissions.DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
