# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
from machine import PWM, Pin, Timer
import time
import network

# Killing pins on init
#for x in [0, 2, 4, 5, 12, 13, 14, 15]:  
#  PWM(Pin(x)).duty(0)
 
rPin= PWM(Pin(14), freq=952, duty=1024) 
gPin=PWM(Pin(2), freq=952, duty=1024)
bPin=PWM(Pin(0), freq=952, duty=1024)
wwPin=PWM(Pin(12), freq=952, duty=1024)
cwPin=PWM(Pin(13), freq=952, duty=1024)

import gc

#import webrepl

#webrepl.start()

gc.collect()