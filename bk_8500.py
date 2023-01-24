

#from serial import Serial
from array import array

import time, sys


class bk_8500:

    def __init__(self, instr, kwargs={}):
        self.__dict__.update(kwargs)

#       self.sp = Serial(port, baud, timeout=1)
        self.instr = instr

        self.resp_status_dict = {
            0x90: "ERROR: Invalid checksum",
            0xA0: "ERROR: Invalid value",
            0xB0: "ERROR: Unable to execute",
            0xC0: "ERROR: Invalid command",
            0xD0: "ERROR: Undocumented error",
            0x80: True,
        }

        self.MODE_CC = 0
        self.MODE_CV = 1
        self.MODE_CW = 2
        self.MODE_CR = 3

        self.FUNC_FIXED = 0
        self.FUNC_SHORT = 1
        self.FUNC_TRANS = 2
        self.FUNC_LIST = 3
        self.FUNC_BATT = 4

        self.SCALE_VOLTS = 1e3
        self.SCALE_CURRENT = 1e4
        self.SCALE_POWER = 1e3
        self.SCALE_RESIST = 1e3

        self.TRIG_MAN = 0
        self.TRIG_EXT = 1
        self.TRIG_BUS = 2
        self.TRIG_HOLD = 3

    def close(self):
        self.instr.close()

    def parse_data(self, resp):
        data = resp[4] | (resp[5] << 8) | (resp[6] << 16) | (resp[7] << 24)
        print(data)
        return data

    def check_resp(self, resp):
        # Check response length
        if len(resp) == 26:

            # Confirm start byte
            if resp[0] == 0xAA: # or resp[0] == 0x27:
                resp_type = resp[2]

                if resp_type == 0x12:  # Status type
                    status = resp[3]
                    if status in self.resp_status_dict:
                        return self.resp_status_dict[status]
                    else:
                        return('ERROR: Unknown status: 0x%X' % status)
                else:
                    return True

            else:
                print('Start byte mismatch: %s' % resp)
                return None

        else:
            print('Packet length mismatch: %s' % resp)
            return None

    def build_cmd(self, cmd, value=None):
        build_cmd = array('B', [0x00]*26)

        build_cmd[0] = 0xAA  # Packet start
        build_cmd[1] = 0x00  # Unsupported address location
        build_cmd[2] = cmd & 0xFF  # Command value

        if value is not None:
            build_cmd[3] = value & 0xFF  # value 1st byte little endian
            build_cmd[4] = (value >> 8) & 0xFF  # value 2nd byte little endian
            build_cmd[5] = (value >> 16) & 0xFF  # value 3rd byte little endian
            build_cmd[6] = (value >> 24) & 0xFF  # value 4th byte little endian

        checksum = 0
        for item in build_cmd:
            checksum += item
        checksum %= 256

        build_cmd[25] = checksum & 0xFF

        return build_cmd.tobytes()

    def send_recv_cmd(self, cmd_packet):
        # House cleaning, flush serial input and output buffers
#       self.instr.reset_output_buffer()
        i = self.instr.timeout  # Flush buffer
        self.instr.timeout = 10
        self.instr.read_raw()
        self.instr.timeout = i

        # Send and receive
        self.instr.write_raw(cmd_packet)
        time.sleep(0.50)  # Provide time for response
        mark = time.time()
        resp_array = array('B', self.instr.read_raw(26))  # get resp and put in array
        n = 10
        while n:
            n -= 1
            j = len(resp_array)
            if j >= 26:
                break
            else:
                resp_array += array('B', self.instr.read_raw(26-j))
                print('.', end='', file=sys.stderr)

        check = self.check_resp(resp_array)

        if check is True:
            return resp_array
        else:
            print('Response check failed')
            print(check)
            return None

    def get_device_info(self):
        built_packet = self.build_cmd(0x6A)
        resp = self.send_recv_cmd(built_packet)

        if resp is not None:
            model = chr(resp[3]) + chr(resp[4]) + chr(resp[5])
            version = str(resp[9]) + '.' + str(resp[8])
            serial = chr(resp[10]) + chr(resp[11]) + chr(resp[12]) + chr(resp[13]) + chr(resp[14]) + chr(resp[16]) + chr(resp[17]) + chr(resp[18]) + chr(resp[19])
            return (model, version, serial)
        else:
            return None

    def get_input_values(self):
        built_packet = self.build_cmd(0x5F)
        resp = self.send_recv_cmd(built_packet)

        if resp is not None:
            volts = (resp[3] | (resp[4] << 8) | (resp[5] << 16) | (resp[6] << 24)) / self.SCALE_VOLTS
            current = (resp[7] | (resp[8] << 8) | (resp[9] << 16) | (resp[10] << 24)) / self.SCALE_CURRENT
            power = (resp[11] | (resp[12] << 8) | (resp[13] << 16) | (resp[14] << 24)) / self.SCALE_POWER
            op_state = hex(resp[15])
            demand_state = hex(resp[16] | (resp[17] << 8))
            return (volts, current, power, op_state, demand_state)
        else:
            return None

    def set_trigger(self, source):
        built_packet = self.build_cmd(0x58, value=source)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_trigger(self):
        built_packet = self.build_cmd(0x59)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return resp[3]
        else:
            return None

    def trigger(self):
        built_packet = self.build_cmd(0x5A)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def recall_user_settings(self, location):
        built_packet = self.build_cmd(0x5C, value=location)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_function(self, function):
        built_packet = self.build_cmd(0x5D, value=function)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_function(self):
        built_packet = self.build_cmd(0x5E)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return resp[3]
        else:
            return None

    def set_remote_sense(self, is_remote=False):
        built_packet = self.build_cmd(0x56, value=int(is_remote))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_remote_sense(self):
        built_packet = self.build_cmd(0x57)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp)
        else:
            return None

    def get_eload_info(self):
        built_packet = self.build_cmd(0xA1)
        resp = self.send_recv_cmd(built_packet)

        if resp is not None:
            model = chr(resp[3]) + chr(resp[4]) + chr(resp[5])
            version = str(resp[9]) + '.' + str(resp[8])
            serial = chr(resp[10]) + chr(resp[11]) + chr(resp[12]) + chr(resp[13]) + chr(resp[14]) + chr(resp[16]) + chr(resp[17]) + chr(resp[18]) + chr(resp[19])
            return (model, version, serial)
        else:
            return None

    def get_min_current(self):
        built_packet = self.build_cmd(0xA5)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return resp[3] + (resp[4]<<8) + (resp[5]<<16) + (resp[6]<<24)
        else:
            return None

    def get_capacity(self):
        built_packet = self.build_cmd(0xA6)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return resp[3] + (resp[4]<<8) + (resp[5]<<16) + (resp[6]<<24)
        else:
            return None

    def set_remote_control(self, is_remote=False):
        built_packet = self.build_cmd(0x20, value=int(is_remote))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_local_control(self, is_local=True):
        built_packet = self.build_cmd(0x55, value=int(is_local))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_mode(self, mode):
        built_packet = self.build_cmd(0x28, value=mode)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_mode(self):
        built_packet = self.build_cmd(0x29)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp)
        else:
            return None

    def set_enable_load(self, is_enabled=False):
        built_packet = self.build_cmd(0x21, value=int(is_enabled))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_max_volts(self, max_volts=0):
        built_packet = self.build_cmd(0x22, value=int(max_volts * self.SCALE_VOLTS))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_volts(self):
        built_packet = self.build_cmd(0x23)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_VOLTS
        else:
            return None

    def set_max_current(self, max_current=0):
        built_packet = self.build_cmd(0x24, value=int(max_current * self.SCALE_CURRENT))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_current(self):
        built_packet = self.build_cmd(0x25)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_CURRENT
        else:
            return None

    def set_max_power(self, max_power=0):
        built_packet = self.build_cmd(0x24, value=int(max_power * self.SCALE_POWER))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_power(self):
        built_packet = self.build_cmd(0x27)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_VOLTS
        else:
            return None

    def set_CV_volts(self, cv_volts=0):
        built_packet = self.build_cmd(0x2C, value=int(cv_volts * self.SCALE_VOLTS))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_CV_volts(self):
        built_packet = self.build_cmd(0x2D)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_VOLTS
        else:
            return None

    def set_CC_current(self, cc_current=0):
        built_packet = self.build_cmd(0x2A, value=int(cc_current * self.SCALE_CURRENT))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_CC_current(self):
        built_packet = self.build_cmd(0x2B)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_CURRENT
        else:
            return None

    def set_CP_power(self, cp_power=0):
        built_packet = self.build_cmd(0x2E, value=int(cp_power * self.SCALE_POWER))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_CP_power(self):
        built_packet = self.build_cmd(0x2F)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_POWER
        else:
            return None

    def set_CR_resistance(self, cr_resistance=0):
        built_packet = self.build_cmd(0x30, value=int(cr_resistance * self.SCALE_RESIST))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_CR_resistance(self):
        built_packet = self.build_cmd(0x31)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_RESIST
        else:
            return None

    def set_bat_volts_min(self, min_volts=3):
        built_packet = self.build_cmd(0x4E, value=int(min_volts * self.SCALE_VOLTS))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_bat_volts_min(self):
        built_packet = self.build_cmd(0x4F)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_VOLTS
        else:
            return None

    def send_cmd(self, cmd):
        built_packet = self.build_cmd(cmd)
        resp = self.send_recv_cmd(built_packet)
        return resp
