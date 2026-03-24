"""
system.py — AWSSSystem Orchestrator
=====================================
Top-level class that owns all hardware and processing objects and
runs the main detection → classify → actuate → log pipeline.

"""

import time
from datetime import datetime

import RPi.GPIO as GPIO

from config import (
    FLAP,
    HOLD_TIME,
    WINDOW_START,
    WINDOW_END,
    IR_DEBOUNCE,
    SETTLE_DELAY,
    BIN_HEIGHT,
    FULL_AT_CM,
    ULTRASONIC_SENSORS,
)
from hardware.ir_sensor import IRSensor
from hardware.camera import Camera
from hardware.flap_controller import FlapController
from hardware.bin_sensor import BinLevelSensor, create_bin_sensors
from processing.classifier import HSVBagClassifier
from utils.storage import StorageManager
from utils.logger import (
    log_bin_full,
    log_bin_status,
    write_session_header,
    write_session_footer,
)


class AWSSSystem:
    """Top-level AWSS pipeline orchestrator."""

    def __init__(
        self,
        settle_delay: float = SETTLE_DELAY,
        hold_time: float = HOLD_TIME,
    ):
        self.delay_after_trigger = settle_delay
        self.hold_time = hold_time

        # ── Hardware (initialized in start()) ─────────────────────────────
        self.ir_sensor: IRSensor | None = None
        self.camera: Camera | None = None
        self.flap_controller: FlapController | None = None
        self.bin_sensors: list[BinLevelSensor] = []

        # ── Processing ────────────────────────────────────────────────────
        self.classifier = HSVBagClassifier()
        self.storage = StorageManager()

        # ── Session state ─────────────────────────────────────────────────
        self.total_bags = 0
        self.results_log: list[dict] = []
        self.category_counts = {
            "RECYCLING": 0,
            "COMPOST": 0,
            "GARBAGE": 0,
            "UNKNOWN": 0,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ══════════════════════════════════════════════════════════════════════════

    def start(self):
        """Initialize all hardware and print system config summary."""
        print("=" * 60)
        print("  AWSS — Automated Waste Sorting System")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # IR sensor
        self.ir_sensor = IRSensor()
        print(f"\n[HW] IR breakbeam on GPIO {self.ir_sensor.pin}")

        # Ultrasonic bin-level sensors
        time.sleep(0.5)
        self.bin_sensors = create_bin_sensors()

        # Camera
        self.camera = Camera()
        self.camera.start()

        # Flap controller (PCA9685)
        self.flap_controller = FlapController()
        self.flap_controller.print_config()

        # Print config summary
        self._print_config_summary()

        # Neutral all flaps
        self.flap_controller.reset_position()
        print("\n  ✓ All flaps at neutral")
        print("\n[AWSS] System ready. Waiting for bags...")
        print("  Ctrl+C to stop\n")

        # Session header in bin log
        active = [s.bin_name for s in self.bin_sensors]
        write_session_header(active, BIN_HEIGHT, FULL_AT_CM,
                             self.delay_after_trigger, IR_DEBOUNCE)

    def shutdown(self):
        """Graceful shutdown: neutralize flaps, release resources, log session."""
        print("[AWSS] Returning flaps to neutral...")

        if self.flap_controller:
            self.flap_controller.close()

        if self.camera:
            self.camera.stop()

        GPIO.cleanup()

        write_session_footer(self.total_bags, self.category_counts)

        print(f"[AWSS] Done — {self.total_bags} bags processed.")
        print(f"  Sorting log : {self.storage.log_dir}/sorting_log_*.txt")
        print(f"  Bin levels  : data/logs/bin_levels.txt")
        print(f"  Captures    : {self.storage.capture_dir}/")

    # ══════════════════════════════════════════════════════════════════════════
    # CORE PIPELINE
    # ══════════════════════════════════════════════════════════════════════════

    def process_bag(self) -> dict:
        """Run one full detection → classify → actuate → log cycle.

        Returns:
            Result dict with category, coverage, bag_number, elapsed, etc.
        """
        # ── Step 1: Wait for IR trigger ───────────────────────────────────
        print(f"{'─' * 60}")
        print(f"[BAG {self.total_bags + 1}] Waiting for bag...")
        self.ir_sensor.wait_for_bag()
        t_detect = time.time()
        print("  ✓ Bag detected")

        # ── Step 2: Wait for bag to enter camera FOV ──────────────────────
        wait_remaining = WINDOW_START - (time.time() - t_detect)
        if wait_remaining > 0:
            time.sleep(wait_remaining)

        # ── Step 3: Burst capture within visibility window ────────────────
        burst_frames = []
        while (time.time() - t_detect) < WINDOW_END:
            frame_bgr = self.camera.capture_array()
            t_cap = time.time() - t_detect
            burst_frames.append((frame_bgr, t_cap))

        print(
            f"  Captured {len(burst_frames)} frames "
            f"({burst_frames[0][1] * 1000:.0f}ms – "
            f"{burst_frames[-1][1] * 1000:.0f}ms)"
        )

        # ── Step 4: Classify burst ────────────────────────────────────────
        result = self.classifier.classify_burst(burst_frames)
        category = result["category"]
        coverage = result["coverage"]
        best_idx = result["best_idx"]
        frame_results = result["frame_results"]
        elapsed = time.time() - t_detect

        self.category_counts[category] = self.category_counts.get(category, 0) + 1
        self.total_bags += 1

        best_time = frame_results[best_idx][2]
        print(
            f"  Classified : {category}  ({coverage * 100:.1f}% coverage)  "
            f"best frame #{best_idx} at {best_time * 1000:.0f}ms  "
            f"[{elapsed:.2f}s total]"
        )

        # ── Step 4b: Save burst frames ────────────────────────────────────
        bag_dir = self.storage.save_burst_frames(
            self.total_bags, burst_frames, frame_results, best_idx
        )
        print(f"  Saved {len(burst_frames)} frames to {bag_dir}/")

        # ── Step 5: Log sort event ────────────────────────────────────────
        self.storage.save_log_entry(category, coverage, elapsed)

        # ── Step 6: Actuate flap ──────────────────────────────────────────
        self._actuate(category)

        # ── Step 7: Hold, then return to neutral ─────────────────────────
        if category in ("RECYCLING", "COMPOST"):
            print(f"  Holding {self.hold_time}s...")
            time.sleep(self.hold_time)

        print("  Returning flaps to neutral...")
        self.flap_controller.reset_position()
        print(
            f"  ✓ Flaps at neutral "
            f"(RECYCLING={FLAP['RECYCLING']['neutral']}°, "
            f"COMPOST={FLAP['COMPOST']['neutral']}°)"
        )

        # ── Step 8: Check bin levels ─────────────────────────────────────
        full_bins = self.check_bin_levels()

        # ── Session stats ─────────────────────────────────────────────────
        print(
            f"\n  Session totals: "
            f"RECYCLING={self.category_counts['RECYCLING']}  "
            f"COMPOST={self.category_counts['COMPOST']}  "
            f"GARBAGE={self.category_counts['GARBAGE']}  "
            f"UNKNOWN={self.category_counts['UNKNOWN']}"
        )

        bag_result = {
            "bag_number": self.total_bags,
            "category": category,
            "coverage": coverage,
            "elapsed": elapsed,
            "full_bins": full_bins,
        }
        self.results_log.append(bag_result)
        return bag_result

    # ══════════════════════════════════════════════════════════════════════════
    # BIN LEVEL CHECK
    # ══════════════════════════════════════════════════════════════════════════

    def check_bin_levels(self) -> set[str]:
        """Poll all active ultrasonic sensors and return names of full bins."""
        if not self.bin_sensors:
            print("  (No ultrasonic sensors active)")
            return set()

        print("  Checking bin levels...")
        full_bins = set()
        for sensor in self.bin_sensors:
            status = sensor.get_status()
            dist = status["distance_cm"]
            pct = status["fill_pct"]
            log_bin_status(sensor.bin_name, dist, pct if pct is not None else 0)
            if status["is_full"]:
                log_bin_full(sensor.bin_name, dist, pct)
                full_bins.add(sensor.bin_name)

        if full_bins:
            print(f"  ⚠ FULL BIN(S) DETECTED: {full_bins}")
            print("  ⚠ Alert logged to bin_levels.txt")

        return full_bins

    # ══════════════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _actuate(self, category: str):
        """Move the correct flap to active position."""
        if category == "RECYCLING":
            cfg = FLAP["RECYCLING"]
            print(f"  → ch{cfg['channel']} to {cfg['active']}° (RECYCLING bin)")
            self.flap_controller.move_servo("RECYCLING", "active")

        elif category == "COMPOST":
            cfg = FLAP["COMPOST"]
            print(f"  → ch{cfg['channel']} to {cfg['active']}° (COMPOST bin)")
            self.flap_controller.move_servo("COMPOST", "active")

        elif category == "GARBAGE":
            print("  → No flap — center passthrough (GARBAGE bin)")

        else:
            print("  → UNKNOWN color — defaulting to center passthrough")
            print("  ⚠ Check lighting or add new color range")

    def _print_config_summary(self):
        """Print timing and sensor config to console."""
        active = [s.bin_name for s in self.bin_sensors]

        print(f"\n  Bin level config:")
        print(f"    Bin height : {BIN_HEIGHT} cm")
        print(f"    Full at    : <= {FULL_AT_CM} cm")
        print(f"    Active sensors: {active}")

        print(f"\n  Timing (calibrated from visibility test):")
        print(f"    Settle delay : {self.delay_after_trigger}s  (bag in FOV: 920–1300ms)")
        print(f"    IR debounce  : {IR_DEBOUNCE * 1000:.0f}ms  (was 80ms)")
        print(f"    IR poll rate : ~5kHz")
        print(f"    Flap hold    : {self.hold_time}s")
        print(f"  Log dir      : {self.storage.log_dir}/")
        print(f"  Captures     : {self.storage.capture_dir}/")
