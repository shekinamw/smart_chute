"""
hardware/camera.py — Pi Camera wrapper
=======================================
Wraps Picamera2 init, focus lock, and frame capture.
"""

import time

import cv2
import numpy as np
from picamera2 import Picamera2

from config import (
    CAMERA_RESOLUTION,
    CAMERA_FORMAT,
    LENS_POSITION,
    CAMERA_WARMUP,
)


class Camera:
    """Pi Camera Module 3 Wide (IMX708) with manual focus lock."""

    def __init__(
        self,
        resolution: tuple = CAMERA_RESOLUTION,
        fmt: str = CAMERA_FORMAT,
        lens_position: float = LENS_POSITION,
        warmup: float = CAMERA_WARMUP,
    ):
        self.resolution = resolution
        self.fmt = fmt
        self.lens_position = lens_position
        self.warmup = warmup
        self._cam: Picamera2 | None = None
        self.is_running = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        """Initialize camera hardware, lock focus, and begin streaming."""
        print("[HW] Initializing Pi Camera Module 3 Wide...")
        self._cam = Picamera2()
        self._cam.configure(
            self._cam.create_still_configuration(
                main={"size": self.resolution, "format": self.fmt}
            )
        )
        self._cam.start()
        time.sleep(self.warmup)

        # Lock autofocus to manual — AWB stays ON for correct colors
        self._cam.set_controls({
            "AfMode": 0,
            "LensPosition": self.lens_position,
        })
        time.sleep(0.5)
        self.is_running = True
        print(f"  ✓ Camera ready (focus locked: LensPosition={self.lens_position}, AWB: ON)")

    def stop(self):
        """Release camera resources."""
        if self._cam is not None:
            try:
                self._cam.stop()
            except Exception:
                pass
        self.is_running = False

    # ── Capture ───────────────────────────────────────────────────────────────

    def capture_array(self) -> np.ndarray:
        """Capture a single frame and return it as a BGR numpy array."""
        frame_rgb = self._cam.capture_array()
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
