"""
hardware/ir_sensor.py — IR Breakbeam Sensor
============================================
Wraps GPIO polling for the IR breakbeam on the chute entrance.

"""

import time
import RPi.GPIO as GPIO

from config import IR_PIN, IR_DEBOUNCE


class IRSensor:
    """IR breakbeam sensor on the chute entrance."""

    def __init__(self, pin: int = IR_PIN, debounce: float = IR_DEBOUNCE):
        self.pin = pin
        self.debounce = debounce
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # ── State queries ─────────────────────────────────────────────────────────

    def is_clear(self) -> bool:
        """True when beam is unbroken (no object)."""
        return GPIO.input(self.pin) == GPIO.HIGH

    def is_broken(self) -> bool:
        """True when beam is broken (object detected)."""
        return GPIO.input(self.pin) == GPIO.LOW

    # ── Blocking waits ────────────────────────────────────────────────────────

    def wait_for_bag(self):
        """Block until beam is broken and debounced.

        Uses fast polling (~5 kHz / 0.2 ms) so we don't miss bags that
        transit the beam quickly.  Debounce is 10 ms — enough to filter
        electrical noise but short enough to catch bags that break the
        beam for only 30–80 ms.
        """
        while not self.is_broken():
            time.sleep(0.0002)

        # Debounce: beam must stay broken for `debounce` seconds
        t0 = time.time()
        while time.time() - t0 < self.debounce:
            if not self.is_broken():
                return self.wait_for_bag()   # noise — restart
            time.sleep(0.0002)

    def wait_for_clear(self):
        """Block until beam is clear again (bag has passed)."""
        while self.is_broken():
            time.sleep(0.05)

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def verify_sensor(self) -> bool:
        """Quick sanity check — sensor should read HIGH (clear) at rest."""
        return self.is_clear()

    def cleanup(self):
        """Release GPIO resources (called by AWSSSystem.shutdown)."""
        # GPIO.cleanup() is called globally; nothing sensor-specific needed.
        pass
