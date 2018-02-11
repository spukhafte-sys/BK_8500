
from bk_8500 import bk_8500
import time

bk = bk_8500()


def init_device():
    if bk.get_device_info() is not None:
        bk.set_remote_control(is_remote=True)
        bk.set_mode(bk.MODE_CC)
        bk.set_max_volts(max_volts=16)
        bk.set_max_current(max_current=30)
        bk.set_max_power(max_power=300)

        bk.set_CC_current(cc_current=0)
