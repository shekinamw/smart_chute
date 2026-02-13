"""Simple Flask app for AWSS."""

import os
import sys
import threading
import time
from flask import Flask, jsonify, send_file, render_template

# Add project root to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# Import directly from src
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
            
            # Process it
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
        system = AWSSSystem()
        system.start()
        
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

@app.route("/latest-image")
def latest_image():
    """Serve latest image."""
    if not state["last"] or "image_path" not in state["last"]:
        return ("No image", 404)
    
    path = state["last"]["image_path"]
    if os.path.exists(path):
        return send_file(path, mimetype="image/jpeg")
    return ("Not found", 404)

@app.route("/")
def home():
    """Dashboard page."""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
