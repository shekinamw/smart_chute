"""
hardware/flap_controller.py — PCA9685 Servo Flap Controller
============================================================
Direct smbus2 I2C register writes to PCA9685 — no Blinka dependency
(incompatible with Python 3.13 / Debian Trixie).

"""

import time

import smbus2

from config import (
    PCA9685_ADDR,
    I2C_BUS,
    PWM_FREQ_HZ,
    MODE1,
    PRESCALE,
    LED0_ON_L,
    FLAP,
)


class FlapController:
    """Controls SG90 servo flaps via PCA9685 over I2C."""

    def __init__(self, bus: smbus2.SMBus | None = None):
        self.bus = bus or smbus2.SMBus(I2C_BUS)
        self.current_position: dict[str, int] = {}   # category → current angle
        self._pca_init()

    # ── PCA9685 initialization ────────────────────────────────────────────────

    def _pca_init(self):
        """Set PCA9685 to ~50 Hz PWM with auto-increment enabled."""
        self.bus.write_byte_data(PCA9685_ADDR, MODE1, 0x00)
        time.sleep(0.01)
        prescale_val = round(25_000_000 / (4096 * PWM_FREQ_HZ)) - 1
        old_mode = self.bus.read_byte_data(PCA9685_ADDR, MODE1)
        self.bus.write_byte_data(PCA9685_ADDR, MODE1, (old_mode & 0x7F) | 0x10)  # sleep
        self.bus.write_byte_data(PCA9685_ADDR, PRESCALE, prescale_val)
        self.bus.write_byte_data(PCA9685_ADDR, MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(PCA9685_ADDR, MODE1, old_mode | 0x80)  # restart
        print(f"[HW] PCA9685 @ 0x{PCA9685_ADDR:02X}")

    # ── Low-level PWM ─────────────────────────────────────────────────────────

    @staticmethod
    def _angle_to_ticks(angle_deg: float, min_us: int, max_us: int) -> int:
        period_us = 1_000_000 / PWM_FREQ_HZ
        pulse_us = min_us + (angle_deg / 180.0) * (max_us - min_us)
        return round((pulse_us / period_us) * 4096)

    def _set_channel(self, channel: int, on_tick: int, off_tick: int):
        base = LED0_ON_L + 4 * channel
        self.bus.write_byte_data(PCA9685_ADDR, base,     on_tick  & 0xFF)
        self.bus.write_byte_data(PCA9685_ADDR, base + 1, on_tick  >> 8)
        self.bus.write_byte_data(PCA9685_ADDR, base + 2, off_tick & 0xFF)
        self.bus.write_byte_data(PCA9685_ADDR, base + 3, off_tick >> 8)

    # ── Public API ────────────────────────────────────────────────────────────

    def move_servo(self, category: str, position: str):
        """Move a flap to 'active' or 'neutral' using its calibrated config.

        Args:
            category: "RECYCLING" or "COMPOST"
            position: "active" or "neutral"
        """
        cfg = FLAP[category]
        angle = cfg[position]
        ticks = self._angle_to_ticks(angle, cfg["min_pulse_us"], cfg["max_pulse_us"])
        self._set_channel(cfg["channel"], 0, ticks)
        self.current_position[category] = angle
        time.sleep(0.3)

    def reset_position(self):
        """Return ALL flaps to their neutral position."""
        for cat in FLAP:
            self.move_servo(cat, "neutral")

    def close(self):
        """Safe shutdown: neutralize flaps, then close I2C bus."""
        try:
            self.reset_position()
        except Exception:
            pass
        try:
            self.bus.close()
        except Exception:
            pass

    # ── Info ──────────────────────────────────────────────────────────────────

    def print_config(self):
        """Print flap configuration summary to console."""
        print("\n  Flap config:")
        for cat, cfg in FLAP.items():
            print(f"    {cat:<10}  ch{cfg['channel']:2d}  "
                  f"neutral={cfg['neutral']}°  active={cfg['active']}°  "
                  f"pulse={cfg['min_pulse_us']}–{cfg['max_pulse_us']} µs")
