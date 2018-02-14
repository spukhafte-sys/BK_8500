
from bk_8500 import bk_8500
from bk_9115 import bk_9115
from data_logging import data_logging

import time

bk_load = bk_8500(port='/dev/ttyUSB1')
bk_supply = bk_9115(port='/dev/ttyUSB2')
d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'])

PS_VOLTS_LIMIT = 4.25

CHARGE_VOLTAGE = 4.15
CHARGE_AMP_CUT = 0.4
CHARGE_CURRENT = 25

DISCHARGE_VOLTAGE = 2.75
DISCHARGE_CURRENT = 30

test_start_time = 0
test_current_time = 0
TIME_INTERVAL = 4

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
        bk_supply.set_remote_sense(is_remote=True)


def start_test_load():

    init_bk_8500()

    bk_load.set_bat_volts_min(min_volts=2.75)
    bk_load.set_CC_current(cc_current=30)
    bk_load.set_fuction(bk_load.FUNC_BATT)
    bk_load.set_enable_load(is_enabled=True)
    time.sleep(1)

    is_running = True

    while is_running:
        reading = bk_load.get_input_values()
        if reading is not None:
            d_log.write_data([time.time(), reading[0], reading[1], reading[2], 0, 0])

        if reading[4] == '0x0':
            print('Battery test complete')
            is_running = False

        time.sleep(TIME_INTERVAL)

    print('Finish load test')
    bk_load.set_enable_load(is_enabled=False)


def start_test_supply():

    print('Put power supply in safe default state')
    bk_supply.clear()
    bk_supply.set_remote(is_remote=True)
    bk_supply.set_output_enable(is_enabled=False)
    bk_supply.set_output_range(volts_max=PS_VOLTS_LIMIT)

    is_running = True

    time.sleep(TIME_INTERVAL)
    print('Put power supply in charging state')
    bk_supply.set_output_enable(is_enabled=True)
    bk_supply.set_output_values(voltage=CHARGE_VOLTAGE, current=CHARGE_CURRENT)

    print('Entering test loop')
    time.sleep(TIME_INTERVAL)

    while is_running:

        reading = bk_supply.reading_measure()
        print(reading)
        d_log.write_data([time.time(), float(reading[0]), float(reading[1]), float(reading[2]), 0, 0])

        # Check if amps have reduced to target
        if float(reading[1]) <= CHARGE_AMP_CUT:
            print('End of test loop')
            is_running = False

        time.sleep(TIME_INTERVAL)

    print('Shut down test')
    bk_supply.set_output_enable(is_enabled=False)
    bk_supply.close()
