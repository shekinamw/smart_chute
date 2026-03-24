"""
processing/classifier.py — HSV Bag Color Classifier
=====================================================
Classifies BGR frames by HSV pixel coverage.
"""

import cv2
import numpy as np

from config import HSV_RANGES, COVERAGE_THRESHOLD


class HSVBagClassifier:
    """Classify waste bags by dominant HSV color coverage."""

    CATEGORIES = list(HSV_RANGES.keys())   # ["RECYCLING", "COMPOST", "GARBAGE"]

    def __init__(
        self,
        hsv_ranges: dict | None = None,
        coverage_threshold: float = COVERAGE_THRESHOLD,
    ):
        self.hsv_ranges = hsv_ranges or HSV_RANGES
        self.coverage_threshold = coverage_threshold

    def classify_hsv(self, frame_bgr: np.ndarray) -> dict:
        """Classify a single BGR frame by HSV coverage.

        Returns:
            {"category": str, "coverage": float, "scores": dict}
        """
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        total = hsv.shape[0] * hsv.shape[1]

        scores = {}
        for cat, ranges in self.hsv_ranges.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lo, hi in ranges:
                mask |= cv2.inRange(hsv, np.array(lo), np.array(hi))
            scores[cat] = np.count_nonzero(mask) / total

        best = max(scores, key=scores.get)
        best_pct = scores[best]

        if best_pct < self.coverage_threshold:
            return {"category": "UNKNOWN", "coverage": best_pct, "scores": scores}

        return {"category": best, "coverage": best_pct, "scores": scores}

    def classify_burst(
        self, burst_frames: list[tuple[np.ndarray, float]]
    ) -> dict:
        """Classify a burst of (frame_bgr, timestamp) tuples.

        Picks the frame with the highest coverage as the "best" frame.

        Returns:
            {"category": str, "coverage": float, "best_idx": int,
             "frame_results": list[tuple[str, float, float]]}
        """
        best_category = "UNKNOWN"
        best_coverage = 0.0
        best_idx = 0
        frame_results = []

        for i, (frame_bgr, t_cap) in enumerate(burst_frames):
            result = self.classify_hsv(frame_bgr)
            cat = result["category"]
            cov = result["coverage"]
            frame_results.append((cat, cov, t_cap))
            if cov > best_coverage:
                best_category = cat
                best_coverage = cov
                best_idx = i

        return {
            "category": best_category,
            "coverage": best_coverage,
            "best_idx": best_idx,
            "frame_results": frame_results,
        }
