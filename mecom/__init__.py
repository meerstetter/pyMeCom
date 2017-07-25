from serial import Serial
from serial.threaded import ReaderThread, FramedPacket

from queue import Queue

from PyCRC.CRCCCITT import CRCCCITT

import time

from struct import pack, unpack

import pandas as pd

from exceptions import ResponseException, WrongResponseSequence, WrongChecksum


class Mepacket(FramedPacket):
    START = b'!'
    STOP = "\r".encode()

    PACKET_QUEUE = Queue(maxsize=1)

    def handle_packet(self, packet):
        self.PACKET_QUEUE.put(packet)


class Meframe:
    TYPES = {"UNIT8": "!H", "UNIT16": "!L", "INT32": "!i", "FLOAT32": "!f"}

    SOURCE = ""
    ADDRESS = 0
    SEQUENCE = 0
    PAYLOAD = []
    CRC = None
    EOL = "\r"  # carriage return

    def __init__(self):
        pass

    def crc(self, in_crc=None):
        if self.CRC is None:
            self.CRC = CRCCCITT().calculate(input_data=self.compose(part=True))

        # crc check
        if in_crc is not None and in_crc != self.CRC:
            raise WrongChecksum

    def compose(self, part=False):
        # first part
        frame = self.SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
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
        frame += self.EOL
        return frame.encode()

    def _decompose_header(self, frame_bytes):
        frame = frame_bytes.decode()

        self.SOURCE = frame[0]
        self.ADDRESS = int(frame[1:3], 16)
        self.SEQUENCE = int(frame[3:7], 16)


class Query(Meframe):
    SOURCE = "#"
    PAYLOAD = ["?VR"]
    RESPONSE = None

    def __init__(self, sequence, parameter, address=0, parameter_instance=1):
        self.ADDRESS = address
        self.SEQUENCE = sequence

        # UNIT16 4 hex digits
        self.PAYLOAD.append("{:04X}".format(parameter["id"]))
        # UNIT8 2 hex digits
        self.PAYLOAD.append("{:02X}".format(parameter_instance))

        # initialize response
        self.RESPONSE = Queryresponse(parameter["response_type"])

    def set_response(self, response_frame):
        assert self.RESPONSE is not None

        # if the checksum is wrong, this statement raises
        self.RESPONSE.decompose(response_frame)

        # did we get the right response to our query?
        if self.SEQUENCE != self.RESPONSE.SEQUENCE:
            raise WrongResponseSequence


class Queryresponse(Meframe):
    SOURCE = "!"
    RESPONSE_TYPE = None

    def __init__(self, response_type):
        self.RESPONSE_TYPE = self.TYPES[response_type]

    def decompose(self, frame_bytes):
        assert self.RESPONSE_TYPE is not None
        frame_bytes = self.SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = [unpack(self.RESPONSE_TYPE, bytes.fromhex(frame[7:15]))[0]]  # convert hex to float or int
        self.crc(int(frame[15:19], 16))  # sets crc or raises


class ACKresponse(Meframe):
    SOURCE = "!"

    def crc(self, in_crc=None):
        pass

    def decompose(self, frame_bytes):
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.CRC = int(frame[7:], 16)


class Errorresponse(Meframe, ResponseException):
    SOURCE = "!"
    ERRORS = pd.DataFrame([
        {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
        {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"},
    ])

    def decompose(self, frame_bytes):
        self._decompose_header(frame_bytes)
        frame = frame_bytes.decode()
        self.PAYLOAD.append(frame[7])
        self.PAYLOAD.append(int(frame[8:10], 16))
        self.crc(int(frame[10:14], 16))


# setup serial port
CONNECTION_SETTINGS = {"baudrate": 57600, "timeout": 10}
ser = Serial(port="/dev/ttyUSB0")
ser.applySettingsDict(CONNECTION_SETTINGS)

protocol = ReaderThread(serial_instance=ser, protocol_factory=Mepacket)
receiver = protocol.__enter__()

p = {"id": 2010, "response_type": "INT32"}
#p = {"id": 1010, "response_type": "FLOAT32"}

q = Query(sequence=5547, parameter=p)
print(q.compose())

protocol.write(q.compose())

while receiver.PACKET_QUEUE.empty():
    time.sleep(0.1)

packet = receiver.PACKET_QUEUE.get()

# is it an ACK packet?
if len(packet) == 10:
    q.set_response(packet)
# is it an error packet?
if packet[7] == b'+':
    response = Errorresponse()
    response.decompose(packet)
    raise response
# nope it's a response to a parameter query
else:
    q.set_response(packet)
    print(q.RESPONSE.compose())
    print(q.RESPONSE.PAYLOAD)

protocol.stop()
