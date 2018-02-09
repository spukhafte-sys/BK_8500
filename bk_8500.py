

from serial import Serial
from array import array

import time

class bk_8500:

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud

        self.sp = Serial(port, baud, timeout=0.250)

    def build_cmd(self, cmd, value):

        build_cmd = array('B', [0x00]*25)

        build_cmd[0] = 0xAA  # Packet start
        build_cmd[1] = 0x00  # Unsupported address location
        build_cmd[2] = cmd & 0xFF  # Command value
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

        self.sp.write(cmd_packet)
        time.sleep(0.250)  # Provide time for response
        resp = self.sp_read(26)

        print(resp)

    def set_remote_control(self, is_remote=True):

        cmd = 0x20
        value = int(is_remote)




    def SetRemoteControl(self):
        "Sets the load to remote control"
        msg = "Set remote control"
        remote = 1
        return self.SendIntegerToLoad(0x20, remote, msg, num_bytes=1)



    def SendIntegerToLoad(self, byte, value, msg, num_bytes=4):
        '''Send the indicated command along with value encoded as an integer
        of the specified size.  Return the instrument's response status.
        '''
        cmd = self.GetCommand(byte, value, num_bytes)
        response = self.SendCommand(cmd)
        #self.PrintCommandAndResponse(cmd, response, msg)
        return self.ResponseStatus(response)


    def GetCommand(self, command, value, num_bytes=4):
        '''Construct the command with an integer value of 0, 1, 2, or
        4 bytes.
        '''
        cmd = self.StartCommand(command)
        if num_bytes > 0:
            r = num_bytes + 3
            cmd += self.CodeInteger(value)[:num_bytes] + self.Reserved(r)
        else:
            cmd += self.Reserved(0)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        return cmd



    def CodeInteger(self, value, num_bytes=4):
        '''Construct a little endian string for the indicated value.  Two
        and 4 byte integers are the only ones allowed.
        '''
        assert(num_bytes == 1 or num_bytes == 2 or num_bytes == 4)
        value = int(value)  # Make sure it's an integer
        s  = chr(value & 0xff)
        if num_bytes >= 2:
            s += chr((value & (0xff << 8)) >> 8)
            if num_bytes == 4:
                s += chr((value & (0xff << 16)) >> 16)
                s += chr((value & (0xff << 24)) >> 24)
                assert(len(s) == 4)
        return s
