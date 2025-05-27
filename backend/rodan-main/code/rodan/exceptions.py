from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    def __init__(self, detail, status):
        self.detail = detail
        self.status_code = status
