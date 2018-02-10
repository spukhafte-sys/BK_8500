

from serial import Serial
from array import array

import time


class bk_8500:

    def __init__(self, port='/dev/ttyUSB0', baud=9600):
        self.port = port
        self.baud = baud

        self.sp = Serial(port, baud, timeout=0.250)

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

        self.MULTI_VOLTS = 1e3
        self.MULTI_AMPS = 1e4
        self.MULTI_POWER = 1e3
        self.MULTI_RESIST = 1e3

    def parse_data(self, resp):
        data = resp[4] | (resp[5] << 8) | (resp[6] << 16) | (resp[7] << 24)
        print(data)
        return data

    def check_resp(self, resp):
        # Check response
        resp_valid = resp[0] == 0xAA  # Confirm start byte
        resp_type = resp[2]  # Says what type of response it is
        resp_status = self.resp_status_dict[resp[3]]  # Get response type

        # Check to see if respons valis
        if resp_valid is True:

            # If status packet
            if resp_type == 0x12:
                # Return response message if not True
                return resp_status  # Get response type
            else:
                return True
        else:
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
        print(resp_array)

        check = self.check_resp(resp_array)

        if check is True:
            return resp_array
        else:
            print('Response check failed')
            print(check)
            return None

    def set_remote_control(self, is_remote=True):
        cmd = 0x20
        value = int(is_remote)
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_mode(self, mode):
        cmd = 0x28
        value = mode
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_enable_load(self, is_enabled=False):
        cmd = 0x21
        value = int(is_enabled)
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def set_max_volts(self, max_volts=0):
        cmd = 0x22
        value = int(max_volts * self.MULTI_VOLTS) & 0xFFFF
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_volts(self):
        cmd = 0x23
        built_packet = self.build_cmd(cmd)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            data = self.parse_data(resp) / self.MULTI_VOLTS
            return data
        else:
            return None

    def set_max_amps(self, max_amps=0):
        cmd = 0x24
        value = int(max_amps * self.MULTI_AMPS) & 0xFFFF
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_amps(self):
        cmd = 0x25
        built_packet = self.build_cmd(cmd)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            data = self.parse_data(resp) / self.MULTI_VOLTS
            return data
        else:
            return None

    def set_max_power(self, max_power=0):
        cmd = 0x24
        value = int(max_power * self.MULTI_POWER) & 0xFFFF
        built_packet = self.build_cmd(cmd, value=value)
        resp = self.send_recv_cmd(built_packet)
        return resp

    def get_max_power(self):
        cmd = 0x27
        built_packet = self.build_cmd(cmd)
        resp = self.send_recv_cmd(built_packet)
        if resp is not None:
            data = self.parse_data(resp) / self.MULTI_VOLTS
            return data
        else:
            return None

# ----------------------------------------------------------------------------

    def GetMode(self):
        "Gets the mode (constant current, constant voltage, etc."
        msg = "Get mode"
        mode = self.GetIntegerFromLoad(0x29, msg, num_bytes=1)
        modes_inv = {0:"cc", 1:"cv", 2:"cw", 3:"cr"}
        return modes_inv[mode]

    def SetCCCurrent(self, current):
        "Sets the constant current mode's current level"
        msg = "Set CC current"
        return self.SendIntegerToLoad(0x2A, current*self.convert_current, msg, num_bytes=4)

    def GetCCCurrent(self):
        "Gets the constant current mode's current level"
        msg = "Get CC current"
        return self.GetIntegerFromLoad(0x2B, msg, num_bytes=4)/self.convert_current

    def SetCVVoltage(self, voltage):
        "Sets the constant voltage mode's voltage level"
        msg = "Set CV voltage"
        return self.SendIntegerToLoad(0x2C, voltage*self.convert_voltage, msg, num_bytes=4)

    def GetCVVoltage(self):
        "Gets the constant voltage mode's voltage level"
        msg = "Get CV voltage"
        return self.GetIntegerFromLoad(0x2D, msg, num_bytes=4)/self.convert_voltage
    def SetCWPower(self, power):
        "Sets the constant power mode's power level"
        msg = "Set CW power"
        return self.SendIntegerToLoad(0x2E, power*self.convert_power, msg, num_bytes=4)

    def GetCWPower(self):
        "Gets the constant power mode's power level"
        msg = "Get CW power"
        return self.GetIntegerFromLoad(0x2F, msg, num_bytes=4)/self.convert_power

    def SetCRResistance(self, resistance):
        "Sets the constant resistance mode's resistance level"
        msg = "Set CR resistance"
        return self.SendIntegerToLoad(0x30, resistance*self.convert_resistance, msg, num_bytes=4)

    def GetCRResistance(self):
        "Gets the constant resistance mode's resistance level"
        msg = "Get CR resistance"
        return self.GetIntegerFromLoad(0x31, msg, num_bytes=4)/self.convert_resistance

    def SetTransient(self, mode, A, A_time_s, B, B_time_s, operation="continuous"):
        '''Sets up the transient operation mode.  mode is one of
        "CC", "CV", "CW", or "CR".
        '''
        if mode.lower() not in self.modes:
            raise Exception("Unknown mode")
        opcodes = {"cc":0x32, "cv":0x34, "cw":0x36, "cr":0x38}
        if mode.lower() == "cc":
            const = self.convert_current
        elif mode.lower() == "cv":
            const = self.convert_voltage
        elif mode.lower() == "cw":
            const = self.convert_power
        else:
            const = self.convert_resistance
        cmd = self.StartCommand(opcodes[mode.lower()])
        cmd += self.CodeInteger(A*const, num_bytes=4)
        cmd += self.CodeInteger(A_time_s*self.to_ms, num_bytes=2)
        cmd += self.CodeInteger(B*const, num_bytes=4)
        cmd += self.CodeInteger(B_time_s*self.to_ms, num_bytes=2)
        transient_operations = {"continuous":0, "pulse":1, "toggled":2}
        cmd += self.CodeInteger(transient_operations[operation], num_bytes=1)
        cmd += self.Reserved(16)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Set %s transient" % mode)
        return self.ResponseStatus(response)
    def GetTransient(self, mode):
        "Gets the transient mode settings"
        if mode.lower() not in self.modes:
            raise Exception("Unknown mode")
        opcodes = {"cc":0x33, "cv":0x35, "cw":0x37, "cr":0x39}
        cmd = self.StartCommand(opcodes[mode.lower()])
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get %s transient" % mode)
        A = self.DecodeInteger(response[3:7])
        A_timer_ms = self.DecodeInteger(response[7:9])
        B = self.DecodeInteger(response[9:13])
        B_timer_ms = self.DecodeInteger(response[13:15])
        operation = self.DecodeInteger(response[15])
        time_const = 1e3
        transient_operations_inv = {0:"continuous", 1:"pulse", 2:"toggled"}
        if mode.lower() == "cc":
            return str((A/self.convert_current, A_timer_ms/time_const,
                    B/self.convert_current, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        elif mode.lower() == "cv":
            return str((A/self.convert_voltage, A_timer_ms/time_const,
                    B/self.convert_voltage, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        elif mode.lower() == "cw":
            return str((A/self.convert_power, A_timer_ms/time_const,
                    B/self.convert_power, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        else:
            return str((A/self.convert_resistance, A_timer_ms/time_const,
                    B/self.convert_resistance, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
    def SetBatteryTestVoltage(self, min_voltage):
        "Sets the battery test voltage"
        msg = "Set battery test voltage"
        return self.SendIntegerToLoad(0x4E, min_voltage*self.convert_voltage, msg, num_bytes=4)
    def GetBatteryTestVoltage(self):
        "Gets the battery test voltage"
        msg = "Get battery test voltage"
        return self.GetIntegerFromLoad(0x4F, msg, num_bytes=4)/self.convert_voltage
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
    def SetCommunicationAddress(self, address=0):
        '''Sets the communication address.  Note:  this feature is
        not currently supported.  The communication address should always
        be set to 0.
        '''
        msg = "Set communication address"
        return self.SendIntegerToLoad(0x54, address, msg, num_bytes=1)
    def EnableLocalControl(self):
        "Enable local control (i.e., key presses work) of the load"
        msg = "Enable local control"
        enabled = 1
        return self.SendIntegerToLoad(0x55, enabled, msg, num_bytes=1)
    def DisableLocalControl(self):
        "Disable local control of the load"
        msg = "Disable local control"
        disabled = 0
        return self.SendIntegerToLoad(0x55, disabled, msg, num_bytes=1)
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
