import cv2
import threading
import time
import platform
import json
from pathlib import Path
from core.crash_logger import log_exception


def auto_backend(source):
    if platform.system() == "Windows":
        return cv2.CAP_MSMF
    elif platform.system() == "Linux":
        return cv2.CAP_V4L2
    return cv2.CAP_ANY


def find_working_webcams(max_index=5):
    working = []
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"[AutoDetect] ✅ Found working webcam at index {idx}")
                working.append(idx)
            else:
                print(f"[AutoDetect] ❌ No frame from index {idx}")
            cap.release()
        else:
            print(f"[AutoDetect] ❌ Camera at index {idx} not opened")
    return working


def load_ip_cameras_from_config(config_path="config/default_settings.json"):
    if not Path(config_path).exists():
        print(f"[Config] ❌ Camera config not found at {config_path}")
        return []
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("camera_sources", [])
    except Exception as e:
        print(f"[Config] ❌ Failed to load camera_sources list: {e}")
        return []


class CameraStream:
    def __init__(self, source_id, source_type, source_value):
        self.source_id = source_id
        self.source_type = source_type

        if isinstance(source_value, str) and source_value.isdigit():
            self.source_value = int(source_value)
        else:
            self.source_value = source_value

        self.capture = None
        self.running = False
        self.frame = None
        self.thread = None

    def start(self):
        if self.running:
            print(f"[Camera {self.source_id}] Already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

    def update_frames(self):
        # Use FFMPEG for IP/NVR streams, DSHOW for USB, fallback to CAP_ANY
        if self.source_type == "ip":
            backend = cv2.CAP_FFMPEG
        elif self.source_type == "usb":
            backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_V4L2
        else:
            backend = cv2.CAP_ANY

        print(f"[Camera {self.source_id}] Attempting backend: {backend}")

        self.capture = cv2.VideoCapture(self.source_value, backend)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.capture.isOpened():
            print(f"[Camera {self.source_id}] ❌ Initial backend failed. Trying CAP_ANY...")
            self.capture = cv2.VideoCapture(self.source_value, cv2.CAP_ANY)

        if not self.capture.isOpened():
            print(f"[Camera {self.source_id}] ❌ Failed to open video stream for {self.source_id}")
            self.running = False
            return

        print(f"[Camera {self.source_id}] ✅ Successfully opened using backend: {backend}")

        frame_attempts = 0
        first_frame_logged = False

        while self.running:
            try:
                ret, frame = self.capture.read()
                if ret and frame is not None:
                    self.frame = frame
                    frame_attempts = 0
                    if not first_frame_logged:
                        print(f"[Camera {self.source_id}] ✅ First frame captured.")
                        first_frame_logged = True
                else:
                    frame_attempts += 1
                    if frame_attempts == 10:
                        print(f"[Camera {self.source_id}] ⚠️ Retried 10 times. Still no frame.")
                    elif frame_attempts >= 50:
                        log_exception(
                            context="Camera stopped after 50 failed frame reads",
                            extra_info={"camera_id": self.source_id, "type": self.source_type, "source": self.source_value}
                        )
                        break
                    time.sleep(0.1)
            except Exception as e:
                log_exception(
                    e,
                    context="Exception during camera read loop",
                    extra_info={"camera_id": self.source_id}
                )
                break

        if self.capture:
            self.capture.release()
        print(f"[Camera {self.source_id}] Capture thread stopped.")

    def stop(self):
        self.running = False
        if self.thread:
            try:
                self.thread.join(timeout=3)
            except RuntimeError:
                print(f"[Camera {self.source_id}] ⚠️ Could not join thread cleanly.")

    def get_frame(self):
        return self.frame


class CameraManager:
    def __init__(self):
        self.cameras = {}

    def auto_initialize_all_cameras(self, webcam_max=4):
        print("[CameraManager] 🔍 Auto-initialising all cameras...")

        ip_cameras = load_ip_cameras_from_config()
        for i, url in enumerate(ip_cameras):
            self.add_camera(f"ip_{i}", "ip", url)

        usb_indexes = find_working_webcams(webcam_max)
        for i, idx in enumerate(usb_indexes):
            self.add_camera(f"usb_{i}", "usb", idx)

        if not self.cameras:
            print("[CameraManager] ⚠️ No cameras successfully initialized.")

        print(f"[CameraManager] ✅ Total cameras initialized: {len(self.cameras)}")
        for cam_id in self.cameras:
            print(f" - Camera ID: {cam_id}")

    def add_camera(self, source_id, source_type, source_value):
        if source_id in self.cameras:
            print(f"[CameraManager] Camera {source_id} already exists.")
            return
        cam = CameraStream(source_id, source_type, source_value)
        self.cameras[source_id] = cam
        cam.start()

    def remove_camera(self, source_id):
        if source_id in self.cameras:
            self.cameras[source_id].stop()
            del self.cameras[source_id]
            print(f"[CameraManager] Camera {source_id} removed.")

    def get_frame(self, source):
        if isinstance(source, int):
            cam_keys = list(self.cameras.keys())
            if source < len(cam_keys):
                return self.cameras[cam_keys[source]].get_frame()
        elif isinstance(source, str) and source in self.cameras:
            return self.cameras[source].get_frame()
        return None

    def start_all_cameras(self):
        for cam in self.cameras.values():
            cam.start()

    def stop_all_cameras(self):
        for cam in self.cameras.values():
            cam.stop()
        print("[CameraManager] All cameras stopped.")
