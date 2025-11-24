# classify_bag.py (Updated for Color Camera)
import cv2
import numpy as np

# --- HSV Color Ranges for Bag Classification ---
# These are general ranges for typical green, blue, and black plastic.
# They are more reliable than the mono thresholds but still benefit from testing!
COLOR_RANGES = {
    "garbage": [  # BLACK: Low Value (V) = dark
        (np.array([0, 0, 0]), np.array([180, 255, 60]))
    ],
    "recycling": [  # BLUE: Hue around 100-140
        (np.array([95, 80, 50]), np.array([135, 255, 255]))
    ],
    "compost": [  # GREEN: Hue around 30-90
        (np.array([30, 40, 40]), np.array([85, 255, 255]))
    ]
}

def classify_bag(frame):
    """
    Analyzes the frame (from the COLOR camera) using HSV color thresholding
    to classify the bag into garbage (black), recycling (blue), or compost (green).
    
    Returns: 'garbage', 'recycling', 'compost', or 'unknown'
    """
    
    # 1. Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2. Iterate through color definitions and check for coverage
    for label, ranges in COLOR_RANGES.items():
        mask_total = None

        for (lower, upper) in ranges:
            mask = cv2.inRange(hsv, lower, upper)
            mask_total = mask if mask_total is None else cv2.bitwise_or(mask_total, mask)

        # Count the number of pixels within the color range
        coverage = cv2.countNonZero(mask_total)

        # Threshold check: If the color covers a large enough area (5000 pixels, adjust based on distance)
        # and it's not the black bag (which can be tricky due to shadows), return the label.
        if label != "garbage" and coverage > 5000:
             # For Green and Blue, coverage is the best metric
             return label
        
        if label == "garbage" and coverage > 20000:
             # For black (low V), we need a larger pixel count to be sure it's the bag and not shadows
             return label


    return "unknown"