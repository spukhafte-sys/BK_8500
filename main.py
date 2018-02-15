
from bk_8500 import bk_8500
from bk_9115 import bk_9115
from data_logging import data_logging

import time

bk_load = bk_8500(port='/dev/ttyUSB0')
bk_supply = bk_9115(port='/dev/ttyUSB1')
d_log = None

PS_VOLTS_LIMIT = 4.25

CHARGE_VOLTAGE = 4.15
CHARGE_AMP_CUT = 0.4
CHARGE_CURRENT = 25

DISCHARGE_VOLTAGE = 2.75
DISCHARGE_CURRENT = 30

test_start_time = 0
test_current_time = 0
TIME_INTERVAL = 5

def init_bk_8500():
    # Setup load
    if bk_load.get_device_info() is not None:
        print('Set to remote control')
        bk_load.set_remote_control(is_remote=True)
        print('Disable load')
        bk_load.set_enable_load(is_enabled=False)
        print('Set function to fixed')
        bk_load.set_function(bk_load.FUNC_FIXED)
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
        return True
    else:
        return False

def start_test_load():

    init_bk_8500()

    d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'], log_file_postfix='LOAD')

    print('Setup load for battery test')
    bk_load.set_bat_volts_min(min_volts=DISCHARGE_VOLTAGE)
    bk_load.set_CC_current(cc_current=DISCHARGE_CURRENT)
    bk_load.set_function(bk_load.FUNC_BATT)

    if bk_load.get_function() == bk_load.FUNC_BATT:

        is_running = True
        ah_counter = 0
        time_last_logged = time.time()

        time.sleep(1)

        # Log and update
        resp = reading_8500(time_last_logged, ah_counter)
        time_last_logged = resp[0]
        ah_counter = resp[1]

        print('Enabel load')
        bk_load.set_enable_load(is_enabled=True)

        time.sleep(1)

        print('Start main loop')
        while is_running:

            # Log and update
            resp = reading_8500(time_last_logged, ah_counter)
            time_last_logged = resp[0]
            ah_counter = resp[1]
            is_running = resp[2]

            time.sleep(TIME_INTERVAL)
    else:
        print('Not in battery function')

    print('Finish load test')
    bk_load.set_enable_load(is_enabled=False)


def ah_calc(time_last, time_now, amp_sample):
    delta_time_hrs = ((time_now - time_last) / 60) / 60
    ah = amp_sample * delta_time_hrs
    return ah

def reading_8500(last_time, ah_counter, logging=True):
    # Read data from power supply
    reading = bk_load.get_input_values()
    # Get current time and calculated Ah
    time_now = time.time()
    ah = ah_counter + ah_calc(last_time, time_now, reading[1])
    # Build data list [Time, Volts, Amps, Watts, Ah, Wh, status]
    data_list = [time.time(), reading[0], reading[1], reading[2], ah, 0]
    # Log data
    if logging is True:
        d_log.write_data(data_list, debug=True)

    if reading[4] == '0x0':
        return (time_now, ah, False)
    else:
        return (time_now, ah, True)


def reading_9115(last_time, ah_counter, logging=True):
    # Read data from power supply
    reading = bk_supply.reading_measure()
    # Get current time and calculated Ah
    time_now = time.time()
    ah = ah_counter + ah_calc(last_time, time_now, reading[1])
    # Build data list [Time, Volts, Amps, Watts, Ah, Wh, status]
    data_list = [time_now, reading[0], reading[1], reading[2], ah, 0]
    # Log data
    if logging is True:
        d_log.write_data(data_list, debug=True)

    return data_list


def start_test_supply():

    d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'], log_file_postfix='SUPPLY')

    print('Put power supply in safe default state')
    bk_supply.clear()
    bk_supply.set_remote(is_remote=True)
    bk_supply.set_output_enable(is_enabled=False)
    bk_supply.set_output_range(volts_max=PS_VOLTS_LIMIT)

    is_running = True
    ah_counter = 0
    time_last_logged = time.time()

    time.sleep(1)

    # Log and update
    resp = reading_9115(time_last_logged, ah_counter)
    time_last_logged = resp[0]
    ah_counter = resp[4]

    print('Put power supply in charging state')
    bk_supply.set_output_enable(is_enabled=True)
    bk_supply.set_output_values(voltage=CHARGE_VOLTAGE, current=CHARGE_CURRENT)

    print('Entering test loop')
    time.sleep(1)

    while is_running:

        #Log and update
        resp = reading_9115(time_last_logged, ah_counter)
        time_last_logged = resp[0]
        ah_counter = resp[4]
        if resp[2] <= CHARGE_AMP_CUT:
            print('Amp cutoff value detected')
            is_running = False

        time.sleep(TIME_INTERVAL)

    print('Shut down test')
    bk_supply.set_output_enable(is_enabled=False)
    bk_supply.close()
