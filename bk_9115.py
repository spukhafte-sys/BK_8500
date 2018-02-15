
from serial import Serial

import time


class bk_9115:

    def __init__(self, port='/dev/ttyUSB1', baud=9600):

        self.sp = Serial(port, baud, timeout=1)

    def close(self):
        self.sp.close()

    def read(self):
        resp = self.sp.readline()
        return resp.strip()

    def write(self, write_string):
        # Clean up port buffers
        self.sp.reset_output_buffer()
        self.sp.reset_input_buffer()

        # Build and send string
        send_string = write_string + '\r\n'
        self.sp.write(send_string.encode())
        time.sleep(0.25)

    def write_read(self, write_string):
        self.write(write_string)
        return self.read()

    def clear(self):
        self.write('system:clear')

    def get_device_info(self):
        return self.write_read('*IDN?')

    def reading_error(self):
        return self.write_read('system:error?')

    def set_remote(self, is_remote=False):
        if is_remote is True:
            self.write('system:remote')
        else:
            self.write('system:locale')

    def set_output_enable(self, is_enabled=False):
        if is_enabled is True:
            self.write('output on')
        else:
            self.write('output off')
        return self.write_read('output?')

    def set_output_range(self, volts_min=None, volts_max=None):
        if volts_min is not None:
            self.write('voltage:limit ' + str(volts_min))
        if volts_max is not None:
            self.write('voltage:range ' + str(volts_max))

    def reading_range(self):
        volts_min = self.write_read('voltage:limit?')
        volts_max = self.write_read('voltage:range?')
        return (volts_min, volts_max)

    def set_output_values(self, voltage=None, current=None):
        if voltage is not None:
            self.write('voltage ' + str(voltage))
        if current is not None:
            self.write('current ' + str(current))

    def reading_measure(self):
        volts = float(self.write_read('measure:voltage?'))
        amps = float(self.write_read('measure:current?'))
        pwr = float(self.write_read('measure:power?'))
        return (volts, amps, pwr)
