# test_multiple_cameras.py
from core.camera_manager import CameraManager
import cv2

if __name__ == "__main__":
    cam_mgr = CameraManager()
    cam_mgr.add_camera(0, 'USB', 0)  # 0 for first webcam

    try:
        while True:
            frame = cam_mgr.get_frame(0)
            if frame is not None:
                cv2.imshow("Camera 0", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Important: Always release cameras and destroy windows
        cam_mgr.stop_all_cameras()
        cv2.destroyAllWindows()
