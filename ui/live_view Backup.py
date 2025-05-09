import queue
import cv2
import time
import json
import os
import numpy as np
from queue import Queue
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel, QVBoxLayout,
    QPushButton, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QMetaObject
from PyQt5.QtGui import QImage, QPixmap
from core.crash_logger import log_exception
from core.watchdog import get_plugin_health
from datetime import datetime, timedelta


from core.watchdog import get_plugin_health
from datetime import datetime, timedelta

class FrameProcessor(QThread):
    frame_processed = pyqtSignal(str, np.ndarray)

    def __init__(self, plugin_manager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.running = True
        self.queue = Queue(maxsize=1)
        self.last_valid_results = {}  # {cam_id: {plugin_name: (result, timestamp)}}

    def run(self):
        while self.running:
            try:
                try:
                    cam_id, frame = self.queue.get(timeout=0.5)
                except queue.Empty:
                    time.sleep(0.1)
                    continue

                now = time.time()
                results = self.plugin_manager.apply_plugins(frame, cam_id)

                if cam_id not in self.last_valid_results:
                    self.last_valid_results[cam_id] = {}

                # Store recent valid results
                for plugin_name in self.plugin_manager.plugins:
                    result = results.get(plugin_name)
                    if result is not None:
                        self.last_valid_results[cam_id][plugin_name] = (result, now)

                # Use valid results from past 5 seconds
                display_results = {}
                for plugin_name, (cached_result, ts) in self.last_valid_results[cam_id].items():
                    if now - ts <= 5:
                        display_results[plugin_name] = cached_result

                processed = self._apply_results(frame.copy(), display_results)
                self.frame_processed.emit(cam_id, processed)

            except Exception as e:
                log_exception(e, context="FrameProcessor run loop")

    def _apply_results(self, frame, results):
        y = 30
        for plugin, result in results.items():
            try:
                if not isinstance(result, dict):
                    continue
                label = plugin.replace("_", " ").title()
                summary = self._extract_summary(result)
                line = f"{label}: {summary}"
                cv2.putText(frame, line[:60], (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y += 25
            except Exception as e:
                log_exception(e, context=f"Render text for {plugin}")
        return frame

    def _extract_summary(self, data: dict) -> str:
        if "face_recognized" in data:
            name = data.get("person_name", "Unknown")
            conf = round(data.get("confidence", 0) * 100)
            return f"{name} ({conf}%)"
        if "helmet_detected" in data:
            return "✅" if data["helmet_detected"] else "❌"
        if "fire_detected" in data:
            return "🔥" if data["fire_detected"] else "Safe"
        if "intrusion_detected" in data:
            return "🚨" if data["intrusion_detected"] else "Clear"
        return str(data)

class LiveView(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(600)

        self.plugin_manager = None
        self.alert_manager = None
        self.camera_manager = None
        self.alerts_page = None
        self.dashboard_page = None

        self.camera_labels = {}
        self.loading_bars = {}
        self.grid_size = (2, 2)

        self.frame_processors = []
        self.last_frame_times = {}

        self.init_ui()
        self.setLayout(self.main_layout)

        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frames)
        self.frame_timer.start(100)

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        for size in [(1, 1), (2, 2), (2, 3), (3, 3)]:
            btn = QPushButton(f"{size[0]}x{size[1]}")
            btn.clicked.connect(lambda _, s=size: self.set_grid_size(s))
            btn_layout.addWidget(btn)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addLayout(self.grid_layout)

    def set_grid_size(self, size):
        self.grid_size = size
        self.refresh_camera_grid()

    def refresh_camera_grid(self):
        if not self.camera_manager:
            return

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.camera_labels.clear()
        self.loading_bars.clear()
        rows, cols = self.grid_size

        cam_ids = list(self.camera_manager.cameras.keys())

        if not cam_ids:
            # Try to use camera_sources from config as fallback for NVR
            config_path = "config/default_settings.json"
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    cam_ids = [f"NVR_Channel_{i+1}" for i, _ in enumerate(config.get("camera_sources", []))]
                except Exception as e:
                    print(f"[LiveView] Error reading camera_sources from config: {e}")

        total_slots = rows * cols
        for i in range(total_slots):
            row, col = divmod(i, cols)
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(2)
            label = QLabel()
            label.setMinimumSize(320, 240)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background:#111; border:1px solid #333;")
            loading_bar = QProgressBar()
            loading_bar.setRange(0, 0)
            loading_bar.setTextVisible(False)
            loading_bar.setFixedHeight(4)
            layout.addWidget(label)
            layout.addWidget(loading_bar)
            if i < len(cam_ids):
                cam_id = cam_ids[i]
                self.camera_labels[cam_id] = label
                self.loading_bars[cam_id] = loading_bar
                label.setToolTip(f"Camera: {cam_id}")
            else:
                label.setText("No Camera")
                loading_bar.hide()
            self.grid_layout.addWidget(container, row, col)

    def update_frames(self):
        if not self.camera_manager or not self.camera_labels:
            return
        current_time = time.time()
        for cam_id, label in self.camera_labels.items():
            if current_time - self.last_frame_times.get(cam_id, 0) < 0.1:
                continue
            frame = self.camera_manager.get_frame(cam_id)
            if frame is None:
                self.show_no_signal(label, cam_id)
                continue
            if self.plugin_manager and self.frame_processors:
                self.process_frame_async(cam_id, frame)
            else:
                self.display_frame(cam_id, frame)
            self.last_frame_times[cam_id] = current_time

    def process_frame_async(self, cam_id, frame):
        queued = False
        for processor in self.frame_processors:
            if not processor.queue.full():
                processor.queue.put((cam_id, frame.copy()))
                queued = True
                break
        if not queued:
            print(f"[LiveView] ⚠️ Frame drop: no available processor for {cam_id}")

    def update_processed_frame(self, cam_id, processed_frame):
        if cam_id not in self.camera_labels:
            return
        label = self.camera_labels[cam_id]

        def safe_update():
            try:
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                pixmap = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                if cam_id in self.loading_bars:
                    self.loading_bars[cam_id].hide()
            except Exception as e:
                self.show_no_signal(label, cam_id)

        QTimer.singleShot(0, safe_update)

    def display_frame(self, cam_id, frame):
        try:
            if cam_id not in self.camera_labels:
                return
            label = self.camera_labels[cam_id]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            if cam_id in self.loading_bars:
                self.loading_bars[cam_id].hide()
        except Exception as e:
            self.show_no_signal(self.camera_labels.get(cam_id), cam_id)

    def show_no_signal(self, label, cam_id):
        empty = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.putText(empty, "No Signal", (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        self.display_frame(cam_id, empty)
        if cam_id in self.loading_bars:
            self.loading_bars[cam_id].show()

    def closeEvent(self, event):
        for processor in self.frame_processors:
            processor.running = False
            processor.quit()
            processor.wait()
        if self.camera_manager:
            self.camera_manager.stop_all_cameras()
        super().closeEvent(event)

    def set_camera_manager(self, manager):
        self.camera_manager = manager
        self.refresh_camera_grid()
        QTimer.singleShot(100, self.init_threads)  # 🔁 slight delay ensures camera_labels is populated


    def set_plugin_manager(self, manager):
        self.plugin_manager = manager
        self.init_threads()

    def init_threads(self):
        if self.plugin_manager and not self.frame_processors:
            for _ in range(min(4, QThread.idealThreadCount())):
                processor = FrameProcessor(self.plugin_manager)
                processor.frame_processed.connect(self.update_processed_frame)
                self.frame_processors.append(processor)
                processor.start()

    def set_alert_manager(self, manager):
        self.alert_manager = manager

    def set_alerts_page(self, alerts_page_widget):
        self.alerts_page = alerts_page_widget

    def set_dashboard_page(self, dashboard_page):
        self.dashboard_page = dashboard_page
