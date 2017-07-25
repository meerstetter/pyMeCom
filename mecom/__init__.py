from serial import Serial
from serial.threaded import ReaderThread, FramedPacket

from PyCRC.CRCCCITT import CRCCCITT

import time

# carriage return
CR = "\r".encode()

class Mepacket(FramedPacket):
    START = b'!'
    STOP = CR

    def handle_packet(self, packet):
        print(packet)

class Frame:
    source = "".encode()
    address =
    sequence
    payload = []
    crc = None
    eof = CR

    def __init__(self):
        pass


# setup serial port

ser = Serial("/dev/ttyUSB0")
ser.baudrate = 57600
ser.timeout = 1

with ReaderThread(ser, Mepacket) as protocol:

    source = b'#'
    address = b'00'
    sequence =

    ser.write(b'#0015AB?VR0064018000' + CR)
    time.sleep(5)