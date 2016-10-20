__author__ = 'domenico'


#!/usr/bin/env python

__all__ = ["monotonic_time"]

from ctypes import *
import os

CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>

class timespec(Structure):
    _fields_ = [
        ('tv_sec',  c_long),
        ('tv_nsec', c_long)
    ]

class cell(Structure):
     pass

cell._fields_ = [
        ("name", c_char_p),
        ("next", POINTER(cell))
    ]

librt = CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [c_int, POINTER(timespec)]

def monotonic_time():
    t = timespec()
    if clock_gettime(CLOCK_MONOTONIC_RAW , pointer(t)) != 0:
        errno_ = get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return t.tv_sec + t.tv_nsec * 1e-9

if __name__ == "__main__":
    #print monotonic_time()
    t = timespec()
    c1 = cell()
    #p = create_string_buffer(b"Hello")
    c1.name = b"Hello"
    #c1.name = POINTER()
    print(c1.name)
