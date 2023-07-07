"""
Definitions of command and error codes as stated in the "Mecom" protocol standard.
https://www.meerstetter.ch/category/35-latest-communication-protocols
"""


TEC_PARAMETERS = [
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 105, "name": "Error Number", "format": "INT32"},
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},

    {"id": 1000, "name": "Object Temperature", "format": "FLOAT32"},
    {"id": 1001, "name": "Sink Temperature", "format": "FLOAT32"},
    {"id": 1010, "name": "Target Object Temperature", "format": "FLOAT32"},
    {"id": 1011, "name": "Ramp Object Temperature", "format": "FLOAT32"},
    {"id": 1020, "name": "Actual Output Current", "format": "FLOAT32"},
    {"id": 1021, "name": "Actual Output Voltage", "format": "FLOAT32"},
    {"id": 1200, "name": "Temperature is Stable", "format": "INT32"},

    {"id": 2010, "name": "Status", "format": "INT32"},
    {"id": 2030, "name": "Current Limitation", "format": "FLOAT32"},
    {"id": 2031, "name": "Voltage Limitation", "format": "FLOAT32"},
    {"id": 2032, "name": "Current Error Threshold", "format": "FLOAT32"},
    {"id": 2033, "name": "Voltage Error Threshold", "format": "FLOAT32"},
    {"id": 2051, "name": "Device Address", "format": "INT32"},

    {"id": 3000, "name": "Target Object Temp (Set)", "format": "FLOAT32"},
    {"id": 6100, "name": "GPIO Function", "format": "INT32"},
    {"id": 6101, "name": "GPIO Level Assignment", "format": "INT32"},
    {"id": 6102, "name": "GPIO Hardware Configuration", "format": "INT32"},
    {"id": 6103, "name": "GPIO Channel", "format": "INT32"},

    {"id": 6300, "name": "Source Selection", "format": "INT32"},
    {"id": 6302, "name": "Observe Mode", "format": "INT32"},
    {"id": 6310, "name": "Delay till Restart", "format": "FLOAT32"},
    {"id": 52100, "name": "Enable Function", "format": "INT32"},
    {"id": 52101, "name": "Set Output to Push-Pull", "format": "INT32"},
    {"id": 52102, "name": "Set Output States", "format": "INT32"},
    {"id": 52103, "name": "Read Input States", "format": "INT32"},

    {"id": 50000, "name": "Live Enable", "format": "INT32"},    
    {"id": 50001, "name": "Live Set Current", "format": "FLOAT32"},
    {"id": 50002, "name": "Live Set Voltage", "format": "FLOAT32"},
    
    {"id": 50011, "name": "Object Target Temperature Source Selection", "format": "INT32"},
    {"id": 50012, "name": "Live Target Object Temperature", "format": "FLOAT32"},

    {"id": 52200, "name": "External Object Temperature", "format": "FLOAT32"},
]



LDD_PARAMETERS = [
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},
    {"id": 1016, "name": "Laser Diode Current", "format": "FLOAT32"},
    {"id": 1017, "name": "Laser Diode Voltage", "format": "FLOAT32"},
    {"id": 1015, "name": "Laser Diode Temperature", "format": "FLOAT32"},
    {"id": 3020, "name": "Current Limit Max [A]", "format": "FLOAT32"},
    {"id": 3040, "name": "Device Address", "format": "INT32"},
    {"id": 2001, "name": "Current CW", "format": "FLOAT32"},
    {"id": 2020, "name": "Input Source", "format": "INT32"},
    {"id": 102, "name": "Device Serial Number", "format": "INT32"},
    {"id": 3050 , "name": "Baud Rate", "format": "INT32"},
    {"id": 3051 , "name": "Response Delay ", "format": "INT32"},
    {"id": 3080, "name": "Hardware PIN", "format": "INT32"},
    {"id": 6100, "name": "GPIO Function", "format": "INT32"},
    {"id": 6101, "name": "GPIO Level Assignment", "format": "INT32"},
    {"id": 6102, "name": "GPIO Hardware Configuration", "format": "INT32"},
    {"id": 6103, "name": "GPIO Channel", "format": "INT32"},
    {"id": 6310, "name": "Delay till Restart", "format": "INT32"},
    {"id": 52100, "name": "Enable Function", "format": "INT32"},
    {"id": 52101, "name": "Set Output to Push-Pull", "format": "INT32"},
    {"id": 52102, "name": "Set Output States", "format": "INT32"},
    {"id": 52103, "name": "Read Input States", "format": "INT32"},
]
    
ERRORS = [
    {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
    {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"},
    {"code": 3, "symbol": "ERR_GENERAL_COM", "description": "General communication error"},
    {"code": 4, "symbol": "EER_FORMAT", "description": "Format error"},
    {"code": 5, "symbol": "EER_PAR_NOT_AVAILABLE", "description": "Parameter is not available"},
    {"code": 6, "symbol": "EER_PAR_NOT_WRITABLE", "description": "Parameter is read only"},
    {"code": 7, "symbol": "EER_PAR_OUT_OF_RANGE", "description": "Value is out of range"},
    {"code": 8, "symbol": "EER_PAR_INST_NOT_AVAILABLE", "description": "Parameter is read only"},
    {"code": 20, "symbol": "MEPORT_ERROR_SET_TIMEOUT", "description": "timeout reached, value cannot be set"},
    {"code": 21, "symbol": "MEPORT_ERROR_QUERY_TIMEOUT", "description": "timeout reached query cannot be served"},
]
