"""Main AWSS System - coordinates everything."""

import cv2
import time
from datetime import datetime

from ..sensors.ir_sensor import IRSensor
from ..vision.camera import Camera
from ..vision.classifier import HSVBagClassifier
from ..utils.storage import StorageManager

class AWSSSystem:
    """Main system that coordinates all components."""

    def __init__(self, delay_after_trigger=1.0, ir_pin=23):
        self.delay = delay_after_trigger

        # Create components
        self.ir_sensor = IRSensor(pin=ir_pin)
        self.camera = Camera()
        self.classifier = HSVBagClassifier()
        self.storage = StorageManager()

        self.running = False

    def start(self):
        """Start the system."""
        self.camera.start()
        self.running = True

    def stop(self):
        """Stop the system."""
        self.running = False
        self.camera.stop()
        self.ir_sensor.cleanup()

    def process_bag(self):
        """Capture and classify a bag."""
        # Wait for bag to settle
        time.sleep(self.delay)

        # Capture image
        frame_rgb = self.camera.capture_array()
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Save image
        image_path, filename = self.storage.get_capture_path()
        cv2.imwrite(image_path, frame_bgr)

        # Classify
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        result = self.classifier.classify_hsv(frame_hsv)

        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["image_path"] = image_path
        result["image_filename"] = filename

        # Save log
        self.storage.save_log(result)

        return result