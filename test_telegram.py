import os
import requests
import cv2
import time

# ------------------ CONFIGURATION ------------------
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

# ------------------ ALERT FUNCTION ------------------
def send_telegram_alert(message, image_path=None):
    if image_path:  # send photo if path provided
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': open(image_path, 'rb')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': message}
        try:
            requests.post(url, files=files, data=data)
            print("Telegram alert sent with photo!")
        except Exception as e:
            print("Failed to send alert:", e)
    else:  # just send text
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        try:
            requests.get(url, params=params)
            print("Telegram alert sent!")
        except Exception as e:
            print("Failed to send alert:", e)

# ------------------ TEST ALERT ------------------
send_telegram_alert("Hello! This is a test alert from your Python bot.")
# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access webcam")
    exit()

print("Press SPACE to capture and send image, Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read frame")
        break

    # Show live feed
    cv2.imshow("Press SPACE to capture", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):  # SPACE key pressed
        # Save the image
        cv2.imwrite("alert.jpg", frame)
        print("Image captured!")
        # Send the alert with image
        send_telegram_alert("📸 Webcam Test Alert!", "alert.jpg")
        print("Alert sent!")
    elif key == ord('q'):  # Q key pressed
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
