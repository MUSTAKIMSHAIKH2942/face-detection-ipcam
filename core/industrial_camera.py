# core/industrial_camera.py
import cv2
import threading
import time
from enum import Enum

class CameraStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    STREAMING = 2
    FAULT = 3

class IndustrialCamera:
    def __init__(self, source_id, source_type, source_value):
        self.source_id = source_id
        self.source_type = source_type
        self.source_value = source_value
        self.capture = None
        self.status = CameraStatus.DISCONNECTED
        self.frame_count = 0
        self.error_count = 0
        self.max_retries = 5
        self.retry_delay = 2.0  # seconds
        self.last_frame_time = 0
        self.frame_rate = 0
        self.lock = threading.Lock()
        
    def connect(self):
        """Enhanced connection with status tracking"""
        if self.status not in [CameraStatus.DISCONNECTED, CameraStatus.FAULT]:
            return
            
        for attempt in range(self.max_retries):
            try:
                backend = self._determine_backend()
                self.capture = cv2.VideoCapture(self.source_value, backend)
                
                if self.capture.isOpened():
                    self.status = CameraStatus.CONNECTED
                    print(f"[Camera {self.source_id}] Connected successfully")
                    return True
                    
            except Exception as e:
                print(f"[Camera {self.source_id}] Connection attempt {attempt+1} failed: {str(e)}")
                time.sleep(self.retry_delay)
                
        self.status = CameraStatus.FAULT
        print(f"[Camera {self.source_id}] Failed to connect after {self.max_retries} attempts")
        return False
        
    def start_streaming(self):
        """Start frame acquisition thread"""
        if self.status != CameraStatus.CONNECTED:
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._update_frames, daemon=True)
        self.thread.start()
        self.status = CameraStatus.STREAMING
        return True
        
    def _update_frames(self):
        """Thread-safe frame acquisition with metrics"""
        while self.running:
            try:
                ret, frame = self.capture.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                        now = time.time()
                        if self.last_frame_time > 0:
                            self.frame_rate = 1.0 / (now - self.last_frame_time)
                        self.last_frame_time = now
                        self.frame_count += 1
                else:
                    self.error_count += 1
                    if self.error_count > 10:
                        self.status = CameraStatus.FAULT
                        break
            except Exception as e:
                print(f"[Camera {self.source_id}] Frame acquisition error: {str(e)}")
                self.error_count += 1
                
    def get_frame(self):
        """Get latest frame with thread safety"""
        with self.lock:
            return self.frame if hasattr(self, 'frame') else None
            
    def get_status(self):
        """Return comprehensive status dictionary"""
        return {
            'status': self.status.name,
            'frame_rate': self.frame_rate,
            'frame_count': self.frame_count,
            'error_count': self.error_count,
            'source': f"{self.source_type}:{self.source_value}"
        }