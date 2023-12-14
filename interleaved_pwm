from rp2 import PIO, StateMachine, asm_pio
from machine import Pin, mem32, Timer
from utime import sleep_us
import time

machine.freq(160_000_000)

# INSTRUCTIONS
#    ______________________
#___|                      |_ high side 1 always on                            -------------------- vbus
#         _       _       _                                                      |           |
#________| |_____| |_____| |_ high side 2 freewheel signal with dead time       hs1         hs2
#    ___     ___     ___                                                         |-----M-----|
#___|   |___|   |___|   |____ low side 2 drive signal                           ls1         ls2
#                                                                                |           |
#____________________________ low side 1 always off                            -------------------- gnd
#
# This PIO code generates four signals to drive a Full-Bridge with active freewheeling for inductive loads.
# There are three state machines: 1. running clockwise, 2. running counter clockwise, 3. all pins low.
# The state machines incorporate dead time to prevent shot through.
#
# The SM frequency determines the length of a single cycle.
# To vary the deadtime and keeping the PWM frequency, the SM frequency needs to be doubled (half the dead time)
# and the number of the on and off cycles needs to be doubled
#
# To change the duty cycle all cycles taken to shorten the on time needs to be added to the off time to keep the frequency

# Set-up the state machine with four output pins all initially low
@asm_pio(set_init = (PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW))
def clockw():
    # all pins off
    set(pins, 0b00000)
    wrap_target()
    # on time
    set(pins, 0b00101) [18]
    set(pins, 0b00101) [10]		# doubled for doubled SM frequency
    # dead time
    set(pins, 0b00100)			# only one cycle
    # off time
    set(pins, 0b00110) [20]
    set(pins, 0b00110) [28]		# doubled for doubled SM frequency
    # dead time
    set(pins, 0b00100)			# only one cycle
    wrap()
    
@asm_pio(set_init = (PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,))
def cclockw():
    set(pins, 0b00000)
    wrap_target()
    # on time
    set(pins, 0b01010) [18]
    set(pins, 0b01010) [18]
    # dead time
    set(pins, 0b00010)
    # off time
    set(pins, 0b00110) [18]
    set(pins, 0b00110) [18]
    # dead time
    set(pins, 0b00010)
    wrap()

@asm_pio(set_init = (PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW))
def alloff():
    set(pins, 0b00000)
    wrap_target()
    set(pins, 0b00000)
    nop()
    wrap()
    
# 1/800kHz=1,25µs (SM Clock)
# 1/20kHz =50µs	  (PWM Clock)
# 50µs/1,25µs=40 Cycles
# double the SM frequency to decrease the dead time. -> double the on time of the steps
cw = StateMachine(0, clockw,   freq = 1_600_000, set_base = Pin(19))
ccw = StateMachine(1, cclockw, freq = 1_600_000, set_base = Pin(19))
off = StateMachine(2, alloff,  freq = 1_600_000, set_base = Pin(19))

cw.active(0)
ccw.active(0)
off.active(1)

actual_time = 0
last_time = 0
refresh_rate = 10
hb_state = 0

while (True):
    #cw.active(1)
    actual_time = time.ticks_ms()
    
    # all <refresh_rate> milli seconds the state machine swaps
    if actual_time - last_time > refresh_rate:
        last_time = actual_time
        if hb_state == 0:
            # enable and restart cw turn off ccw
            off.active(0)
            cw.active(1)
            hb_state = 1 # is cw on
        else:
            # enable and restart ccw and disable cw
            cw.active(0)
            off.active(1)

            hb_state = 0
            

            

