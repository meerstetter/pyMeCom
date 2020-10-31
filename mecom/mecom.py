""""
The magic happens in this file.
"""

from struct import pack, unpack
from functools import partialmethod
import time
from threading import Lock

# more special pip packages
from serial import Serial
from PyCRC.CRCCCITT import CRCCCITT

# from this package
from .exceptions import ResponseException, WrongResponseSequence, WrongChecksum, ResponseTimeout, UnknownParameter, UnknownMeComType
from .commands import TEC_PARAMETERS, LDD_PARAMETERS, ERRORS


class Parameter(object):
    """"
    Every parameter dict from commands.py is parsed into a Parameter instance.
    """

    def __init__(self, parameter_dict):
        """
        Takes a dict e.g. {"id": 104, "name": "Device Status", "format": "INT32"} and creates an object which can be
        passed to a Query().
        :param parameter_dict: dict
        """
        self.id = parameter_dict["id"]
        self.name = parameter_dict["name"]
        self.format = parameter_dict["format"]


class Error(object):
    """"
    Every error dict from commands.py is parsed into a Error instance.
    """

    def __init__(self, error_dict):
        """
        Takes a dict e.g. {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"} which
        defines a error specified by the protocol.
        :param error_dict: dict
        """
        self.code = error_dict["code"]
        self.symbol = error_dict["symbol"]
        self.description = error_dict["description"]

    def as_list(self):
        """
        Returns a list representation of this object.
        :return: list
        """
        return [self.code, self.description, self.symbol]


class ParameterList(object):
    """
    Contains a list of Parameter() for either TEC (metype = 'TEC') 
    or LDD (metype = 'TEC') controller.
    Provides searching via id or name.
    :param error_dict: dict
    """

    def __init__(self,metype='TEC'):
        """
        Reads the parameter dicts from commands.py.
        """
        self._PARAMETERS = []
        if metype == 'TEC':
            for parameter in TEC_PARAMETERS:
                self._PARAMETERS.append(Parameter(parameter))
        elif metype =='LDD':
            for parameter in LDD_PARAMETERS:
                self._PARAMETERS.append(Parameter(parameter))
        else:
            raise UnknownMeComType

    def get_by_id(self, id):
        """
        Returns a Parameter() identified by it's id.
        :param id: int
        :return: Parameter()
        """
        for parameter in self._PARAMETERS:
            if parameter.id == id:
                return parameter
        raise UnknownParameter

    def get_by_name(self, name):
        """
        Returns a Parameter() identified by it's name.
        :param name: str
        :return: Parameter()
        """
        for parameter in self._PARAMETERS:
            if parameter.name == name:
                return parameter
        raise UnknownParameter


class MeFrame(object):
    """
    Basis structure of a MeCom frame as defined in the specs.
    """
    _TYPES = {"UINT8": "!H", "UINT16": "!L", "INT32": "!i", "FLOAT32": "!f"}
    _SOURCE = ""
    _EOL = "\r"  # carriage return

    def __init__(self):
        self.ADDRESS = 0
        self.SEQUENCE = 0
        self.PAYLOAD = []
        self.CRC = None

    def crc(self, in_crc=None):
        """
        Calculates the checksum of a given frame, if a checksum is given as parameter, the two are compared.
        :param in_crc:
        :return: int
        """
        if self.CRC is None:
            self.CRC = CRCCCITT().calculate(input_data=self.compose(part=True))

        # crc check
        # print(self.CRC)
        # print(in_crc)
        if in_crc is not None and in_crc != self.CRC:
            raise WrongChecksum

    def set_sequence(self, sequence):
        self.SEQUENCE = sequence

    def compose(self, part=False):
        """
        Returns the frame as bytes, the return-value can be directly send via serial.
        :param part: bool
        :return: bytes
        """
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload can be str or float or int
        for p in self.PAYLOAD:
            if type(p) is str:
                frame += p
            elif type(p) is int:
                frame += "{:08X}".format(p)
            elif type(p) is float:
                # frame += hex(unpack('<I', pack('<f', p))[0])[2:].upper()  # please do not ask
                # if p = 0 CRC fails, e.g. !01000400000000 composes to b'!0100040' / missing zero padding
                frame += '{:08X}'.format(unpack('<I', pack('<f', p))[0])   #still do not aks
        # if we only want a partial frame, return here
        if part:
            return frame.encode()
        # add checksum
        if self.CRC is None:
            self.crc()
        frame += "{:04X}".format(self.CRC)
        # add end of line (carriage return)
        frame += self._EOL
        return frame.encode()

    def _decompose_header(self, frame_bytes):
        """
        Takes bytes as input and decomposes into the instance variables.
        :param frame_bytes: bytes
        :return:
        """
        frame = frame_bytes.decode()

        self._SOURCE = frame[0]
        self.ADDRESS = int(frame[1:3], 16)
        self.SEQUENCE = int(frame[3:7], 16)


class Query(MeFrame):
    """
    Basic structure of a query to get or set a parameter. Has the attribute RESPONSE which contains the answer received
    by the device. The response is set via set_response
    """
    _SOURCE = "#"
    _PAYLOAD_START = None

    def __init__(self, parameter=None, address=0, parameter_instance=1):
        """
        To be initialized with a target device address (default=broadcast), the channel, teh sequence number and a
        Parameter() instance of the corresponding parameter.
        :param parameter: Parameter
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        super(Query, self).__init__()

        if hasattr(self, "_PAYLOAD_START"):
            self.PAYLOAD.append(self._PAYLOAD_START)

        self.RESPONSE = None
        self._RESPONSE_FORMAT = None

        self.ADDRESS = address
        if parameter is not None:
            # UNIT16 4 hex digits
            self.PAYLOAD.append("{:04X}".format(parameter.id))
        # UNIT8 2 hex digits
        self.PAYLOAD.append("{:02X}".format(parameter_instance))

    def set_response(self, response_frame):
        """
        Takes the bytes received from the device as input and creates the corresponding response instance.
        :param response_frame: bytes
        :return:
        """
        # check the type of the response
        # is it an ACK packet?
        if len(response_frame) == 10:
            self.RESPONSE = ACK()
            self.RESPONSE.decompose(response_frame)
        # is it an info string packet/response_frame does not contain source (!)
        elif len(response_frame) == 30:
            self.RESPONSE = IFResponse()
            self.RESPONSE.decompose(response_frame)
        # is it an error packet?
        elif b'+' in response_frame:
            self.RESPONSE = DeviceError()
            self.RESPONSE.decompose(response_frame)
        # nope it's a response to a parameter query
        else:
            self.RESPONSE = VRResponse(self._RESPONSE_FORMAT)
            # if the checksum is wrong, this statement raises
            self.RESPONSE.decompose(response_frame)

        # did we get the right response to our query?
        if self.SEQUENCE != self.RESPONSE.SEQUENCE:
            raise WrongResponseSequence


class VR(Query):
    """
    Implementing query to get a parameter from the device (?VR).
    """
    _PAYLOAD_START = "?VR"

    def __init__(self, parameter, address=0, parameter_instance=1):
        """
        Create a query to get a parameter value.
        :param parameter: Parameter
        :param address: int
        :param parameter_instance: int
        """
        # init header (equal for get and set queries
        super(VR, self).__init__(parameter=parameter,
                         address=address,
                         parameter_instance=parameter_instance)
        # initialize response
        self._RESPONSE_FORMAT = parameter.format


class VS(Query):
    """
    Implementing query to set a parameter from the device (VS).
    """
    _PAYLOAD_START = "VS"

    def __init__(self, value, parameter, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param value: int or float
        :param parameter: Parameter
        :param address: int
        :param parameter_instance: int
        """
        # init header (equal for get and set queries)
        super(VS, self).__init__(parameter=parameter,
                         address=address,
                         parameter_instance=parameter_instance)


        # cast the value parameter to the correct type
        conversions = {'FLOAT32': float, 'INT32': int}
        assert parameter.format in conversions.keys()
        
        value=conversions[parameter.format](value)

        # the set value
        self.PAYLOAD.append(value)

        # no need to initialize response format, we want ACK
        
        


class RS(Query):
    """
    Implementing system reset.
    """
    _PAYLOAD_START = 'RS'

    def __init__(self, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param address: int
        :param parameter_instance: int
        """
        
        # init header (equal for get and set queries)
        super(RS, self).__init__(parameter=None,
                         address=address,
                         parameter_instance=parameter_instance)

        # no need to initialize response format, we want ACK
        
class IF(Query):
    """
    Implementing device info query.
    """
    _PAYLOAD_START = '?IF'

    def __init__(self, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param address: int
        :param parameter_instance: int
        """
        
        # init header (equal for get and set queries)
        super(IF, self).__init__(parameter=None,
                         address=address,
                         parameter_instance=parameter_instance)

        # no need to initialize response format, we want ACK


class VRResponse(MeFrame):
    """
    Frame for the device response to a VR() query.
    """
    _SOURCE = "!"
    _RESPONSE_FORMAT = None

    def __init__(self, response_format):
        """
        The format of the response is given via VR.set_response()
        :param response_format: str
        """
        super(VRResponse, self).__init__()
        self._RESPONSE_FORMAT = self._TYPES[response_format]

    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """
        assert self._RESPONSE_FORMAT is not None
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = [unpack(self._RESPONSE_FORMAT, bytes.fromhex(frame[7:15]))[0]]  # convert hex to float or int
        self.crc(int(frame[-4:], 16))  # sets crc or raises


class ACK(MeFrame):
    """
    ACK command sent by the device.
    """
    _SOURCE = "!"
    
    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)
        
        frame = frame_bytes.decode()
        self.CRC = int(frame[-4:], 16)
        

class IFResponse(MeFrame):
    """
    ACK command sent by the device.
    """
    _SOURCE = "!"

    def crc(self, in_crc=None):
        """
        ACK has the same checksum as the VS command.
        :param in_crc: int
        :return:
        """
        pass

    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = frame[7:-4]
        self.CRC = int(frame[-4:], 16)


class DeviceError(MeFrame):
    """
    Queries failing return a device error, implemented as repsonse by this class.
    """
    _SOURCE = "!"

    def __init__(self):
        """
        Read error codes from command.py and parse into a list of Error() instances.
        """
        super(DeviceError, self).__init__()
        self._ERRORS = []
        for error in ERRORS:
            self._ERRORS.append(Error(error))

    def _get_by_code(self, code):
        """
        Returns a Error() identified by it's error code.
        :param code: int
        :return: Error()
        """
        for error in self._ERRORS:
            if error.code == code:
                return error
        # we do not need to raise here since error are well defined

    def compose(self, part=False):
        """
        Device errors have a different but simple structure.
        :param part: bool
        :return:
        """
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload is ['+', #_of_error]
        frame += self.PAYLOAD[0]
        frame += "{:02x}".format(self.PAYLOAD[1])
        # if we only want a partial frame, return here
        if part:
            return frame.encode()
        # add checksum
        if self.CRC is None:
            self.crc()
        frame += "{:04X}".format(self.CRC)
        # add end of line (carriage return)
        frame += self._EOL
        return frame.encode()

    def decompose(self, frame_bytes):
        """
        Again, different but consistent structure.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)
        frame = frame_bytes.decode()
        self.PAYLOAD.append(frame[7])
        self.PAYLOAD.append(int(frame[8:10], 16))
        self.crc(int(frame[-4:], 16))

    def error(self):
        """
        Returns error code, description and symbol as [str,].
        :return: [str, str, str]
        """
        error_code = self.PAYLOAD[1]
        # returns [code, description, symbol]
        return self._get_by_code(error_code).as_list()


class MeCom:
    """
    Main class. Import this one:
    from qao.devices.mecom import MeCom

    For a usage example see __main__
    """
    SEQUENCE_COUNTER = 1

    def __init__(self, serialport="/dev/ttyUSB0", timeout=1, baudrate=57600,metype = 'TEC'):
        """
        Initialize communication with serial port.
        :param serialport: str
        :param timeout: int
        :param metype: str: either 'TEC' or 'LDD'
        """
        # initialize serial connection
        self.ser = Serial(port=serialport, timeout=timeout, write_timeout=timeout, baudrate=baudrate)
        self.ser_lock = Lock()

        # start protocol thread
        # self.protocol = ReaderThread(serial_instance=self.ser, protocol_factory=MePacket)
        # self.receiver = self.protocol.__enter__()

        # initialize parameters
        self.PARAMETERS = ParameterList(metype)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ser.__exit__(exc_type, exc_val, exc_tb)

    def __enter__(self):
        return self

    def stop(self):
        self.ser.flush()
        self.ser.close()

    def _find_parameter(self, parameter_name, parameter_id):
        """
        Return Parameter() with either name or id given.
        :param parameter_name: str
        :param parameter_id: int
        :return: Parameter
        """
        return self.PARAMETERS.get_by_name(parameter_name) if parameter_name is not None\
            else self.PARAMETERS.get_by_id(parameter_id)

    def _inc(self):
        self.SEQUENCE_COUNTER += 1
        # sequence in controller is int16 and overflows 
        self.SEQUENCE_COUNTER = self.SEQUENCE_COUNTER % (2**16)

    @staticmethod
    def _raise(query):
        """
        If DeviceError is received, raise!
        :param query: VR or VS
        :return:
        """
        # did we encounter an error?
        if type(query.RESPONSE) is DeviceError:
            code, description, symbol = query.RESPONSE.error()
            raise ResponseException("device {} raised {}".format(query.RESPONSE.ADDRESS, description))

    def _read(self, size):
        """
        Read n=size bytes from serial, if <n bytes are received (serial.read() return because of timeout), raise a timeout.
        """
        recv = self.ser.read(size=size)
        if len(recv) < size:
            raise ResponseTimeout("timeout while communication via serial")
        else:
            return recv

    def _execute(self, query):
        self.ser_lock.acquire()
        
        try:
            # clear buffers
            self.ser.reset_output_buffer()
            self.ser.reset_input_buffer()
    
            query.set_sequence(self.SEQUENCE_COUNTER)
            # send query
            self.ser.write(query.compose())
            # print(query.compose())
    
            # flush write cache
            self.ser.flush()
    
            # initialize response and carriage return
            cr = "\r".encode()
            response_frame = b''
            response_byte = self._read(size=1)  # read one byte at a time, timeout is set on instance level
    
            # read until stop byte
            while response_byte != cr:
                response_frame += response_byte
                response_byte = self._read(size=1)
        finally:
            # increment sequence counter
            self._inc()
            self.ser_lock.release()

        # strip source byte (! or #, but for a response always !)
        response_frame = response_frame[1:]

        # print(response_frame)
        query.set_response(response_frame)

        # did we encounter an error?
        self._raise(query)

        return query

    def _get(self, parameter_name=None, parameter_id=None, *args, **kwargs):
        """
        Get a query object for a VR command.
        :param parameter_name:
        :param parameter_id:
        :param args:
        :param kwargs:
        :return:
        """
        assert parameter_name is not None or parameter_id is not None

        # search in DataFrame returns a dict
        parameter = self._find_parameter(parameter_name, parameter_id)

        # execute query
        vr = self._execute(VR(parameter=parameter, *args, **kwargs))

        # print(vr.PAYLOAD)
        # print(vr.RESPONSE.PAYLOAD)
        # return the query with response
        return vr

    def _set(self, value, parameter_name=None, parameter_id=None, *args, **kwargs):
        """
        Get a query object for a VS command.
        :param value:
        :param parameter_name:
        :param parameter_id:
        :param args:
        :param kwargs:
        :return:
        """
        assert parameter_name is not None or parameter_id is not None

        # search in DataFrame returns a dict
        parameter = self._find_parameter(parameter_name, parameter_id)

        # execute query
        vs = self._execute(VS(value=value, parameter=parameter, *args, **kwargs))

        # return the query with response
        return vs

    def get_parameter(self, parameter_name=None, parameter_id=None, *args, **kwargs):
        """
        Get the value of a parameter given by name or id.
        Returns a list of success and value.
        :param parameter_name:
        :param parameter_id:
        :param args:
        :param kwargs:
        :return: int or float
        """
        # get the query object
        vr = self._get(parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)

        return vr.RESPONSE.PAYLOAD[0]

    def set_parameter(self, value, parameter_name=None, parameter_id=None, *args, **kwargs):
        """
        Set the new value of a parameter given by name or id.
        Returns success.
        :param value:
        :param parameter_name:
        :param parameter_id:
        :param args:
        :param kwargs:
        :return: bool
        """
        # get the query object
        vs = self._set(value=value, parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)

        # check if value setting has succeeded
        #
        # Not necessary as we get an acknolewdge response or Value is out of range
        # exception when an invalid value was passed. 
        # current implementation also often fails due to rounding, e.g. setting 1.0
        # but returning 0.999755859375 when performing a self.get_parameter
        # value_set = self.get_parameter(parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)

        # return True if we got an ACK
        return type(vs.RESPONSE) == ACK
    
    def reset_device(self,*args, **kwargs):
        """
        Resets the device after an error has occured
        """
        rs = self._execute(RS(*args, **kwargs))
        return type(rs.RESPONSE) == ACK
    
    def info(self,*args, **kwargs):
        """
        Resets the device after an error has occured
        """
        info = self._execute(IF(*args, **kwargs))
        return info.RESPONSE.PAYLOAD


    
    # returns device address
    identify = partialmethod(get_parameter, parameter_name="Device Address")
    """
    Returns success and device address as int.
    """

    def status(self, *args, **kwargs):
        """
        Get the device status.
        Returns success and status as readable str.
        :param args:
        :param kwargs:
        :return: [bool, str]
        """
        # query device status
        status_id = self.get_parameter(parameter_name="Device Status", *args, **kwargs)

        if status_id == 0:
            status_name = "Init"
        elif status_id == 1:
            status_name = "Ready"
        elif status_id == 2:
            status_name = "Run"
        elif status_id == 3:
            status_name = "Error"
        elif status_id == 4:
            status_name = "Bootloader"
        elif status_id == 5:
            status_name = "Device will Reset within next 200ms"
        else:
            status_name = "Unknown"

        # return address and status
        return status_name

    # enable or disable auto saving to flash
    enable_autosave = partialmethod(set_parameter, value=0, parameter_name="Save Data to Flash")
    disable_autosave = partialmethod(set_parameter, value=1, parameter_name="Save Data to Flash")

    def write_to_flash(self, *args, **kwargs):
        """
        Write parameters to flash.
        :param args:
        :param kwargs:
        :return: bool
        """
        self.enable_autosave()
        timer_start = time.time()

        # value 0 means "All Parameters are saved to Flash"
        while self.get_parameter(parameter_name="Flash Status") != 0:
            # check for timeout
            if time.time() - timer_start > 10:
                raise ResponseTimeout("writing to flash timed out!")
            time.sleep(0.5)

        self.disable_autosave()

        return True


if __name__ == "__main__":
    with MeCom("/dev/ttyUSB0") as mc:
        # # which device are we talking to?
        address = mc.identify()
        status = mc.status()
        print("connected to device: {}, status: {}".format(address, status))

        # get object temperature
        temp = mc.get_parameter(parameter_name="Object Temperature", address=address)
        print("query for object temperature, measured temperature {}C".format(temp))

        # is the loop stable?
        stable_id = mc.get_parameter(parameter_name="Temperature is Stable", address=address)
        if stable_id == 0:
            stable = "temperature regulation is not active"
        elif stable_id == 1:
            stable = "is not stable"
        elif stable_id == 2:
            stable = "is stable"
        else:
            stable = "state is unknown"
        print("query for loop stability, loop {}".format(stable))

        # # setting a new device address and get again
        # new_address = 6
        # value_set = mc.set_parameter(value=new_address, parameter_name="Device Address")
        # print("setting device address to {}".format(value_set))
        #
        # # get device address again
        # address = mc.identify()
        # print("connected to device: {}".format(address))

        # set target temperature to 21C
        # success = mc.set_parameter(value=20.0, parameter_id=3000)
        # print(success)

        print("leaving with-statement, connection will be closed")
