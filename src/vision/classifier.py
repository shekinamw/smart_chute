"""Classifier - determines bag color and category."""

import cv2
import numpy as np

class HSVBagClassifier:
    """Classifies bags by color using HSV."""

    def __init__(self):
        # HSV color ranges
        self.hsv_ranges = {
            "blue": {
                "lower": np.array([15, 50, 170]),
                "upper": np.array([50, 255, 255]),
            },
            "green": {
                "lower": np.array([51, 40, 120]),
                "upper": np.array([90, 255, 255]),
            },
            "black": {
                "lower": np.array([0, 0, 0]),
                "upper": np.array([179, 255, 100]),
            },
        }

        # Color to category mapping
        self.categories = {
            "black": "GARBAGE",
            "blue": "RECYCLING",
            "green": "COMPOST",
        }

    def classify_hsv(self, hsv_image):
        """Classify bag color from HSV image."""
        # Use center region
        h, w = hsv_image.shape[:2]
        roi = hsv_image[h//4 : 3*h//4, w//4 : 3*w//4]

        # Calculate average HSV
        avg_h, avg_s, avg_v = np.mean(roi, axis=(0, 1))

        # Check each color
        color_matches = {}
        for color_name, r in self.hsv_ranges.items():
            mask = cv2.inRange(roi, r["lower"], r["upper"])
            match_pct = (np.sum(mask > 0) / mask.size) * 100.0
            color_matches[color_name] = match_pct

        # Decide color
        if color_matches["blue"] > 30:
            color = "blue"
            confidence = min(95.0, color_matches["blue"])
        elif avg_v < 120:
            color = "black"
            confidence = (120.0 - avg_v) / 120.0 * 100.0
        elif color_matches["green"] > 20:
            color = "green"
            confidence = min(95.0, color_matches["green"])
        else:
            color = max(color_matches, key=color_matches.get)
            confidence = color_matches[color]

        category = self.categories[color]

        return {
            "color": color,
            "category": category,
            "confidence": float(confidence),
            "hsv": {"h": float(avg_h), "s": float(avg_s), "v": float(avg_v)},
        }