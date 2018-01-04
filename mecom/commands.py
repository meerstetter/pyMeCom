"""
Definitions of command and error codes as stated in the "Mecom" protocol standard.
https://www.meerstetter.ch/category/35-latest-communication-protocols
"""


PARAMETERS = [
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 2010, "name": "Status", "format": "INT32"},
    {"id": 1010, "name": "Target Object Temperature", "format": "FLOAT32"},
    {"id": 1000, "name": "Object Temperature", "format": "FLOAT32"},
    {"id": 1200, "name": "Temperature is Stable", "format": "INT32"},
    {"id": 2051, "name": "Device Address", "format": "INT32"}
]


ERRORS = [
    {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
    {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"}
]