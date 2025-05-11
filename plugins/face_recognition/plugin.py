# # """
# # Face Recognition Plugin - Simulates face recognition from video frames.

# # Author: ItsOji Team
# # """

# # import random
# # import time
# # from datetime import datetime
# # from plugins.base_plugin import BasePlugin
# # from core.log_manager import LogManager


# # class Plugin(BasePlugin):
# #     """Face Recognition Plugin."""

# #     def __init__(self):
# #         super().__init__()
# #         self.model = None
# #         self.logger = LogManager()
# #         self.plugin_name = "face_recognition"
# #         self.last_logged_result = None
# #         self.known_faces = ["Person_1", "Person_2", "Person_3"]

# #     def load_model(self):
# #         print("[FaceRecognitionPlugin] Model loaded (simulated).")
# #         self.model = True

# #     def process(self, frame, camera_id=None):
# #         recognized = random.choice([True, False])
# #         if recognized:
# #             person_name = random.choice(self.known_faces)
# #             confidence = round(random.uniform(0.85, 0.98), 2)
# #         else:
# #             person_name = "Unknown"
# #             confidence = round(random.uniform(0.50, 0.70), 2)

# #         timestamp_ms = int(time.time() * 1000)

# #         result = {
# #             "face_recognized": recognized,
# #             "person_name": person_name,
# #             "confidence": confidence,
# #             "camera_id": camera_id,
# #             "timestamp_ms": timestamp_ms
# #         }

# #         # Smart logging
# #         log_cfg = self.logger.get_plugin_config(self.plugin_name)
# #         if log_cfg:
# #             trigger_filter = log_cfg.get("log_trigger_filter", "")
# #             distinct_only = trigger_filter == "distinct_only"

# #             if not distinct_only or (self.last_logged_result != result):
# #                 self.logger.log(self.plugin_name, result)
# #                 self.last_logged_result = result

# #         return result

# #     def release(self):
# #         self.model = None
# #         print("[FaceRecognitionPlugin] Model released.")
    
# """
# Face Recognition Plugin - Simulates face recognition from video frames.

# Author: ItsOji Team
# """

# import random
# import time
# import cv2
# import os
# import numpy as np
# from datetime import datetime
# from plugins.base_plugin import BasePlugin
# from core.log_manager import LogManager


# class Plugin(BasePlugin):
#     """Face Recognition Plugin."""

#     def __init__(self):
#         super().__init__()
#         self.model = None
#         self.logger = LogManager()
#         self.plugin_name = "face_recognition"
#         self.last_logged_result = None
#         self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
#         self.known_faces = []  # To store names of known faces
#         self.face_images = []  # To store face images for training
#         self.face_labels = []  # To store labels corresponding to known faces
#         self.load_model()

#     def load_model(self):
#         """Simulate loading the face recognition model and training with known face images."""
#         print("[FaceRecognitionPlugin] Loading and training model with known faces.")

#         known_faces_path = r"C:\Users\musta\OneDrive\Desktop\app\face-detection-ipcam\plugins\face_recognition\Known_faces"

#         # Get all image files in the "Known_faces" folder
#         image_files = [f for f in os.listdir(known_faces_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
#         for image_file in image_files:
#             # Load image from file
#             image_path = os.path.join(known_faces_path, image_file)
#             image = cv2.imread(image_path)
#             gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#             # Assume each file name (without extension) is the person's name
#             person_name = os.path.splitext(image_file)[0]

#             # Detect faces in the image using OpenCV's Haar Cascade
#             face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#             faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)

#             # Process detected faces and prepare data for training
#             for (x, y, w, h) in faces:
#                 face_image = gray_image[y:y+h, x:x+w]
#                 self.face_images.append(face_image)
#                 self.face_labels.append(len(self.known_faces))  # Assign a unique label for each person

#             # Add person's name to known faces list
#             self.known_faces.append(person_name)

#         # Train the face recognizer with the collected data
#         self.face_labels = np.array(self.face_labels)
#         self.face_recognizer.train(self.face_images, self.face_labels)
#         self.model = True
#         print("[FaceRecognitionPlugin] Model loaded and trained with known faces.")

#     def process(self, frame, camera_id=None):
#         """
#         Process a video frame, simulate face recognition, and log the results.

#         Args:
#             frame (ndarray): Video frame from the camera.
#             camera_id (str): ID of the camera capturing the frame.

#         Returns:
#             dict: Result of face recognition containing recognized status, person name, confidence, etc.
#         """
#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#         faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

#         result = {
#             "face_recognized": False,
#             "person_name": "Unknown",
#             "confidence": 0.0,
#             "camera_id": camera_id,
#             "timestamp_ms": int(time.time() * 1000)
#         }

#         # If faces are detected in the frame
#         if len(faces) > 0:
#             for (x, y, w, h) in faces:
#                 face_image = gray_frame[y:y+h, x:x+w]
#                 label, confidence = self.face_recognizer.predict(face_image)

#                 person_name = self.known_faces[label] if confidence < 100 else "Unknown"
#                 result["face_recognized"] = True
#                 result["person_name"] = person_name
#                 result["confidence"] = round(100 - confidence, 2)

#         # Smart logging
#         log_cfg = self.logger.get_plugin_config(self.plugin_name)
#         if log_cfg:
#             trigger_filter = log_cfg.get("log_trigger_filter", "")
#             distinct_only = trigger_filter == "distinct_only"

#             # Log if needed (only log if distinct or if the result is different from the last one)
#             if not distinct_only or (self.last_logged_result != result):
#                 self.logger.log(self.plugin_name, result)
#                 self.last_logged_result = result

#         return result

#     def release(self):
#         """Release resources and cleanup."""
#         self.model = None
#         print("[FaceRecognitionPlugin] Model released.")
"""
Face Recognition Plugin - Simulates face recognition from video frames.

Author: ItsOji Team
"""

import random
import time
import cv2
import os
import numpy as np
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager


class Plugin(BasePlugin):
    """Face Recognition Plugin."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.logger = LogManager()
        self.plugin_name = "face_recognition"
        self.last_logged_result = None
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_faces = []  # To store names of known faces
        self.face_images = []  # To store face images for training
        self.face_labels = []  # To store labels corresponding to known faces
        self.load_model()

    def load_model(self):
        """Load and train the face recognition model with images from the Known_faces directory."""
        print("[FaceRecognitionPlugin] Loading and training model with known faces.")

        known_faces_path = r"C:\Users\musta\OneDrive\Desktop\app\face-detection-ipcam\plugins\face_recognition\Known_faces"
        
        # Loop through the directories (one for each person) in Known_faces
        for person_folder in os.listdir(known_faces_path):
            person_folder_path = os.path.join(known_faces_path, person_folder)

            # Ensure it's a directory
            if not os.path.isdir(person_folder_path):
                continue

            # Loop through all images of that person
            for image_file in os.listdir(person_folder_path):
                # Read the image (only if it ends with an image extension)
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(person_folder_path, image_file)
                    image = cv2.imread(image_path)
                    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    # Detect faces in the image using Haar Cascade
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)

                    # Process detected faces and prepare data for training
                    for (x, y, w, h) in faces:
                        face_image = gray_image[y:y+h, x:x+w]
                        self.face_images.append(face_image)
                        self.face_labels.append(len(self.known_faces))  # Label based on position in known_faces

            # Add person name to known faces list (folder name)
            self.known_faces.append(person_folder)

        # Train the face recognizer with the collected data
        self.face_labels = np.array(self.face_labels)
        if len(self.face_images) > 0:
            self.face_recognizer.train(self.face_images, self.face_labels)
            self.model = True
            print("[FaceRecognitionPlugin] Model loaded and trained with known faces.")
        else:
            print("[FaceRecognitionPlugin] No faces found to train the model.")

    def process(self, frame, camera_id=None):
        """
        Process a video frame, simulate face recognition, and log the results.

        Args:
            frame (ndarray): Video frame from the camera.
            camera_id (str): ID of the camera capturing the frame.

        Returns:
            dict: Result of face recognition containing recognized status, person name, confidence, etc.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        result = {
            "face_recognized": False,
            "person_name": "Unknown",
            "confidence": 0.0,
            "camera_id": camera_id,
            "timestamp_ms": int(time.time() * 1000)
        }

        # If faces are detected in the frame
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_image = gray_frame[y:y+h, x:x+w]
                label, confidence = self.face_recognizer.predict(face_image)

                person_name = self.known_faces[label] if confidence < 100 else "Unknown"
                result["face_recognized"] = True
                result["person_name"] = person_name
                result["confidence"] = round(100 - confidence, 2)

        # Smart logging
        log_cfg = self.logger.get_plugin_config(self.plugin_name)
        if log_cfg:
            trigger_filter = log_cfg.get("log_trigger_filter", "")
            distinct_only = trigger_filter == "distinct_only"

            # Log if needed (only log if distinct or if the result is different from the last one)
            if not distinct_only or (self.last_logged_result != result):
                self.logger.log(self.plugin_name, result)
                self.last_logged_result = result

        return result

    def release(self):
        """Release resources and cleanup."""
        self.model = None
        print("[FaceRecognitionPlugin] Model released.")
