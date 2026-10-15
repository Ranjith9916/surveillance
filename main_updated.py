import os
import cv2
from deepface import DeepFace
import numpy as np
import time
import requests
from ultralytics import YOLO

# ===============================
# Configuration
# ===============================
def load_env_file(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("[WARNING] TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set. Please configure them in .env")

OBJECTS_TO_DETECT = ["knife", "cell phone", "gun"]

def send_telegram_alert(message, image=None):
    if image is not None:
        # Save the image temporarily
        cv2.imwrite("alert.jpg", image)
        # Send photo with caption
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': open('alert.jpg', 'rb')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': message}
        try:
            response = requests.post(url, files=files, data=data)
            print("[INFO] Telegram alert with photo sent!")
            # Clean up
            files['photo'].close()
            os.remove('alert.jpg')
        except Exception as e:
            print("[ERROR] Failed to send photo alert:", e)
    else:
        # Send text only
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        try:
            requests.get(url, params=data)
            print("[INFO] Telegram text alert sent!")
        except Exception as e:
            print("[ERROR] Failed to send text alert:", e)

# Load YOLO model
print("[INFO] Loading YOLO model...")
model = YOLO("yolov8n.pt")

# ===============================
# Step 1: Load all known faces
# ===============================
known_faces_dir = "known_faces"
people = []

for person_name in os.listdir(known_faces_dir):
    person_folder = os.path.join(known_faces_dir, person_name)
    if not os.path.isdir(person_folder):
        continue

    images = []
    for filename in os.listdir(person_folder):
        filepath = os.path.join(person_folder, filename)
        images.append(filepath)

    if len(images) > 0:
        people.append({"name": person_name, "images": images})
        print(f"[LOADED] {person_name} with {len(images)} images")

print(f"[INFO] {len(people)} people loaded.\n")

# ===============================
# Step 2: Start webcam
# ===============================
cap = cv2.VideoCapture(0)
print("[INFO] Smart Surveillance running... Press 'q' to quit.")

# Alert cooldown to avoid spamming
last_alert_time = {}
alert_cooldown = 5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Initialize detection results
    unknown_detected = False
    objects_detected = []
    
    # DeepFace detect faces and analyze
    try:
        faces = DeepFace.extract_faces(img_path=frame, enforce_detection=False)
        for face in faces:
            face_area = face['facial_area']
            x, y, w, h = face_area['x'], face_area['y'], face_area['w'], face_area['h']
            
            # Try to match with known faces
            matched = False
            for person in people:
                if len(person["images"]) > 0:
                    try:
                        verification = DeepFace.verify(
                            frame[y:y+h, x:x+w],  # Crop to face area
                            person["images"][0],
                            enforce_detection=False,
                            model_name='Facenet'
                        )
                        if verification["verified"]:
                            name = person["name"]
                            matched = True
                            
                            # Draw green rectangle for known face
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                                      0.9, (0, 255, 0), 2)
                            break
                    except Exception as e:
                        continue
            
            if not matched:
                unknown_detected = True
                # Draw red rectangle for unknown face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.9, (0, 0, 255), 2)
    
    except Exception as e:
        print(f"Face detection error: {e}")
        
    # Object Detection with YOLO
    results = model(frame, verbose=False)
    for r in results:
        for box in r.boxes:
            class_name = model.names[int(box.cls)]
            if class_name in OBJECTS_TO_DETECT:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, class_name, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                objects_detected.append(class_name)

    # Handle alerts with cooldown
    current_time = time.time()
    
    # Check for unknown faces
    if unknown_detected and ("unknown" not in last_alert_time or 
                           (current_time - last_alert_time["unknown"]) > alert_cooldown):
        alert_message = "🚨 ALERT: Unknown person detected!"
        send_telegram_alert(alert_message, frame)
        last_alert_time["unknown"] = current_time

    # Check for suspicious objects
    if objects_detected and ("objects" not in last_alert_time or 
                           (current_time - last_alert_time["objects"]) > alert_cooldown):
        alert_message = f"🚨 ALERT: Suspicious objects detected: {', '.join(objects_detected)}"
        send_telegram_alert(alert_message, frame)
        last_alert_time["objects"] = current_time

    # Display the frame
    cv2.imshow("Smart Surveillance", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()