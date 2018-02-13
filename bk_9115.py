

import time


class bk_9115:

    def __init__(self, com_type='USBTMC', device='/dev/usbtmc0'):

        self.com_type = com_type
        self.COM_TYPE_USB = 'USBTMC'
        self.COM_TYPE_SERIAL = 'SERIAL'
        self.device = device

        self.instrument = None

        if self.com_type == self.COM_TYPE_USB:
            self.instrument = open(self.device, 'r+')
        elif self.com_type == self.COM_TYPE_SERIAL:
            pass
        else:
            print('Communication type not supported')

    def close(self):
        self.instrument.close()
        time.sleep(0.250)

    def read(self):
        resp = self.instrument.read(4096)
        return resp

    def write(self, write_string):
        self.instrument.write(write_string)
        time.sleep(0.250)

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
        time.sleep(0.500)
        return self.write_read('output?')

    def set_output_range(self, voltage, current, power):
        self.write('volage:range ' + str(voltage))
        self.write('current:range ' + str(current))
        self.write('power:range ' + str(power))

    def reading_range(self):
        volts = self.write_read('voltage?')
        amps = self.write_read('current?')
        pwr = self.write.read('power?')
        return (volts, amps, pwr)

    def set_output_values(self, voltage=None, current=None, power=None):
        if voltage is not None:
            self.write('votlage ' + str(voltage))
        if current is not None:
            self.write('current ' + str(current))
        if power is not None:
            self.write('power ' + str(power))

    def reading_measure(self):
        volts = self.write_read('measure:voltage?')
        amps = self.write_read('measure:current?')
        pwr = self.write_read('measure:power?')
        return (volts, amps, pwr)
