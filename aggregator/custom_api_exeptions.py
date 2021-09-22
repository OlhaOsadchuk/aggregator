from rest_framework.exceptions import APIException


class Http204(APIException):
    status_code = 204


class Http400(APIException):
    status_code = 400


class Http403(APIException):
    status_code = 403


class Http429(APIException):
    status_code = 429
