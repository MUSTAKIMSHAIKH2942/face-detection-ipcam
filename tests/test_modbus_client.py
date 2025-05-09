import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from industrial.modbus_client import ModbusClientHandler


def main():
    modbus_client = ModbusClientHandler(server_ip="127.0.0.1", port=502)
    modbus_client.run_example()

if __name__ == "__main__":
    main()
