"""
Base Plugin Class - Defines the standard interface for all AI plugins.

Author: ItsOji Team
"""

class BasePlugin:
    """Abstract base class for all AI plugins."""

    def __init__(self):
        """Initialise the plugin."""
        pass

    def load_model(self):
        """
        Load the AI model required for detection.
        Must be implemented by the plugin.
        """
        raise NotImplementedError("Plugins must implement load_model() method.")

    def process(self, frame):
        """
        Process a video frame and return detection results.
        
        :param frame: Input video frame (OpenCV BGR format)
        :return: Detection results (dict or list depending on plugin)
        """
        raise NotImplementedError("Plugins must implement process() method.")

    def release(self):
        """
        Release any resources (e.g., model, session) when the plugin is unloaded.
        """
        pass  # Optional to implement
