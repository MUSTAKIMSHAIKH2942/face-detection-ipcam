from core.log_manager import LogManager

log = LogManager()

sample_data = {
    "face_recognized": True,
    "person_name": "TestUser",
    "confidence": 0.98
}

log.log("face_recognition", sample_data)
print("✅ Log attempted. Check logs/face_recognition/ for today's file.")
