import unittest
from core.io_manager import IOManager

class TestIOManager(unittest.TestCase):
    def test_digital_output(self):
        io = IOManager()
        io.set_digital_output(1, True)
        self.assertTrue(io.digital_outputs[1])

    def test_digital_input(self):
        io = IOManager()
        io.digital_inputs[2] = True  # simulate input
        self.assertTrue(io.get_digital_input(2))

if __name__ == "__main__":
    unittest.main()
