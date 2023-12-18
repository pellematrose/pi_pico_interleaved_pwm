from rp2 import PIO, StateMachine, asm_pio
from machine import Pin, mem32, Timer
from utime import sleep_us
import time

machine.freq(200_000_000)

#TODO:
# - implement defined start of sm
# - implement defined turn off of sm
# - alloff sm does not work properly. first instructions could not be seen.
# - before calling alloff set the PC to the beginning before the wrap_target()

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
    ON = 19
    OFF = 19
    DEAD = 0
    # all pins off
    #set(pins, 0b00000)            # this line will only be executed once. The program counter can not be reset to this position.
    wrap_target()
    # on time
    set(pins, 0b00101) [ON]
    set(pins, 0b00101) [ON - 1]		# doubled for doubled SM frequency
    # dead time
    set(pins, 0b00100) [DEAD]		# only one cycle
    # off time
    set(pins, 0b00110) [OFF]
    set(pins, 0b00110) [OFF - 1]	# doubled for doubled SM frequency
    # dead time
    set(pins, 0b00100) [DEAD]		# only one cycle
    wrap()
    
@asm_pio(set_init = (PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,))
def cclockw():
    ON = 19
    OFF = 19
    DEAD = 0
    #set(pins, 0b00000)
    wrap_target()
    # on time
    set(pins, 0b01010) [ON]
    set(pins, 0b01010) [ON - 1]
    # dead time
    set(pins, 0b00010) [DEAD]
    # off time
    set(pins, 0b00110) [OFF]
    set(pins, 0b00110) [OFF - 1]
    # dead time
    set(pins, 0b00010) [DEAD]
    wrap()

@asm_pio(set_init = (PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW))
def alloff():
    set(pins, 0b00000) # these lines are not executed... why? not properly restarted?

    
# 1/800kHz=1,25µs (SM Clock)
# 1/20kHz =50µs	  (PWM Clock)
# 50µs/1,25µs=40 Cycles
# double the SM frequency to decrease the dead time. -> double the on time of the steps
cw = StateMachine(0, clockw,   freq = 1_600_000, set_base = Pin(19))
ccw = StateMachine(1, cclockw, freq = 1_600_000, set_base = Pin(19))
off = StateMachine(2, alloff,  freq = 1_600_000, set_base = Pin(19))

# enable SM2 [PIO0 Base addr. + CTRL reg]
machine.mem32[0x50200000 + 0x000] =  0b000000000100

actual_time = 0
last_time = 0
refresh_rate = 10
hb_state = 0

cw_only =  0b000000000001
ccw_only = 0b000000000010
off_only = 0b000000000100

while (True):
    
    user_input = input("Enter the case number (1: CW, 2: CCW, or 3: Off): ")
    
    if user_input == '1':
        machine.mem32[0x50200000 + 0x000] = cw_only # enable cw_only
        print("Running CW")
    elif user_input == '2':
        machine.mem32[0x50200000 + 0x000] = ccw_only # enable ccw_only
        print("Running CCW")
    elif user_input == '3':
        machine.mem32[0x50200000 + 0x000] = off_only # enable off_only
        print("Turning OFF")
    else:
        print("Invalid Input")
