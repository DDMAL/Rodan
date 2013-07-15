from django.http import HttpResponse
import json


class JsonResponse(HttpResponse):
    def __init__(self, content={}, mimetype=None, status=None, content_type=None):
        if not content_type:
            content_type = 'application/json'
        super(JsonResponse, self).__init__(json.dumps(content), mimetype=mimetype,
                                           status=status, content_type=content_type)
