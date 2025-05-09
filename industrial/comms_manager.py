# industrial/comms_manager.py
from industrial.opc_server import OPCUAServer
from industrial.modbus_client import ModbusClientHandler
from queue import Queue

class IndustrialCommsManager:
    def __init__(self):
        self.opc_server = OPCUAServer()
        self.modbus_clients = {}
        self.active_protocol = 'opc'  # Default protocol
        self.fallback_protocol = 'modbus'
        self.message_queue = Queue()
        
    def add_modbus_client(self, name, ip, port=502):
        self.modbus_clients[name] = ModbusClientHandler(ip, port)
        
    def start_all(self):
        # Start OPC-UA server in thread
        self.opc_server.run_in_thread()
        
        # Connect all Modbus clients
        for name, client in self.modbus_clients.items():
            try:
                client.connect()
            except Exception as e:
                print(f"[Comms] Failed to connect Modbus client {name}: {str(e)}")
                
    def send_command(self, command, data):
        """Send command via active protocol with fallback"""
        try:
            if self.active_protocol == 'opc':
                self.opc_server.set_variable(command, data)
            elif self.active_protocol == 'modbus':
                # Map command to Modbus registers/coils
                self._send_modbus_command(command, data)
        except Exception as e:
            print(f"[Comms] Primary protocol failed, switching to fallback")
            self._use_fallback_protocol(command, data)
            
    def _use_fallback_protocol(self, command, data):
        """Switch to fallback communication protocol"""
        try:
            if self.fallback_protocol == 'modbus':
                self._send_modbus_command(command, data)
        except Exception as e:
            print(f"[Comms] Fallback protocol also failed: {str(e)}")
            self.message_queue.put(('error', str(e)))