# BK_8500
BK Precision 8500 interface library

## Command Packet

|Byte0|Byte1|Byte2|Byte3-24|Byte25|
|---|---|---|---|---|
|0xAA|Address|Command|Data|CRC|


If a CMD packet responds without a 0x12 status, usually when data is being returned, the command ID should be in the Byte3 positions.

## Status Packet

|Byte0|Byte1|Byte2|Byte3|Byte4-24|Byte25|
|---|---|---|---|---|---|
|0xAA|Address|0x12|Status|Reserved|CRC|


''' Python
self.resp_status_dict = {
    0x90: "ERROR: Invalid checksum",
    0xA0: "ERROR: Invalid value",
    0xB0: "ERROR: Unable to execute",
    0xC0: "ERROR: invalid command",
    0x80: True,
}
'''



## Op state
Bit
Meaning
0
Calculate the new demarcation coefficient
1
Waiting for a trigger signal
2
Remote control state (1 means enabled)
3
Output state (1 means ON)
4
Local key state (0 means not enabled, 1 means enabled)
5
Remote sensing mode (1 means enabled)
6
LOAD ON timer is enabled
7
Reserved


## Demand state
Bit
Meaning
0
Reversed voltage is at instrument's terminals (1 means yes)
1
Over voltage (1 means yes)
2
Over current (1 means yes)
3
Over power (1 means yes)
4
Over temperature (1 means yes)
5
Not connect remote terminal
6
Constant current
7
Constant voltage
8
Constant power
9
Constant resistance
