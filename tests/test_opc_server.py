# tests/test_opc_server.py

"""
Test Suite for OPCUAServer — Validates OPC UA variable communication.

Author: ItsOji Team
"""

import time
import sys
import os

sys.path.append(os.path.abspath("."))

from industrial.opc_server import OPCUAServer

def test_opc_variables(server):
    print("[TEST] 🧪 Verifying OPC UA variable states...")

    test_cases = {
        "HelmetDetected": True,
        "FireDetected": False,
        "FaceRecognized": True,
        "IntrusionDetected": False,
    }

    for var_name, expected in test_cases.items():
        server.set_variable(var_name, expected)
        actual = server.variables[var_name].get_value()
        assert actual == expected, f"[ERROR] {var_name} mismatch: expected {expected}, got {actual}"
        print(f"[PASS] {var_name}: {actual}")

    print("[TEST] ✅ All OPC UA variables set and verified successfully.")



if __name__ == "__main__":
    print("[TEST SUITE] 🚀 Starting OPC UA Server for test...\n")

    opc_server = OPCUAServer()
    opc_server.run_in_thread()  # non-blocking background server

    time.sleep(2)  # Wait for server to be ready

    try:
        test_opc_variables(opc_server)
        print("\n[TEST SUITE] ✅ OPC UA Server test completed successfully.")
    except Exception as e:
        print(f"[TEST SUITE] ❌ Test failed with exception: {e}")
    finally:
        opc_server.stop()
        print("[TEST SUITE] 🛑 OPC UA Server stopped.")

