"""Camera - handles image capture."""

from picamera2 import Picamera2
import time

class Camera:
    """Wrapper for Raspberry Pi Camera."""

    def __init__(self, width=1920, height=1080):
        self.camera = Picamera2()
        config = self.camera.create_still_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
        self.camera.configure(config)
        self.is_running = False

    def start(self):
        """Start camera."""
        if not self.is_running:
            self.camera.start()
            time.sleep(1.5)  # warmup
            self.is_running = True

    def stop(self):
        """Stop camera."""
        if self.is_running:
            self.camera.stop()
            self.is_running = False

    def capture_array(self):
        """Capture image as array."""
        return self.camera.capture_array()