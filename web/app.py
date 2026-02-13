"""Simple Flask app for AWSS with live camera feed."""

import os
import sys
import threading
import time
import cv2
from flask import Flask, jsonify, send_file, render_template, Response
from threading import Lock

# Add project root to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from src.core.awss_system import AWSSSystem

app = Flask(__name__)

# Simple state
state = {
    "running": False,
    "last": None,
    "history": [],
    "bagCount": 0,
}
system = None
worker_thread = None
camera_lock = Lock()

def generate_frames():
    """Generate camera frames for live stream."""
    global system
    
    while True:
        if not system or not system.running:
            # No system running, send blank/waiting frame
            time.sleep(0.1)
            continue
        
        try:
            with camera_lock:
                # Capture frame
                frame = system.camera.capture_array()
                
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Optional: Add text overlay
                cv2.putText(frame_bgr, f"Bags: {state['bagCount']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2)
                
                # Encode as JPEG
                ret, buffer = cv2.imencode('.jpg', frame_bgr, 
                                          [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # ~10 FPS (adjust for performance)
        
        except Exception as e:
            print(f"Stream error: {e}")
            time.sleep(0.5)

def worker_loop():
    """Background worker - waits for bags and processes them."""
    global system
    
    while state["running"]:
        if not system:
            time.sleep(0.1)
            continue
        
        try:
            # Wait for bag
            system.ir_sensor.wait_for_bag()
            
            # Process it (with camera lock to not interfere with stream)
            with camera_lock:
                result = system.process_bag()
            
            # Update state
            state["bagCount"] += 1
            state["last"] = result
            state["history"].insert(0, result)
            if len(state["history"]) > 20:
                state["history"] = state["history"][:20]
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)

@app.route("/api/start", methods=["POST"])
def api_start():
    """Start the system."""
    global system, worker_thread
    
    if state["running"]:
        return jsonify({"ok": True, "message": "Already running"})
    
    try:
        # Create system
        system = AWSSSystem()
        system.start()
        
        # Start worker
        state["running"] = True
        state["bagCount"] = 0
        state["history"] = []
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
        
        return jsonify({"ok": True, "message": "Started"})
    
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Stop the system."""
    global system
    
    state["running"] = False
    
    if system:
        system.stop()
        system = None
    
    return jsonify({"ok": True, "message": "Stopped"})

@app.route("/api/status")
def api_status():
    """Get current status."""
    return jsonify(state)

@app.route('/video-feed')
def video_feed():
    """Live video stream endpoint."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/latest-image")
def latest_image():
    """Serve latest captured image (not live feed)."""
    if not state.get("last") or "image_path" not in state["last"]:
        return ("No image captured yet", 404)
    
    image_path = state["last"]["image_path"]
    
    if not os.path.isabs(image_path):
        image_path = os.path.join(BASE_DIR, image_path)
    
    if os.path.exists(image_path):
        return send_file(image_path, mimetype="image/jpeg")
    
    return ("Image not found", 404)

@app.route("/")
def home():
    """Dashboard page."""
    return render_template("index.html")

if __name__ == "__main__":
    print("Starting AWSS Dashboard...")
    print("Open: http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)