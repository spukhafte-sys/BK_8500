
from bk_8500 import bk_8500
from bk_9115 import bk_9115
from data_logging import data_logging

import time

bk_load = bk_8500()
bk_supply = bk_9115()
d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'])


def init_bk_8500():
    # Setup load
    if bk_load.get_device_info() is not None:
        print('Set to remote control')
        bk_load.set_remote_control(is_remote=True)
        print('Disable load')
        bk_load.set_enable_load(is_enabled=False)
        print('Set to CC mode')
        bk_load.set_mode(bk_load.MODE_CC)
        print('Set max volts to 18')
        bk_load.set_max_volts(max_volts=18)
        print('Set max current to 30')
        bk_load.set_max_current(max_current=30)
        print('Set max power to 300')
        bk_load.set_max_power(max_power=300)
        print('set CC level to 0')
        bk_load.set_CC_current(cc_current=0)


def init_bk_9115():
    # Setup supply
    if bk_supply.get_device_info is not None:
        bk_supply.clear()
        bk_supply.set_remote(is_remote=True)
        bk_supply.set_output_enable(is_enabled=False)


def start_test_load():
        bk_load.set_CC_current(cc_current=2)
        bk_load.set_enable_load(is_enabled=True)
        time.sleep(1)
        reading = bk_load.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk_load.set_CC_current(cc_current=1)
        time.sleep(1)
        reading = bk_load.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk_load.set_CV_volts(cv_volts=12.25)
        bk_load.set_mode(bk_load.MODE_CV)
        time.sleep(1)
        reading = bk_load.get_input_values()
        if reading is not None:
            d_log.write_data([reading[0], reading[1], reading[2]])
        time.sleep(1)
        bk_load.set_enable_load(is_enabled=False)


def start_test_supply():
    pass
