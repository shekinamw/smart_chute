"""
config.py — All AWSS system constants and hardware pin assignments.
===================================================================
Single source of truth for every tunable parameter. Modules import
from here instead of defining their own magic numbers.

To override at runtime, use CLI args in main.py (they patch this module).
"""

import os

# ═══════════════════════════════════════════════════════════════════════════════
# GPIO PIN ASSIGNMENTS (BCM numbering)
# ═══════════════════════════════════════════════════════════════════════════════

# ── IR breakbeam sensor ───────────────────────────────────────────────────────
IR_PIN      = 18        # HIGH = clear, LOW = beam broken
IR_DEBOUNCE = 0.010     # 10 ms  (was 80 ms — bags transit beam in <80 ms)

# ── Ultrasonic sensors (HC-SR04) ──────────────────────────────────────────────
# Only RECYCLING is wired.  Uncomment others when physically connected.
ULTRASONIC_SENSORS = {
    "RECYCLING": {"trig": 27, "echo": 17},
    # "COMPOST":   {"trig": 13, "echo": 19},
    # "GARBAGE":   {"trig": 5,  "echo": 6},
}

ULTRASONIC_TIMEOUT  = 0.04      # seconds per echo wait
ULTRASONIC_SAMPLES  = 5         # median-of-N for noise rejection
SPEED_OF_SOUND_CM_S = 34300

# ═══════════════════════════════════════════════════════════════════════════════
# PCA9685 SERVO DRIVER
# ═══════════════════════════════════════════════════════════════════════════════
PCA9685_ADDR = 0x40
I2C_BUS      = 1
PWM_FREQ_HZ  = 50

# Register map
MODE1     = 0x00
PRESCALE  = 0xFE
LED0_ON_L = 0x06

# ═══════════════════════════════════════════════════════════════════════════════
# FLAP CONFIGURATION (per waste category)
# ═══════════════════════════════════════════════════════════════════════════════
FLAP = {
    "RECYCLING": {
        "channel":      15,
        "neutral":      10,
        "active":       65,
        "min_pulse_us": 500,
        "max_pulse_us": 2500,
    },
    "COMPOST": {
        "channel":      11,
        "neutral":      103,
        "active":       50,
        "min_pulse_us": 500,
        "max_pulse_us": 2500,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# HSV CLASSIFICATION RANGES  (calibrated from actual bags inside chute)
# ═══════════════════════════════════════════════════════════════════════════════
HSV_RANGES = {
    "RECYCLING": [((5,  100, 60), (30,  255, 255))],   # blue:  H 5-30,  S 100+, V 60+
    "COMPOST":   [((35,  20, 60), (75,  255, 255))],    # green: H 35-75, S 20+,  V 60+
    "GARBAGE":   [((0,    0,  0), (180, 255,  70))],    # black: any H/S, V ≤ 70
}
COVERAGE_THRESHOLD = 0.05

# ═══════════════════════════════════════════════════════════════════════════════
# TIMING (calibrated from visibility_test.py)
# ═══════════════════════════════════════════════════════════════════════════════
SETTLE_DELAY  = 0.95    # seconds after IR trigger before capture window opens
HOLD_TIME     = 2.0     # seconds flap stays in active position
WINDOW_START  = 0.87    # seconds — bag enters camera FOV
WINDOW_END    = 1.3     # seconds — bag leaves camera FOV

# ═══════════════════════════════════════════════════════════════════════════════
# BIN LEVEL DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
BIN_HEIGHT = 30.0       # cm  (sensor-to-floor distance)
FULL_AT_CM = 5.0        # cm  (distance at which bin is "full")

# ═══════════════════════════════════════════════════════════════════════════════
# CAMERA
# ═══════════════════════════════════════════════════════════════════════════════
CAMERA_RESOLUTION = (2304, 1296)
CAMERA_FORMAT     = "RGB888"
LENS_POSITION     = 5.0     # manual focus (higher = closer)
CAMERA_WARMUP     = 2.0     # seconds

# ═══════════════════════════════════════════════════════════════════════════════
# FILE PATHS
# ═══════════════════════════════════════════════════════════════════════════════
LOG_DIR       = os.path.join("data", "logs")
CAPTURE_DIR   = os.path.join("data", "captures")
BIN_LEVEL_LOG = os.path.join(LOG_DIR, "bin_levels.txt")
