# Automated Waste Sorting Chute (Capstone Project)
Pi-powered waste sorting prototype with IR and camera color detection.
## Features
- Detect falling object with IR break-beam sensor
- Capture bag image using global shutter camera
- Classify bag by color (blue, green, black)
- Print waste type for demo purposes
- Modular and collaborative code design

  ## Folder Structure

  ## How to Run
  ### Installation

1. **Clone the repository**
```bash
git clone https://github.com/
cd wmart_chute
```

2. **Install dependencies**
bash
pip install -r requirements.txt


### Running the System

cd web
python app.py

### 4. Open Dashboard

http://localhost:5050

Or from another device: `http://YOUR_PI_IP:5050`

---

## 🏗️ How It Works

### Components

**1. IR Sensor** (`src/sensors/ir_sensor.py`)
- Detects when bag enters system
- Uses GPIO pins

**2. Camera** (`src/vision/camera.py`)
- Captures image of bag
- Uses Picamera2

**3. Classifier** (`src/vision/classifier.py`)
- Analyzes bag color using HSV
- Returns: GARBAGE (black), RECYCLING (blue), or COMPOST (green)

**4. Storage** (`src/utils/storage.py`)
- Saves images to `data/captures/`
- Saves logs to `data/logs/`

**5. Main System** (`src/core/awss_system.py`)
- Coordinates all components
- Processes each bag

**6. Web App** (`web/app.py`)
- Dashboard interface
- Start/stop controls
- Shows results

### Process Flow

1. IR sensor detects bag
   ↓
2. Camera captures image
   ↓
3. Classifier analyzes color
   ↓
4. Result displayed on dashboard
   ↓
5. Image and log saved
