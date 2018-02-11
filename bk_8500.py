

from serial import Serial
from array import array

import time


class bk_8500:

    def __init__(self, port='/dev/ttyUSB0', baud=9600):
        self.port = port
        self.baud = baud

        self.sp = Serial(port, baud, timeout=1)

        self.resp_status_dict = {
            0x90: "ERROR: Invalid checksum",
            0xA0: "ERROR: Invalid value",
            0xB0: "ERROR: Unable to execute",
            0xC0: "ERROR: invalid command",
            0x80: True,
        }

        self.MODE_CC = 0
        self.MODE_CV = 1
        self.MODE_CW = 2
        self.MODE_CR = 3

        self.SCALE_VOLTS = 1e3
        self.SCALE_CURRENT = 1e4
        self.SCALE_POWER = 1e3
        self.SCALE_RESIST = 1e3

    def parse_data(self, resp):
        data = resp[4] | (resp[5] << 8) | (resp[6] << 16) | (resp[7] << 24)
        print(data)
        return data

    def check_resp(self, resp):
        # Check response length
        if len(resp) == 26:

            # Confirm start byte
            if resp[0] == 0xAA:
                resp_type = resp[2]

                if resp_type == 0x12:  # Status type
                    return self.resp_status_dict[resp[3]]
                else:
                    return True

            else:
                print('Start byte mismatch')
                return None

        else:
            print('Packet length mismatch')
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
        # House cleaning, flush serial input and output bufferss
        self.sp.reset_output_buffer()
        self.sp.reset_input_buffer()

        # Send and receive
        self.sp.write(cmd_packet)
        time.sleep(0.250)  # Provide time for response
        resp_array = array('B', self.sp.read(26))  # get resp and put in array

        check = self.check_resp(resp_array)

        if check is True:
            return resp_array
        else:
            print('Response check failed')
            print(check)
            return None

    def set_remote_control(self, is_remote=True):
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
        built_packet = self.build_cmd(0x2C, value=int(max_volts * self.SCALE_VOLTS))
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
        built_packet = self.build_cmd(0x2A, value=int(max_current * self.SCALE_CURRENT))
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
        built_packet = self.build_cmd(0x2E, value=int(max_power * self.SCALE_POWER))
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
        built_packet = self.build_cmd(0x4E, value=int(max_volts * self.SCALE_VOLTS))
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_bat_volts_min(self):
        built_packet = self.build_cmd(0x4F)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            return self.parse_data(resp) / self.SCALE_VOLTS
        else:
            return None

# ----------------------------------------------------------------------------



    def SetLoadOnTimer(self, time_in_s):
        "Sets the time in seconds that the load will be on"
        msg = "Set load on timer"
        return self.SendIntegerToLoad(0x50, time_in_s, msg, num_bytes=2)
    def GetLoadOnTimer(self):
        "Gets the time in seconds that the load will be on"
        msg = "Get load on timer"
        return self.GetIntegerFromLoad(0x51, msg, num_bytes=2)
    def SetLoadOnTimerState(self, enabled=0):
        "Enables or disables the load on timer state"
        msg = "Set load on timer state"
        return self.SendIntegerToLoad(0x50, enabled, msg, num_bytes=1)
    def GetLoadOnTimerState(self):
        "Gets the load on timer state"
        msg = "Get load on timer"
        state = self.GetIntegerFromLoad(0x53, msg, num_bytes=1)
        if state == 0:
            return "disabled"
        else:
            return "enabled"

    def SetRemoteSense(self, enabled=0):
        "Enable or disable remote sensing"
        msg = "Set remote sense"
        return self.SendIntegerToLoad(0x56, enabled, msg, num_bytes=1)
    def GetRemoteSense(self):
        "Get the state of remote sensing"
        msg = "Get remote sense"
        return self.GetIntegerFromLoad(0x57, msg, num_bytes=1)
    def SetTriggerSource(self, source="immediate"):
        '''Set how the instrument will be triggered.
        "immediate" means triggered from the front panel.
        "external" means triggered by a TTL signal on the rear panel.
        "bus" means a software trigger (see TriggerLoad()).
        '''
        trigger = {"immediate":0, "external":1, "bus":2}
        if source not in trigger:
            raise Exception("Trigger type %s not recognized" % source)
        msg = "Set trigger type"
        return self.SendIntegerToLoad(0x54, trigger[source], msg, num_bytes=1)
    def GetTriggerSource(self):
        "Get how the instrument will be triggered"
        msg = "Get trigger source"
        t = self.GetIntegerFromLoad(0x59, msg, num_bytes=1)
        trigger_inv = {0:"immediate", 1:"external", 2:"bus"}
        return trigger_inv[t]
    def TriggerLoad(self):
        '''Provide a software trigger.  This is only of use when the trigger
        mode is set to "bus".
        '''
        cmd = self.StartCommand(0x5A)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Trigger load (trigger = bus)")
        return self.ResponseStatus(response)
    def SaveSettings(self, register=0):
        "Save instrument settings to a register"
        assert(self.lowest_register <= register <= self.highest_register)
        msg = "Save to register %d" % register
        return self.SendIntegerToLoad(0x5B, register, msg, num_bytes=1)
    def RecallSettings(self, register=0):
        "Restore instrument settings from a register"
        assert(self.lowest_register <= register <= self.highest_register)
        cmd = self.GetCommand(0x5C, register, num_bytes=1)
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Recall register %d" % register)
        return self.ResponseStatus(response)
    def SetFunction(self, function="fixed"):
        '''Set the function (type of operation) of the load.
        function is one of "fixed", "short", "transient", or "battery".
        Note "list" is intentionally left out for now.
        '''
        msg = "Set function to %s" % function
        functions = {"fixed":0, "short":1, "transient":2, "battery":4}
        return self.SendIntegerToLoad(0x5D, functions[function], msg, num_bytes=1)
    def GetFunction(self):
        "Get the function (type of operation) of the load"
        msg = "Get function"
        fn = self.GetIntegerFromLoad(0x5E, msg, num_bytes=1)
        functions_inv = {0:"fixed", 1:"short", 2:"transient", 4:"battery"}
        return functions_inv[fn]
    def GetInputValues(self):
        '''Returns voltage in V, current in A, and power in W, op_state byte,
        and demand_state byte.
        '''
        cmd = self.StartCommand(0x5F)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get input values")
        voltage = self.DecodeInteger(response[3:7])/self.convert_voltage
        current = self.DecodeInteger(response[7:11])/self.convert_current
        power   = self.DecodeInteger(response[11:15])/self.convert_power
        op_state = hex(self.DecodeInteger(response[15]))
        demand_state = hex(self.DecodeInteger(response[16:18]))
        s = [str(voltage) + " V", str(current) + " A", str(power) + " W", str(op_state), str(demand_state)]
        return join(s, "\t")
    # Returns model number, serial number, and firmware version number
    def GetProductInformation(self):
        "Returns model number, serial number, and firmware version"
        cmd = self.StartCommand(0x6A)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get product info")
        model = response[3:8]
        fw = hex(ord(response[9]))[2:] + "."
        fw += hex(ord(response[8]))[2:]
        serial_number = response[10:20]
        return join((str(model), str(serial_number), str(fw)), "\t")
