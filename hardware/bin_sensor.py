"""
hardware/bin_sensor.py — HC-SR04 Ultrasonic Bin Level Sensor
=============================================================
Measures distance to waste surface to calculate fill percentage.
"""

import time

import RPi.GPIO as GPIO

from config import (
    ULTRASONIC_SENSORS,
    ULTRASONIC_TIMEOUT,
    ULTRASONIC_SAMPLES,
    SPEED_OF_SOUND_CM_S,
    BIN_HEIGHT,
    FULL_AT_CM,
)


class BinLevelSensor:
    """Single HC-SR04 ultrasonic sensor for one bin."""

    def __init__(self, bin_name: str, trig_pin: int, echo_pin: int):
        self.bin_name = bin_name
        self.trig = trig_pin
        self.echo = echo_pin

        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, GPIO.LOW)

    # ── Single measurement ────────────────────────────────────────────────────

    def _measure_once(self) -> float | None:
        """Fire one ultrasonic pulse and return distance in cm, or None."""
        GPIO.output(self.trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig, GPIO.LOW)

        t_start = time.time()
        while GPIO.input(self.echo) == GPIO.LOW:
            if time.time() - t_start > ULTRASONIC_TIMEOUT:
                return None

        pulse_start = time.time()
        while GPIO.input(self.echo) == GPIO.HIGH:
            if time.time() - pulse_start > ULTRASONIC_TIMEOUT:
                return None

        duration = time.time() - pulse_start
        return round((duration * SPEED_OF_SOUND_CM_S) / 2.0, 1)

    # ── Median-filtered measurement ───────────────────────────────────────────

    def measure_distance(self) -> float | None:
        """Take N readings and return the median distance in cm."""
        readings = []
        for _ in range(ULTRASONIC_SAMPLES):
            d = self._measure_once()
            if d is not None:
                readings.append(d)
            time.sleep(0.06)
        if not readings:
            return None
        readings.sort()
        return readings[len(readings) // 2]

    # ── Fill calculation ──────────────────────────────────────────────────────

    @staticmethod
    def fill_percent(distance_cm: float | None) -> float | None:
        """Convert distance reading to fill percentage."""
        if distance_cm is None:
            return None
        pct = (1.0 - (distance_cm / BIN_HEIGHT)) * 100.0
        return max(0.0, min(100.0, round(pct, 1)))

    # ── Public API (R3 diagram) ───────────────────────────────────────────────

    def is_full(self) -> bool:
        """True if measured distance ≤ FULL_AT_CM threshold."""
        dist = self.measure_distance()
        return dist is not None and dist <= FULL_AT_CM

    def get_status(self) -> dict:
        """Return a status dict with distance, fill %, and full flag.

        Returns:
            {"bin": str, "distance_cm": float|None,
             "fill_pct": float|None, "is_full": bool}
        """
        dist = self.measure_distance()
        pct = self.fill_percent(dist)
        full = dist is not None and dist <= FULL_AT_CM
        return {
            "bin": self.bin_name,
            "distance_cm": dist,
            "fill_pct": pct,
            "is_full": full,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY — create sensors from config
# ═══════════════════════════════════════════════════════════════════════════════

def create_bin_sensors() -> list[BinLevelSensor]:
    """Instantiate one BinLevelSensor per entry in ULTRASONIC_SENSORS config."""
    sensors = []
    for bin_name, pins in ULTRASONIC_SENSORS.items():
        sensor = BinLevelSensor(bin_name, pins["trig"], pins["echo"])
        print(f"[HW] Ultrasonic ({bin_name}) TRIG={pins['trig']} ECHO={pins['echo']}")
        sensors.append(sensor)
    return sensors
