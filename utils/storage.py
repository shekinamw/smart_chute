"""
utils/storage.py — Burst Frame Storage Manager
================================================
Saves burst-captured frames and per-bag summary files.
"""

import os
from datetime import datetime

import cv2

from config import CAPTURE_DIR, LOG_DIR


class StorageManager:
    """Manages burst frame captures and sorting log files."""

    def __init__(
        self,
        capture_dir: str = CAPTURE_DIR,
        log_dir: str = LOG_DIR,
    ):
        self.capture_dir = capture_dir
        self.log_dir = log_dir
        os.makedirs(self.capture_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    # ── Capture paths ─────────────────────────────────────────────────────────

    def get_capture_path(self, bag_number: int) -> str:
        """Return (and create) the directory for a specific bag's captures."""
        bag_dir = os.path.join(self.capture_dir, f"bag_{bag_number:04d}")
        os.makedirs(bag_dir, exist_ok=True)
        return bag_dir

    # ── Burst frame saving ────────────────────────────────────────────────────

    def save_burst_frames(
        self,
        bag_number: int,
        burst_frames: list,
        frame_results: list,
        best_idx: int,
    ) -> str:
        """Save all burst-captured frames and a summary file.

        Output structure:
          data/captures/bag_0001/
            frame_0_+1012ms_GARBAGE_76.8pct.jpg
            frame_1_+1065ms_RECYCLING_22.5pct.jpg
            frame_2_+1118ms_RECYCLING_31.7pct_BEST.jpg
            summary.txt

        Returns:
            Path to the bag directory.
        """
        bag_dir = self.get_capture_path(bag_number)

        for i, (frame_bgr, t_cap) in enumerate(burst_frames):
            cat, cov, _ = frame_results[i]
            chosen = "_BEST" if i == best_idx else ""
            fname = (
                f"frame_{i}_{t_cap * 1000:+07.0f}ms"
                f"_{cat}_{cov * 100:.1f}pct{chosen}.jpg"
            )
            cv2.imwrite(os.path.join(bag_dir, fname), frame_bgr)

        # Summary text file
        best_cat, best_cov, best_time = frame_results[best_idx]
        summary_path = os.path.join(bag_dir, "summary.txt")
        ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(summary_path, "w") as f:
            f.write(f"Bag #{bag_number}  —  {ts_str}\n")
            f.write(f"{'=' * 55}\n")
            f.write(f"Decision: {best_cat}  ({best_cov * 100:.1f}% coverage)\n")
            f.write(f"Best frame: #{best_idx} at {best_time * 1000:.0f}ms\n\n")
            f.write(f"{'Frame':<8} {'Offset':<12} {'Category':<12} {'Coverage':<10} {'Note'}\n")
            f.write(f"{'-' * 55}\n")
            for i, (cat, cov, t_cap) in enumerate(frame_results):
                note = "◄ BEST" if i == best_idx else ""
                f.write(
                    f"{i:<8d} {t_cap * 1000:>+7.0f}ms    "
                    f"{cat:<12} {cov * 100:>6.1f}%    {note}\n"
                )

        return bag_dir

    # ── Sort log entry ────────────────────────────────────────────────────────

    def save_log_entry(self, category: str, coverage: float, elapsed: float):
        """Append one sorting event to today's sort log."""
        path = os.path.join(
            self.log_dir,
            f"sorting_log_{datetime.now().strftime('%Y%m%d')}.txt",
        )
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "a") as f:
            f.write(
                f"[{ts}]  category={category:<10}  "
                f"coverage={coverage * 100:5.1f}%  "
                f"time={elapsed:.2f}s\n"
            )
