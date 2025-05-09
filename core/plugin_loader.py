"""
Plugin Loader - Dynamically loads AI plugins from /plugins/ folder.

Author: ItsOji Team
"""

import importlib
import os
import sys
from pathlib import Path
from plugins.base_plugin import BasePlugin
from core.crash_logger import log_exception
from datetime import datetime

class PluginManager:
    """Manages and applies all AI plugins."""

    def __init__(self, plugin_folder="plugins"):
        self.plugin_folder = plugin_folder
        self.plugins = self.load_plugins(plugin_folder)

    def load_plugins(self, plugin_folder):
        plugins = {}
        plugin_path = Path(plugin_folder)

        if not plugin_path.exists():
            print(f"[PluginLoader] Folder not found: {plugin_folder}")
            return plugins

        sys.path.append(str(plugin_path.parent))  # Ensure parent folder is importable

        for file in plugin_path.glob("*.py"):
            if file.name in ("__init__.py", "base_plugin.py") or file.name.startswith("_"):
                continue

            module_name = file.stem
            try:
                module = importlib.import_module(f"plugins.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                        plugins[module_name] = attr()
                        print(f"[PluginManager] ✅ Loaded plugin: {module_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"[PluginManager] ❌ Error loading {module_name}: {e}")
                log_exception(e, context=f"PluginLoader → {module_name}")

        return plugins

    def apply_plugins(self, frame, camera_id=None):
        """Run all loaded plugins on the frame and return their results."""
        results = {}
        for name, plugin in self.plugins.items():
            try:
                result = plugin.run(frame, camera_id=camera_id)
                results[name] = result
                print(f"[PluginManager] Applied {name} on Cam {camera_id} at {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"[PluginManager] ❌ Error in plugin {name}: {e}")
                log_exception(e, context=f"PluginManager → {name}")
        return results

    def refresh_plugins(self):
        """Reloads all plugins at runtime."""
        print("[PluginManager] 🔄 Refreshing plugins...")
        self.plugins = self.load_plugins(self.plugin_folder)
        print("[PluginManager] ✅ Plugin refresh complete.")

    def list_plugins(self):
        """Return a list of loaded plugin names."""
        return list(self.plugins.keys())

    def get_plugin(self, name):
        """Return a specific plugin instance by name."""
        return self.plugins.get(name)
