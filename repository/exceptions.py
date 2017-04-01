from rest_framework.exceptions import APIException


class FileLimitExceedException(Exception):
    pass


class FileLimitExceedApiException(APIException, FileLimitExceedException):
    pass
