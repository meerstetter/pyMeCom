"""
The package consists of 3 files.

commands.py contains a dictionary parameters which can be get/set
exceptions.py defines the error thrown by this pockage
mecom.py contains the communication logic

"""

from .mecom import MeCom, MeComSerial, MeComTcp, VR, VS, Parameter
from .exceptions import ResponseException, WrongChecksum
