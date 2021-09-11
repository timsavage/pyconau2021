import machine
from time import ticks_add, ticks_diff, ticks_ms, ticks_us
import _thread

import animation


#
# Display shift-register interface
#
class Display:
    def __init__(self, led_count=32, offset=2, data_pin=7, clk_pin=6, latch_pin=8):
        self.led_count = led_count
        self.offset = offset
        self.data = machine.Pin(data_pin, machine.Pin.OUT)
        self.clock = machine.Pin(clk_pin, machine.Pin.OUT)
        self.latch = machine.Pin(latch_pin, machine.Pin.OUT)

    def shift_out(self, value):
        for _ in range(self.led_count):
            self.clock.on()
            self.data.on() if value & 1 else self.data.off()
            value >>= 1
            self.clock.off()

    def set(self, value):
        self.latch.off()
        self.shift_out(value << self.offset)
        self.latch.on()


DELAY = 1000
PHASES = 4
MAP = [
    4, 4, 4,
    4, 4, 4, 4,  # Green
    15, 15, 15, 15,  # Yellow
    15, 15, 15, 15,  # Orange
    10, 10, 10, 10,  # Red
    15, 15, 15, 15,  # Blue
    4, 4, 4, 4,  # Green
]
output_buffer = [0] * 28


#
# Calculate BAM values
#
def bam(led_states, phase):
    output = 0
    for led_state in led_states:
        output <<= 1
        output |= (led_state >> phase) & 1
    return output


#
# Thread that runs on second core to generate output
#
def output_thread():
    display = Display()
    phase = 0
    delay = DELAY
    deadline = 0
    output = 0

    while True:
        now = ticks_us()
        if ticks_diff(now, deadline) > 0:
            display.set(bam(output_buffer, phase))

            # Calculate next
            delay <<= 1
            phase += 1
            if phase == PHASES:
                phase = 0
                delay = DELAY

            # Generate next deadline
            deadline = ticks_add(now, delay)


#
# Helper run loop that takes a object with a loop
#
def run(*anis, delay=100, ani_delay=5000):
    state = [False] * 27
    deadline = 0
    ani_idx = 0
    ani_timeout = ticks_add(ticks_ms(), ani_delay)

    while True:
        ani = anis[ani_idx]

        while ticks_diff(ticks_ms(), ani_timeout):
            now = ticks_ms()
            if ticks_diff(now, deadline) > 0:
                # Update output buffer
                for idx in range(len(state)):
                    output_buffer[idx] = MAP[idx] if state[idx] else 0

                # Generate next state and deadline
                ani(state)
                deadline = ticks_add(now, delay)

        ani_idx = (ani_idx + 1) % len(anis)
        ani_timeout = ticks_add(ticks_ms(), ani_delay)


#
# Clear display
#
def clear():
    for idx in range(len(output_buffer)):
        output_buffer[idx] = 0


b = animation.Bounce()
s = animation.Snake()
c = animation.Chaser()

_thread.start_new_thread(output_thread, ())
