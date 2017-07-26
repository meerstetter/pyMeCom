class ResponseException(Exception):
    pass


class ResponseTimeout(ResponseException):
    pass


class WrongResponseSequence(ResponseException):
    pass


class WrongChecksum(Exception):
    pass

