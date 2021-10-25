# This file is executed on every boot (including wake-boot from deepsleep)

from machine import Pin, PWM

PWM(Pin(17), freq=78125, duty=0)
PWM(Pin(16), freq=78125, duty=0)
PWM(Pin(22), freq=78125, duty=0)
PWM(Pin(21), freq=78125, duty=0)

import esp

esp.osdebug(None)

# Making network and sys a global
import network
import sys

# Cleaning Memory
import gc

gc.collect()
