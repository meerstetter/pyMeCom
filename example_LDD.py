"""

"""
import logging
from mecom import MeComSerial, ResponseException, WrongChecksum
from serial import SerialException


# default queries from command table below
DEFAULT_QUERIES = [
    "current",
    "max current",
]

# syntax
# { display_name: [parameter_id, unit], }
COMMAND_TABLE = {
    "Device Status": [104, ""],
    "current": [1016, "A"],
    "max current": [3020, "A"],
    "temperature": [1015, "°C"],
}


class MeerstetterLDD(object):
    """
    Controlling TEC devices via serial.
    """

    def _tearDown(self):
        self.session().stop()

    def __init__(self, port="COM6", channel=1, queries=DEFAULT_QUERIES, *args, **kwars):
        assert channel in (1, 2)
        self.channel = channel
        self.port = port
        self.queries = queries
        self._session = None
        self._connect()

    def _connect(self):
        # open session
        self._session = MeComSerial(serialport=self.port,metype = 'LDD')
        # get device address
        self.address = self._session.identify()
        logging.info("connected to {}".format(self.address))

    def session(self):
        if self._session is None:
            self._connect()
        return self._session

    def get_data(self):
        data = {}
        for description in self.queries:
            id, unit = COMMAND_TABLE[description]
            try:
                value = self.session().get_parameter(parameter_id=id, address=self.address, parameter_instance=self.channel)
                data.update({description: (value, unit)})
            except (ResponseException, WrongChecksum) as ex:
                self.session().stop()
                self._session = None
        return data

    def set_current(self, value):
        """
        Set laser diode cw current
        :param value: float
        :param channel: int
        :return:
        """
        # assertion to explicitly enter floats
        assert type(value) is float
        logging.info("set current to {} C".format(self.channel, value))
        return self.session().set_parameter(parameter_id=2001, value=value, address=self.address, parameter_instance=self.channel)
        

    def set_current_limit(self, value):
        """
        Set laser diode cw current limit
        :param value: float
        :param channel: int
        :return:
        """
        # assertion to explicitly enter floats
        assert type(value) is float
        logging.info("set current limit to {} C".format(self.channel, value))
        return self.session().set_parameter(parameter_id=3020, value=value, address=self.address, parameter_instance=self.channel)

    def _set_enable(self, enable=True):
        """
        Enable or disable control loop
        :param enable: bool
        :param channel: int
        :return:
        """
        value, description = (1, "on") if enable else (0, "off")
        logging.info("set current output to {} to {}".format(self.channel, description))
        return self.session().set_parameter(value=value, parameter_id=2020, address=self.address, parameter_instance=self.channel)

    def enable(self):
        return self._set_enable(True)

    def disable(self):
        return self._set_enable(False)


if __name__ == '__main__':
    # start logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")

    # initialize controller
    mc = MeerstetterLDD()

    # get the values from DEFAULT_QUERIES
    print(mc.get_data())
