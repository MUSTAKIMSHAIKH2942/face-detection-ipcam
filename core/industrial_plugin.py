# core/industrial_plugin.py
from abc import ABC, abstractmethod
import time
from enum import Enum

class PluginCriticality(Enum):
    SAFETY = 1
    QUALITY = 2
    PRODUCTION = 3
    MONITORING = 4

class IndustrialPlugin(ABC):
    def __init__(self):
        self.criticality = None
        self.required_resources = []
        self.timeout = 5.0  # seconds
        self.last_heartbeat = time.time()
        
    @abstractmethod
    def initialize(self, config):
        """Initialize with industrial config"""
        pass
        
    @abstractmethod
    def process(self, frame):
        """Process frame with industrial requirements"""
        pass
        
    def validate_environment(self):
        """Check required resources are available"""
        for resource in self.required_resources:
            if not self._check_resource(resource):
                return False
        return True
        
    def send_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = time.time()
        
    def check_health(self):
        """Check if plugin is healthy"""
        return (time.time() - self.last_heartbeat) < self.timeout
        
    def emergency_stop(self):
        """Trigger emergency actions if needed"""
        pass