
from bk_8500 import bk_8500
from bk_9115 import bk_9115
from data_logging import data_logging

import time

bk_load = bk_8500(port='/dev/ttyUSB0')
bk_supply = bk_9115(port='/dev/ttyUSB1')
d_log = None

PS_VOLTS_LIMIT = 4.2

CHARGE_VOLTAGE = 4.03  # Used for CV mode charger setting
CHARGE_VOLT_CUT = 4.15  # Used for hard cutoff voltage
CHARGE_AMP_CUT = 0.5  # When current drops to this level end charge
CHARGE_CURRENT = 15  #

DISCHARGE_VOLTAGE = 3.35  # Discharge hard cut off voltage
DISCHARGE_CURRENT = 30  # Discharge constant current

TIME_INTERVAL = 5  # Logging intervals
REST_COUNT = 35


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
    data_list = [time_now, reading[0], reading[1], reading[2], ah, 0]
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


def start_test_load():

    print('Setup load and logging')
    init_bk_8500()
    global d_log
    d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'], log_file_postfix='LOAD')


    is_running = True
    ah_counter = 0
    time_last_logged = time.time()

    # Log and update
    print('Log with no load')
    resp = reading_8500(time_last_logged, ah_counter)
    time_last_logged = resp[0]
    ah_counter = resp[1]

    print('Setup load for battery test')
    bk_load.set_bat_volts_min(min_volts=DISCHARGE_VOLTAGE)
    bk_load.set_CC_current(cc_current=DISCHARGE_CURRENT)
    bk_load.set_function(bk_load.FUNC_BATT)
    bk_load.set_enable_load(is_enabled=True)

    time.sleep(1)

    if bk_load.get_function() == bk_load.FUNC_BATT:

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

        print('Finale log with no load')
    for rest in range(REST_COUNT):
        time.sleep(TIME_INTERVAL)

        # Log and update
        resp = reading_8500(time_last_logged, ah_counter)
        time_last_logged = resp[0]
        ah_counter = resp[1]
        is_running = resp[2]

    print('Finish load test')
    bk_load.set_enable_load(is_enabled=False)
    bk_load.close()


def start_test_supply():

    print('Put power supply in safe default state')
    bk_supply.clear()
    bk_supply.set_remote(is_remote=True)
    bk_supply.set_output_enable(is_enabled=False)
    bk_supply.set_output_range(volts_max=PS_VOLTS_LIMIT)

    global d_log
    d_log = data_logging(['Time', 'volts', 'current', 'watts', 'amp_hour', 'watt_hour'], log_file_postfix='SUPPLY')

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
        if resp[1] >= CHARGE_VOLT_CUT:
            print('Volt cutoff level detected')
            is_running = False

        time.sleep(TIME_INTERVAL)

    bk_supply.set_output_enable(is_enabled=False)

    print('Final log with no charge')
    for rest in range(REST_COUNT):
        time.sleep(TIME_INTERVAL)

        #Log and update
        resp = reading_9115(time_last_logged, ah_counter)
        time_last_logged = resp[0]
        ah_counter = resp[4]

    print('Shut down test')
    bk_supply.close()
