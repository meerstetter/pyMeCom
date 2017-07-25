class ResponseException(Exception):
    pass


class WrongResponseSequence(ResponseException):
    pass


class WrongChecksum(Exception):
    pass