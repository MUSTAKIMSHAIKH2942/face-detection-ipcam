# industrial/modbus_client.py - Final Updated

from pymodbus.client import ModbusTcpClient
import threading
import time

class ModbusClientHandler:
    """Handles Modbus TCP Client operations with background read/write threading."""

    def __init__(self, server_ip="127.0.0.1", port=502):
        self.server_ip = server_ip
        self.port = port
        self.client = ModbusTcpClient(self.server_ip, port=self.port)
        self.connected = False
        self.running = False
        self.thread = None

    def ensure_connection(self):
        """Reconnect if connection is lost or socket is closed."""
        if not self.connected or not self.client.is_socket_open():
            print("[ModbusClient] ⚠ Connection lost. Reconnecting...")
            self.connect()

    def connect(self):
        self.connected = self.client.connect()
        if self.connected:
            print(f"[ModbusClient] ✅ Connected to {self.server_ip}:{self.port}")
        else:
            print(f"[ModbusClient] ❌ Failed to connect to {self.server_ip}:{self.port}")

    def disconnect(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.client.close()
        self.connected = False
        print(f"[ModbusClient] 🔌 Disconnected from {self.server_ip}:{self.port}")

    def write_coil(self, address, value):
        self.ensure_connection()
        if self.connected:
            self.client.write_coil(address=address, value=value)
        else:
            print("[ModbusClient] ⚠ Not connected. Cannot write coil.")

    def write_register(self, address, value):
        self.ensure_connection()
        if self.connected:
            self.client.write_register(address=address, value=value)
        else:
            print("[ModbusClient] ⚠ Not connected. Cannot write register.")

    def read_coil(self, address):
        self.ensure_connection()
        if not self.connected:
            print("[ModbusClient] ⚠ Not connected.")
            return None
        result = self.client.read_coils(address=address, count=1)
        if result.isError():
            print("[ModbusClient] ❌ Error reading coil!")
            return None
        value = result.bits[0]
        print(f"[ModbusClient] 🧪 Coil[{address}] = {value}")
        return value

    def read_register(self, address):
        self.ensure_connection()
        if not self.connected:
            print("[ModbusClient] ⚠ Not connected.")
            return None
        result = self.client.read_holding_registers(address=address, count=1)
        if result.isError():
            print("[ModbusClient] ❌ Error reading register!")
            return None
        value = result.registers[0]
        print(f"[ModbusClient] 🧪 Register[{address}] = {value}")
        return value

    def run_in_thread(self):
        if not self.connected:
            self.connect()
        self.running = True
        self.thread = threading.Thread(target=self._simulate_loop)
        self.thread.start()

    def _simulate_loop(self):
        while self.running:
            try:
                self.write_coil(0, True)
                time.sleep(1)
                self.read_coil(0)
                self.write_register(1, 1234)
                time.sleep(1)
                self.read_register(1)
            except Exception as e:
                print(f"[ModbusClient] ⚠ Exception in loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    client = ModbusClientHandler()
    client.run_in_thread()
    time.sleep(10)
    client.disconnect()
