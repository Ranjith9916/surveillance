# AI Surveillance & Face Recognition Alert System

An intelligent real-time surveillance system powered by **YOLOv8** and **DeepFace** that performs object detection (e.g., weapons, phones) and facial recognition with automated Telegram alerts.

---

## 🚀 Features

- **Real-Time Object Detection**: Uses Ultralytics YOLOv8 for detecting suspicious objects (knives, guns, cell phones).
- **Face Recognition**: Uses DeepFace to recognize known individuals and detect unknown visitors.
- **Automated Telegram Alerts**: Sends instant notifications and snapshot images via Telegram bot whenever alerts are triggered.
- **Image Dataset Capture**: Built-in script to easily capture known faces from webcam.

---

## 📁 Project Structure

```text
surveillance/
├── Known_faces/          # Directories containing reference images for known individuals
│   └── <person_name>/    # Images (1.jpg, 2.jpg, ...)
├── capture_images.py     # Utility to capture reference face photos via webcam
├── main_updated.py       # Main surveillance and alert script
├── test_telegram.py      # Script to verify Telegram bot alerts
├── yolov8n.pt            # Pre-trained YOLOv8 nano model
├── requirements.txt      # Project Python dependencies
├── .env.example          # Sample environment variables file
└── .gitignore            # Git ignore rules for venv, secrets, and caches
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Ranjith9916/surveillance.git
cd surveillance
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env   # On Windows
# or: cp .env.example .env on Linux/macOS
```
Open `.env` and fill in your Telegram Bot credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

---

## 💻 Usage

### 1. Test Telegram Bot Connection
```bash
python test_telegram.py
```

### 2. Add Known Faces
Run the capture utility to save reference images of a person:
```bash
python capture_images.py
```
Or manually place image files under `Known_faces/<person_name>/`.

### 3. Start Surveillance
```bash
python main_updated.py
```
Press `q` to terminate the surveillance window.