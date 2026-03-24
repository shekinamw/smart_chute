"""
utils/logger.py — Bin-level logging and console status display
===============================================================
Handles full-bin alerts (appended to bin_levels.txt) and
formatted console output for bin status bars.
"""

import os
from datetime import datetime

from config import LOG_DIR, BIN_LEVEL_LOG


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_bin_full(bin_name: str, distance_cm: float, fill_pct: float):
    """Append a full-bin alert to bin_levels.txt."""
    _ensure_log_dir()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"[{ts}]  BIN FULL: {bin_name:<10}  "
        f"distance={distance_cm:.1f}cm  fill={fill_pct:.1f}%\n"
    )
    with open(BIN_LEVEL_LOG, "a") as f:
        f.write(line)
    print(f"  [BIN LOG] {line.strip()}")


def log_bin_status(bin_name: str, distance_cm, fill_pct):
    """Print bin level bar to console (not written to file unless full)."""
    if distance_cm is None:
        print(f"  [BIN] {bin_name:<10}  sensor error / no reading")
        return
    bar_w = 20
    filled = round((fill_pct / 100.0) * bar_w)
    bar = "█" * filled + "░" * (bar_w - filled)
    status = "FULL" if fill_pct >= 90 else ("HIGH" if fill_pct >= 70 else "OK  ")
    print(f"  [BIN] {bin_name:<10}  {distance_cm:5.1f}cm  [{bar}] {fill_pct:5.1f}%  {status}")


def write_session_header(active_sensors: list, bin_height: float,
                         full_at: float, settle_delay: float, ir_debounce: float):
    """Write session start block to bin_levels.txt."""
    _ensure_log_dir()
    with open(BIN_LEVEL_LOG, "a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"SESSION START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Bin height: {bin_height}cm  Full threshold: {full_at}cm\n")
        f.write(f"Active sensors: {active_sensors}\n")
        f.write(f"Settle delay: {settle_delay}s  IR debounce: {ir_debounce * 1000:.0f}ms\n")
        f.write(f"{'=' * 60}\n")


def write_session_footer(bag_count: int, category_counts: dict):
    """Write session end block to bin_levels.txt."""
    _ensure_log_dir()
    try:
        with open(BIN_LEVEL_LOG, "a") as f:
            f.write(f"\nSESSION END: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"Total bags: {bag_count}  "
                f"RECYCLING={category_counts.get('RECYCLING', 0)}  "
                f"COMPOST={category_counts.get('COMPOST', 0)}  "
                f"GARBAGE={category_counts.get('GARBAGE', 0)}  "
                f"UNKNOWN={category_counts.get('UNKNOWN', 0)}\n"
            )
    except Exception:
        pass
