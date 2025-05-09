import cv2

print("[TEST] Opening webcam...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # or cv2.CAP_ANY or cv2.CAP_MSMF

if not cap.isOpened():
    print("❌ Camera failed to open.")
    exit()

print("✅ Camera opened. Showing feed... Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame.")
        break
    cv2.imshow("Test Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
