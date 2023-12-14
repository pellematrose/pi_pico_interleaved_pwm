# pi_pico_interleaved_pwm
Driving a Full-Bridge with active freewheeling using the asm_pio module

 ## INSTRUCTIONS
```python
    ______________________
___|                      |_ high side 1 always on                            -------------------- vbus
         _       _       _                                                      |           |
________| |_____| |_____| |_ high side 2 freewheel signal with dead time       hs1         hs2
    ___     ___     ___                                                         |-----M-----|
___|   |___|   |___|   |____ low side 2 drive signal                           ls1         ls2
                                                                                |           |
____________________________ low side 1 always off                            -------------------- gnd
```
 This PIO code generates four signals to drive a Full-Bridge with active freewheeling for inductive loads.
 There are three state machines: 1. running clockwise, 2. running counter clockwise, 3. all pins low.
 The state machines incorporate dead time to prevent shot through.

 The SM frequency determines the length of a single cycle.
 To vary the deadtime and keeping the PWM frequency, the SM frequency needs to be doubled (half the dead time)
 and the number of the on and off cycles needs to be doubled

 To change the duty cycle all cycles taken to shorten the on time needs to be added to the off time to keep the frequency
