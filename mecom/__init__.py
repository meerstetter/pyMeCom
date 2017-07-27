from serial import Serial
from serial.threaded import ReaderThread, FramedPacket

from queue import Queue

from PyCRC.CRCCCITT import CRCCCITT

import time

from struct import pack, unpack

import pandas as pd

from functools import partialmethod

from exceptions import ResponseException, WrongResponseSequence, WrongChecksum, ResponseTimeout

from commands import PARAMETERS, ERRORS


class MePacket(FramedPacket):
    START = b'!'
    STOP = "\r".encode()

    PACKET_QUEUE = Queue(maxsize=1)

    def handle_packet(self, packet):
        self.PACKET_QUEUE.put(packet)


class MeFrame:
    _TYPES = {"UNIT8": "!H", "UNIT16": "!L", "INT32": "!i", "FLOAT32": "!f"}
    _SOURCE = ""
    _EOL = "\r"  # carriage return

    def __init__(self):
        self.ADDRESS = 0
        self.SEQUENCE = 0
        self.PAYLOAD = []
        self.CRC = None

    def crc(self, in_crc=None):
        if self.CRC is None:
            self.CRC = CRCCCITT().calculate(input_data=self.compose(part=True))

        # crc check
        # print(self.CRC)
        # print(in_crc)
        if in_crc is not None and in_crc != self.CRC:
            raise WrongChecksum

    def compose(self, part=False):
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload can be str or float or int
        for p in self.PAYLOAD:
            if type(p) is str:
                frame += p
            elif type(p) is int:
                frame += "{:08X}".format(p)
            elif type(p) is float:
                frame += hex(unpack('<I', pack('<f', p))[0])[2:].upper()  # please do not ask
            # frame += p if type(p) is str else "{:08X}".format(p)
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
        frame = frame_bytes.decode()

        self._SOURCE = frame[0]
        self.ADDRESS = int(frame[1:3], 16)
        self.SEQUENCE = int(frame[3:7], 16)


class Query(MeFrame):
    _SOURCE = "#"
    _PAYLOAD_START = None

    def __init__(self, parameter, sequence, address=0, parameter_instance=1):
        super().__init__()

        if hasattr(self, "_PAYLOAD_START"):
            self.PAYLOAD.append(self._PAYLOAD_START)

        self.RESPONSE = None
        self._RESPONSE_FORMAT = None

        self.ADDRESS = address
        self.SEQUENCE = sequence

        # UNIT16 4 hex digits
        self.PAYLOAD.append("{:04X}".format(parameter["id"]))
        # UNIT8 2 hex digits
        self.PAYLOAD.append("{:02X}".format(parameter_instance))

    def set_response(self, response_frame):
        # check the type of thr response
        # is it an ACK packet?
        if len(response_frame) == 10:
            self.RESPONSE = ACK()
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
    _PAYLOAD_START = "?VR"

    def __init__(self, parameter, sequence, address=0, parameter_instance=1):
        # init header (equal for get and set queries
        super().__init__(parameter=parameter,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)
        # initialize response
        self._RESPONSE_FORMAT = parameter["format"]


class VS(Query):
    _PAYLOAD_START = "VS"

    def __init__(self, value, parameter, sequence=1, address=0, parameter_instance=1):
        # init header (equal for get and set queries
        super().__init__(parameter=parameter,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)

        # the set value
        self.PAYLOAD.append(value)

        # no need to initialize response format, we want ACK


class VRResponse(MeFrame):
    _SOURCE = "!"
    _RESPONSE_FORMAT = None

    def __init__(self, response_format):
        super().__init__()
        self._RESPONSE_FORMAT = self._TYPES[response_format]

    def decompose(self, frame_bytes):
        assert self._RESPONSE_FORMAT is not None
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = [unpack(self._RESPONSE_FORMAT, bytes.fromhex(frame[7:15]))[0]]  # convert hex to float or int
        self.crc(int(frame[-4:], 16))  # sets crc or raises


class ACK(MeFrame):
    _SOURCE = "!"

    def crc(self, in_crc=None):
        pass

    def decompose(self, frame_bytes):
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.CRC = int(frame[7:], 16)


class DeviceError(MeFrame):
    _SOURCE = "!"
    ERRORS = pd.DataFrame(ERRORS)

    def compose(self, part=False):
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
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)
        frame = frame_bytes.decode()
        self.PAYLOAD.append(frame[7])
        self.PAYLOAD.append(int(frame[8:10], 16))
        self.crc(int(frame[-4:], 16))

    def error(self):
        error_code = self.PAYLOAD[1]
        # returns [code, description, symbol]
        return self.ERRORS[self.ERRORS["code"] == error_code].to_dict(orient="records")[0].values()


class MeCom:
    CONNECTION_SETTINGS = {"baudrate": 57600, "timeout": 5}
    PARAMETERS = pd.DataFrame(PARAMETERS)
    SEQUENCE_COUNTER = 1

    def __init__(self, serialport="/dev/ttyUSB0"):
        # initialize serial connection
        self.ser = Serial(port=serialport)
        self.ser.applySettingsDict(self.CONNECTION_SETTINGS)

        # start protocol thread
        self.protocol = ReaderThread(serial_instance=self.ser, protocol_factory=MePacket)
        self.receiver = self.protocol.__enter__()

    def _wait_for_response(self, snooze=0.1, timeout=5):
        wait_0 = time.time()
        while self.receiver.PACKET_QUEUE.empty():
            # check for timeout
            if wait_0 + timeout < time.time():
                raise ResponseTimeout
            time.sleep(snooze)

    def stop(self, *args, **kwargs):
        self.protocol.stop(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        self.protocol.__exit__(*args, **kwargs)

    def __enter__(self):
        return self

    def _get_parameter(self, parameter_name, parameter_id):
        return self.PARAMETERS[self.PARAMETERS["name"] == parameter_name].to_dict(orient="records")[0] if parameter_name\
            else self.PARAMETERS[self.PARAMETERS["id"] == parameter_id].to_dict(orient="records")[0]

    def _inc(self):
        self.SEQUENCE_COUNTER += 1

    @staticmethod
    def _raise(query):
        # did we encounter an error?
        if type(query.RESPONSE) is DeviceError:
            code, description, symbol = query.RESPONSE.error()
            raise ResponseException("device {} raised {}".format(query.RESPONSE.ADDRESS, description))

    def _execute(self, query):
        # send query
        self.protocol.write(query.compose())
        # print(query.compose())

        # wait for answer
        self._wait_for_response()

        # get answer from queue and attach to query
        response_frame = self.receiver.PACKET_QUEUE.get()
        # print(response_frame)
        query.set_response(response_frame)

        # did we encounter an error?
        self._raise(query)

        # clear buffers
        self.ser.reset_output_buffer()

        return query

    def _get(self, parameter_name=None, parameter_id=None, *args, **kwargs):
        assert parameter_name is not None or parameter_id is not None

        # search in DataFrame returns a dict
        parameter = self._get_parameter(parameter_name, parameter_id)

        # execute query
        vr = self._execute(VR(parameter=parameter, sequence=self.SEQUENCE_COUNTER, *args, **kwargs))

        # increment sequence counter
        self._inc()
        # print(vr.PAYLOAD)
        # print(vr.RESPONSE.PAYLOAD)
        # return the query with response
        return vr

    def _set(self, value, parameter_name=None, parameter_id=None, *args, **kwargs):
        assert parameter_name is not None or parameter_id is not None

        # search in DataFrame returns a dict
        parameter = self._get_parameter(parameter_name, parameter_id)

        # execute query
        vs = self._execute(VS(value=value, parameter=parameter, sequence=self.SEQUENCE_COUNTER, *args, **kwargs))

        # increment sequence counter
        self._inc()

        # return the query with response
        return vs

    def get_parameter(self, parameter_name=None, parameter_id=None, *args, **kwargs):
        # get the query object
        try:
            vr = self._get(parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)
        except ResponseException as ex:
            return [False, ex]

        return [True, vr.RESPONSE.PAYLOAD[0]]

    def set_parameter(self, value, parameter_name=None, parameter_id=None, *args, **kwargs):
        # get the query object
        try:
            vs = self._set(value=value, parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)
        except ResponseException as ex:
            return [False, ex]

        # check if value setting has succeeded
        state, value_set = self.get_parameter(parameter_id=parameter_id, parameter_name=parameter_name, *args, **kwargs)

        # return True if the values are equal
        return [value == value_set, value_set]

    # returns device address
    identify = partialmethod(get_parameter, parameter_name="Device Address")

    def status(self, *args, **kwargs):
        # query device status
        success, status_id = self.get_parameter(parameter_name="Device Status", *args, **kwargs)

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
        return [success, status_name]


if __name__ == "__main__":
    with MeCom("/dev/ttyUSB0") as mc:
        # # which device are we talking to?
        success_1, address = mc.identify()
        success_2, status = mc.status()
        print("success: {}, connected to device: {}, status: {}".format(success_1 and success_2, address, status))

        # get object temperature
        success, temp = mc.get_parameter(parameter_name="Object Temperature", address=address)
        print("query for object temperature succeeded: {}, measured temperature {}°C".format(success, temp))

        # is the loop stable?
        success, stable_id = mc.get_parameter(parameter_name="Temperature is Stable", address=address)
        if stable_id == 0:
            stable = "temperature regulation is not active"
        elif stable_id == 1:
            stable = "is not stable"
        elif stable_id == 2:
            stable = "is stable"
        else:
            stable = "state is unknown"
        print("query for loop stability succeeded: {}, loop {}".format(success, stable))

        # # setting a new device address and get again
        # new_address = 6
        # success, value_set = mc.set_parameter(value=new_address, parameter_name="Device Address")
        # print("setting device address to {} suceeded: {}".format(value_set, success))
        #
        # # get device address again
        # success_1, address = mc.identify()
        # success_2, status = mc.status()
        # print("success: {}, connected to device: {}, status: {}".format(success_1 and success_2, address, status))

        print("leaving with-statement, connection will be closed")
