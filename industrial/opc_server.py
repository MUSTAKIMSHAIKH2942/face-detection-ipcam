# industrial/opc_server.py

"""
OPCUAServer — Enhanced OPC UA Server with support for:
- Industrial variable setup (SystemMonitoring, Production)
- Plugin-to-OPC mapping
- Background thread execution for testing

Author: ItsOji Team
"""

from opcua import Server
from opcua.ua import VariantType
import threading
import time
from queue import Queue

class OPCUAServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4850/eyeq/server/"):
        self.server = Server()
        self.endpoint = endpoint
        self.running = False
        self.event_queue = Queue()
        self.namespace_uri = "http://eyeq.enterprise"
        self.idx = None
        self.objects = None
        self.variables = {}  # OPC variable storage

    def setup(self):
        """Set up OPC UA server with EyeQ nodes."""
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name("EyeQ Enterprise OPC-UA Server")
        self.idx = self.server.register_namespace(self.namespace_uri)

        self.objects = self.server.nodes.objects

        # System monitoring branch
        system_monitoring = self.objects.add_object(self.idx, "SystemMonitoring")
        self.variables["CPUUsage"] = system_monitoring.add_variable(self.idx, "CPUUsage", 0.0)
        self.variables["MemoryUsage"] = system_monitoring.add_variable(self.idx, "MemoryUsage", 0.0)

        # Production monitoring branch
        production = self.objects.add_object(self.idx, "Production")
        self.variables["UnitsPerHour"] = production.add_variable(self.idx, "UnitsPerHour", 0)
        self.variables["DefectRate"] = production.add_variable(self.idx, "DefectRate", 0.0)

        # AI Plugin Detection Nodes
        plugin_obj = self.objects.add_object(self.idx, "PluginDetections")
        self.variables["HelmetDetected"] = plugin_obj.add_variable(self.idx, "HelmetDetected", False)
        self.variables["FireDetected"] = plugin_obj.add_variable(self.idx, "FireDetected", False)
        self.variables["FaceRecognized"] = plugin_obj.add_variable(self.idx, "FaceRecognized", False)
        self.variables["IntrusionDetected"] = plugin_obj.add_variable(self.idx, "IntrusionDetected", False)

        # Make all writable
        for var in self.variables.values():
            var.set_writable()

    def set_variable(self, name, value):
        if name in self.variables:
            self.variables[name].set_value(value)
        else:
            print(f"[OPC UA] ⚠️ Variable '{name}' not found.")

    def start(self):
        try:
            self.setup()
            self.server.start()
            print(f"[OPC UA] ✅ Server running at {self.endpoint}")
        except Exception as e:
            print(f"[OPC UA] ❌ Server failed to start: {str(e)}")
            raise

    def stop(self):
        try:
            self.running = False
            self.server.stop()
            print("[OPC UA] 🛑 Server stopped.")
        except Exception as e:
            print(f"[OPC UA] ❌ Error stopping server: {e}")

    def run_in_thread(self):
        def _run():
            self.start()
            while self.running:
                time.sleep(1)
        self.running = True
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        print("[OPC UA] 🧵 Background thread started.")
