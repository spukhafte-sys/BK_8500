
from bk_8500 import bk_8500
from data_logging

import time

bk = bk_8500()
d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'])


def init_device():
    if bk.get_device_info() is not None:
        print('Set to remote control')
        bk.set_remote_control(is_remote=True)
        print('Disable load')
        bk.set_enable_load(is_enabled=False)
        print('Set to CC mode')
        bk.set_mode(bk.MODE_CC)
        print('Set max volts to 18')
        bk.set_max_volts(max_volts=18)
        print('Set max current to 30')
        bk.set_max_current(max_current=30)
        print('Set max power to 300')
        bk.set_max_power(max_power=300)
        print('set CC level to 0')
        bk.set_CC_current(cc_current=0)



def start_test_load():
        bk.set_CC_current(cc_current=2)
        bk.set_enable_load(is_enabled=True)
        time.sleep(1)
        reading = bk.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk.set_CC_current(cc_current=1)
        time.sleep(1)
        reading = bk.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk.set_CV_volts(cv_volts=12.25)
        bk.set_mode(bk.MODE_CV)
        time.sleep(1)
        reading = bk.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk.set_enable_load(is_enabled=False)
