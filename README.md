# BK_8500
BK Precision 8500 interface library

## Command Packet
| Byte 0 | Byte 1 | Byte 2 | Byte 3 to 24 | Byte 25 |
| 0xAA | Address | Command | Data | CRC |

If a CMD packet responds without a 0x12 status, usually when data is being returned, the command ID should be in the Byte3 positions.

## Status Packet
| Byte 0 | Byte 1 | Byte 2 | Byte 3 | Byte 4 to 24 | Byte 25 |
| 0xAA | Address | 0x12 | Status |Reserved | CRC |

''' Python
self.resp_status_dict = {
    0x90: "ERROR: Invalid checksum",
    0xA0: "ERROR: Invalid value",
    0xB0: "ERROR: Unable to execute",
    0xC0: "ERROR: invalid command",
    0x80: True,
}
'''
