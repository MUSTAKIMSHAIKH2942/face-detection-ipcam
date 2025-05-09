# core/config_validator.py

import json
import os

def validate_config_file(config_path="config/default_settings.json", required_keys=None):
    """
    Validate a config JSON file against required keys and types.

    :param config_path: Path to the config file.
    :param required_keys: Dictionary of keys and expected types.
    :raises FileNotFoundError: If file doesn't exist.
    :raises ValueError: If keys are missing or types don't match.
    :return: True if config is valid.
    """
    default_required = {
        "camera_sources": list,
        "plugin_folder": str,
        "backup_folder": str,
        "report_format": str,
        "server_ip": str
    }

    if required_keys is None:
        required_keys = default_required

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"[VALIDATOR] ❌ Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"[VALIDATOR] ❌ Invalid JSON format: {e}")

    missing = []
    wrong_type = []

    for key, expected_type in required_keys.items():
        if key not in config:
            missing.append(key)
        elif not isinstance(config[key], expected_type):
            wrong_type.append((key, type(config[key]).__name__, expected_type.__name__))

    if missing or wrong_type:
        error_msg = "[VALIDATOR] ❌ Config validation failed:\n"
        if missing:
            error_msg += f" - Missing keys: {missing}\n"
        if wrong_type:
            error_msg += " - Wrong types:\n"
            for key, got, expected in wrong_type:
                error_msg += f"   → '{key}': got {got}, expected {expected}\n"
        raise ValueError(error_msg.strip())

    print(f"[VALIDATOR] ✅ Config file '{config_path}' is valid.")
    return True