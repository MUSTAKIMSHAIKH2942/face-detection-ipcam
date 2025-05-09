import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config_validator import validate_config_file

try:
    validate_config_file("config/default_settings.json")
except Exception as e:
    print(e)
