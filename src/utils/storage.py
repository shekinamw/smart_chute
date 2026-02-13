"""Storage - saves images and logs."""

import os
from datetime import datetime

class StorageManager:
    """Manages file storage for images and logs."""

    def __init__(self, base_dir="data"):
        self.capture_dir = os.path.join(base_dir, "captures")
        self.log_dir = os.path.join(base_dir, "logs")

        # Create directories
        os.makedirs(self.capture_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def get_capture_path(self):
        """Generate path for new capture."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bag_{timestamp}.jpg"
        return os.path.join(self.capture_dir, filename), filename

    def save_log(self, entry):
        """Save log entry."""
        log_file = os.path.join(
            self.log_dir,
            f"log_{datetime.now().strftime('%Y%m%d')}.txt"
        )

        with open(log_file, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Time: {entry['timestamp']}\n")
            f.write(f"Category: {entry['category']}\n")
            f.write(f"Color: {entry['color']}\n")
            f.write(f"Confidence: {entry['confidence']:.1f}%\n")