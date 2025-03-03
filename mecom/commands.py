"""
Definitions of command and error codes as stated in the MeCom protocol specification.
Documents can be found at https://www.meerstetter.ch/customer-center/downloads/category/35-latest-communication-protocols
"""

#common TEC family parameters
#for a full list of parameters and their description, see the "TEC-Family MeCom Communication Protocol" document
TEC_PARAMETERS = [
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 105, "name": "Error Number", "format": "INT32"},
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},

    {"id": 1000, "name": "Object Temperature", "format": "FLOAT32"},
    {"id": 1001, "name": "Sink Temperature", "format": "FLOAT32"},
    {"id": 3000, "name": "Target Object Temperature", "format": "FLOAT32"},
    {"id": 1011, "name": "Ramp Object Temperature", "format": "FLOAT32"},
    {"id": 1020, "name": "Actual Output Current", "format": "FLOAT32"},
    {"id": 1021, "name": "Actual Output Voltage", "format": "FLOAT32"},
    {"id": 1200, "name": "Temperature is Stable", "format": "INT32"},
    {"id": 3002, "name": "Proximity Width", "format": "FLOAT32"},
    {"id": 3003, "name": "Coarse Temp Ramp", "format": "FLOAT32"},
    {"id": 3010, "name": "Kp", "format": "FLOAT32"},
    {"id": 3011, "name": "Ti", "format": "FLOAT32"},
    {"id": 3012, "name": "Td", "format": "FLOAT32"},

    {"id": 2000, "name": "Output Stage Input Selection", "format": "INT32"},
    {"id": 2010, "name": "Output Enable Status", "format": "INT32"},
    {"id": 2020, "name": "Set Current", "format": "FLOAT32"},
    {"id": 2021, "name": "Set Voltage", "format": "FLOAT32"},
    {"id": 2030, "name": "Current Limitation", "format": "FLOAT32"},
    {"id": 2031, "name": "Voltage Limitation", "format": "FLOAT32"},
    {"id": 2032, "name": "Current Error Threshold", "format": "FLOAT32"},
    {"id": 2033, "name": "Voltage Error Threshold", "format": "FLOAT32"},
    {"id": 2051, "name": "Device Address", "format": "INT32"},

    {"id": 6100, "name": "GPIO Function", "format": "INT32"},
    {"id": 6101, "name": "GPIO Level Assignment", "format": "INT32"},
    {"id": 6102, "name": "GPIO Hardware Configuration", "format": "INT32"},
    {"id": 6103, "name": "GPIO Channel", "format": "INT32"},

    {"id": 6300, "name": "Object Source Selection", "format": "INT32"},
    {"id": 6302, "name": "Observe Mode", "format": "INT32"},
    {"id": 6310, "name": "Delay till Restart", "format": "FLOAT32"},
    {"id": 52100, "name": "Enable Function", "format": "INT32"},
    {"id": 52101, "name": "Set Output to Push-Pull", "format": "INT32"},
    {"id": 52102, "name": "Set Output States", "format": "INT32"},
    {"id": 52103, "name": "Read Input States", "format": "INT32"},

    {"id": 52200, "name": "External Object Temperature", "format": "FLOAT32"},
]


#common LDD-112x family parameters
#for a full list of parameters and their description, see the "LDD-Family MeCom Communication Protocol" document
LDD_112x_PARAMETERS = [
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

#deprecated, use LDD_112x_PARAMETERS instead
LDD_PARAMETERS = LDD_112x_PARAMETERS

#monitor and common LDD-130x parameters
#for a full list of parameters and their description, see the "LDD-130x Communication Protocol" document
LDD_130x_PARAMETERS = [
    #Communication Device Address
    {"id": 2051, "name": "Device Address", "format": "INT32"},
    #Device Identification
    {"id": 100, "name": "Device Type", "format": "INT32"},
    {"id": 101, "name": "Hardware Version", "format": "INT32"},
    {"id": 103, "name": "Firmware Version", "format": "INT32"},
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 105, "name": "Error Number", "format": "INT32"},
    {"id": 106, "name": "Error Instance", "format": "INT32"},
    {"id": 107, "name": "Error Parameter", "format": "INT32"},
    #Flash
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},
    #Output Stage Monitoring
    {"id": 1100, "name": "Actual Output Current", "format": "FLOAT32"},
    {"id": 1101, "name": "Actual Output Voltage", "format": "FLOAT32"},
    #External Temperature Measurement x
    {"id": 1200, "name": "Temperature", "format": "FLOAT32"},
    {"id": 1201, "name": "Resistance", "format": "FLOAT32"},
    {"id": 1202, "name": "Raw ADC Value", "format": "FLOAT32"},
    #Power Stage Phase Monitoring
    {"id": 1300, "name": "Phase Current x", "format": "FLOAT32"},
    {"id": 1301, "name": "Phase Symmetrization Factor x", "format": "FLOAT32"},
    #Internal Parameters
    {"id": 1402, "name": "Nominal Output Current (Ramp)", "format": "FLOAT32"},
    {"id": 1403, "name": "Output Level", "format": "FLOAT32"},
    {"id": 1404, "name": "Calculated Input Current", "format": "FLOAT32"},
    {"id": 1405, "name": "Calculated Output Current", "format": "FLOAT32"},
    #Power Stage Temperature Monitoring
    {"id": 1302, "name": "Temperature Phase x Buck/Boost", "format": "FLOAT32"},
    #Analog Input
    {"id": 1500, "name": "Analog Voltage Input", "format": "FLOAT32"},
    {"id": 1501, "name": "Photodiode Input", "format": "FLOAT32"},
    #Light Power Monitoring
    {"id": 1600, "name": "Emitted Light Power", "format": "FLOAT32"},
    {"id": 1601, "name": "Output Level", "format": "FLOAT32"},
    #Firmware and Hardware Versions
    {"id": 1051, "name": "Firmware Build Number", "format": "INT32"},
    {"id": 1054, "name": "Min Version for Firmware Downgrade", "format": "INT32"},
    #Power Supplies and Temperature
    {"id": 1060, "name": "Driver Input Voltage", "format": "FLOAT32"},
    {"id": 1061, "name": "12V Internal Supply", "format": "FLOAT32"},
    {"id": 1062, "name": "5V Internal Supply", "format": "FLOAT32"},
    {"id": 1063, "name": "3.3V Internal Supply", "format": "FLOAT32"},
    {"id": 1064, "name": "-5V Internal Supply", "format": "FLOAT32"},
    {"id": 1065, "name": "Device Temperature", "format": "FLOAT32"},
]

#monitor and common LDD-1321 parameters
#for a full list of parameters and their description, see the "LDD-1321 Communication Protocol" document
LDD_1321_PARAMETERS = [
    #Communication Device Address
    {"id": 2051, "name": "Device Address", "format": "INT32"},
    #Device Identification
    {"id": 100, "name": "Device Type", "format": "INT32"},
    {"id": 101, "name": "Hardware Version", "format": "INT32"},
    {"id": 103, "name": "Firmware Version", "format": "INT32"},
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 105, "name": "Error Number", "format": "INT32"},
    {"id": 106, "name": "Error Instance", "format": "INT32"},
    {"id": 107, "name": "Error Parameter", "format": "INT32"},
    #Flash
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},
    #LDD Output Monitoring
    {"id": 1100, "name": "Actual Output Current", "format": "FLOAT32"},
    {"id": 1101, "name": "Actual Output Voltage", "format": "FLOAT32"},
    {"id": 1102, "name": "Actual Output Current Raw ADC Value", "format": "FLOAT32"},
    {"id": 1104, "name": "Actual Anode Voltage", "format": "FLOAT32"},
    {"id": 1105, "name": "Actual Cathode Voltage", "format": "FLOAT32"},
    {"id": 1106, "name": "Nominal Anode Voltage", "format": "FLOAT32"},
    #LDD Internal Parameters
    {"id": 1402, "name": "Nominal Output Current (Ramp)", "format": "FLOAT32"},
    {"id": 1404, "name": "Gate Voltage", "format": "FLOAT32"},
    {"id": 1103, "name": "Raw DAC Value", "format": "INT32"},
    #External Temperature Measurement x
    {"id": 1200, "name": "Temperature", "format": "FLOAT32"},
    {"id": 1201, "name": "Resistance", "format": "FLOAT32"},
    {"id": 1202, "name": "Raw ADC Value", "format": "FLOAT32"},
    #Analog Interfaces
    {"id": 1502, "name": "Analog Voltage Input Raw ADC Value", "format": "INT32"},
    {"id": 1500, "name": "Analog Voltage Input", "format": "FLOAT32"},
    {"id": 1501, "name": "Photodiode Input", "format": "FLOAT32"},
    #Light Measurement
    {"id": 1600, "name": "Laser Power", "format": "FLOAT32"},
    #Fan Controller x
    {"id": 1210, "name": "Relative Cooling Power", "format": "FLOAT32"},
    {"id": 1212, "name": "Actual Fan Speed", "format": "FLOAT32"},
    {"id": 1211, "name": "Fan Nominal Speed", "format": "FLOAT32"},
    {"id": 1213, "name": "Actual Fan PWM Level", "format": "FLOAT32"},
    #Firmware and Hardware Versions
    {"id": 1051, "name": "Firmware Build Number", "format": "INT32"},
    {"id": 1054, "name": "Min Version for Firmware Downgrade", "format": "INT32"},
    #Power Supplies and Temperature
    {"id": 1060, "name": "Driver Input Voltage", "format": "FLOAT32"},
    {"id": 1061, "name": "8V Internal Supply", "format": "FLOAT32"},
    {"id": 1062, "name": "5V Internal Supply", "format": "FLOAT32"},
    {"id": 1063, "name": "3.3V Internal Supply", "format": "FLOAT32"},
    {"id": 1064, "name": "-3.3V Internal Supply", "format": "FLOAT32"},
    {"id": 1065, "name": "Device Temperature", "format": "FLOAT32"},
    {"id": 1066, "name": "Powerstage Temperature", "format": "FLOAT32"},
]

#MeCom server error codes as specified in the "MeCom Protocol Specification" document
ERRORS = [
    {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
    {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"},
    {"code": 3, "symbol": "ERR_GENERAL_COM", "description": "General communication error"},
    {"code": 4, "symbol": "EER_FORMAT", "description": "Format error"},
    {"code": 5, "symbol": "EER_PAR_NOT_AVAILABLE", "description": "Parameter is not available"},
    {"code": 6, "symbol": "EER_PAR_NOT_WRITABLE", "description": "Parameter is read only"},
    {"code": 7, "symbol": "EER_PAR_OUT_OF_RANGE", "description": "Value is out of range"},
    {"code": 8, "symbol": "EER_PAR_INST_NOT_AVAILABLE", "description": "Instance is not available"},
    {"code": 9, "symbol": "ERR_PAR_GENERAL_FAILURE", "description": "Parameter general error"},
]
