from rest_framework.metadata import SimpleMetadata

_filter_fields_cache = {}
_ordering_fields_cache = {}


class RodanMetadata(SimpleMetadata):
    """
    Customize `OPTIONS` response to include filterable and orderable fields.
    """

    def determine_metadata(self, request, view):
        metadata = super(RodanMetadata, self).determine_metadata(request, view)
        metadata["filter_fields"] = self.get_filter_fields(view)
        metadata["ordering_fields"] = self.get_ordering_fields(view)
        return metadata

    def get_filter_fields(self, view):
        if view in _filter_fields_cache:
            return _filter_fields_cache[view]
        else:
            # [TODO] not clever enough...
            # repeating codes: https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/filters.py  # noqa
            if hasattr(view, "filter_class"):
                fc = view.filter_class()
                fields = {}
                for k in fc.filters.keys():
                    things = k.rsplit("__", 1)
                    field = things[0]
                    if field not in fields:
                        fields[field] = []
                    if len(things) == 1:
                        fields[field].append("exact")
                    elif len(things) == 2:
                        lookup_type = things[1]
                        fields[field].append(lookup_type)
            elif hasattr(view, "filter_fields"):
                if isinstance(view.filter_fields, dict):
                    fields = view.filter_fields
                else:
                    fields = {}
                    for field in view.filter_fields:
                        fields[field] = ["exact"]
            else:
                fields = {}

            _filter_fields_cache[view] = fields
            return fields

    def get_ordering_fields(self, view):
        # restrict it to db_index fields
        if view in _ordering_fields_cache:
            return _ordering_fields_cache[view]
        else:
            # model x serializers x ordering_fields
            m = view.get_queryset().model
            fs = m._meta.fields
            fields = set()
            for f in fs:
                if f.primary_key or f.db_index:
                    fields.add(f.name)

            s = view.get_serializer()
            fields = fields.intersection(set(s.fields.keys()))

            if hasattr(view, "ordering_fields") and view.ordering_fields != "__all__":
                fields = fields.intersection(set(view.ordering_fields))

            fields = tuple(fields)
            _ordering_fields_cache[view] = fields
            return fields
