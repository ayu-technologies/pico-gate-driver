import time
import rp2
from machine import ADC,Pin


# Define  the blink program.  It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blinking visible by eye.
@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW), autopull=True, pull_thresh=32)
def blink():
    label("get_y")
    pull()
    out(y,32)
    label("start")
    jmp(not_osre,"get_y")
    mov(x,y)
    set(pins, 2)
    label("delay_high")
    jmp(x_dec, "delay_high")
    
    set(pins, 0)   [30]
    
    mov(x,y)
    set(pins, 1)
    label("delay_low")
    jmp(x_dec, "delay_low")
    set(pins, 0)   [30]
    jmp("start")

# GPIOピンの設定
pwm_pin = Pin(14, Pin.OUT)
pwm_pin1 = Pin(15, Pin.OUT)
machine.freq(270_000_000)
# Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the Pico board)
sm = rp2.StateMachine(0, blink, freq=270_000_000, set_base=pwm_pin)
# Run the state machine for 3 seconds.  The LED should blink.
sm.active(1)
sm.put(200)

Pin(26,Pin.IN)
a = ADC(0)
coeff = 3.3/65535

trim_max = 40_000
trim_min = 140_000


while True:
    voltage_sum = 0
    for i in range(10):
        voltage_sum += a.read_u16() * coeff
    voltage = voltage_sum/10
    print(voltage)
        # Scale the voltage to the PWM range
    F = int((voltage / 3.3) * (trim_min - trim_max) + trim_max)

    # Ensure the pwm_value is within the bounds
    F = max(min(F, trim_min), trim_max)
    
    #N=19+2*on_time+2*3
    #F=(1/(3.7*N))*1_000_000_000
    print(str(F/1000)+"kHz")
    
    N = (1/F)*(1/3.7)*1_000_000_000
    pwm_value = int((N-(12+60))/2)#60 はdeattime が30 30 だから
    
    
    print(pwm_value)
    # Send the value to the state machine
    sm.put(pwm_value)
    time.sleep(0.1)
