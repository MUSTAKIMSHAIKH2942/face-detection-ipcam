# core/io_manager.py

"""
IO Manager - Simulates Digital and Analog IO handling.
Future expansion: integrate with real Modbus/TCP hardware.
"""

import time
import random

class IOManager:
    def __init__(self):
        self.digital_outputs = {}
        self.analog_outputs = {}
        self.digital_inputs = {}
        self.analog_inputs = {}

    def set_digital_output(self, channel, value):
        self.digital_outputs[channel] = value
        print(f"[IOManager] (Dummy) Setting Modbus Coil at {channel} to {value}")

    def get_digital_input(self, channel):
        value = self.digital_inputs.get(channel, random.choice([True, False]))
        print(f"[IOManager] (Dummy) Reading DI at {channel}: {value}")
        return value

    def set_analog_output(self, channel, value):
        self.analog_outputs[channel] = value
        print(f"[IOManager] (Dummy) Writing Analog Output at {channel} = {value}")

    def get_analog_input(self, channel):
        value = self.analog_inputs.get(channel, round(random.uniform(0, 10), 2))
        print(f"[IOManager] (Dummy) Reading Analog Input at {channel}: {value}V")
        return value

    def simulate_input_update(self):
        # Future: sync from actual field sensors
        self.digital_inputs = {ch: random.choice([True, False]) for ch in range(8)}
        self.analog_inputs = {ch: round(random.uniform(0, 10), 2) for ch in range(4)}
