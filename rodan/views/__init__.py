from rest_framework.metadata import SimpleMetadata

class RodanMetadata(SimpleMetadata):
    """
    Customize `OPTIONS` response to include filterable and orderable fields.
    """
    def determine_metadata(self, request, view):
        metadata = super(RodanMetadata, self).determine_metadata(request, view)
        metadata['filter_fields'] = self.get_filter_fields(view)
        return metadata

    def get_filter_fields(self, view):
        if hasattr(view, 'filter_fields'):
            return view.filter_fields
        if hasattr(view, 'filter_class'):
            fc = view.filter_class()
            return fc.filters.keys()
        return []
