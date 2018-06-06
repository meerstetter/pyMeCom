"""
This file contains some custom expceptions.
"""


class ResponseException(Exception):
    pass


class ResponseTimeout(ResponseException):
    pass


class WrongResponseSequence(ResponseException):
    pass


class WrongChecksum(Exception):
    pass


class UnknownParameter(Exception):
    pass
    
class UnknownMeComType(Exception):
    pass
