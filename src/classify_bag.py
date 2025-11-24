# classify_bag.py (Updated for Color Camera)
import cv2
import numpy as np

# --- HSV Color Ranges for Bag Classification ---
COLOR_RANGES = [
    {
        'name': 'Blue (H: 19.1)', # Note: This is an unusual H value for Blue.
        'lower': np.array([0, 67, 167]),
        'upper': np.array([20, 167, 255]),
        'color_bgr': (255, 0, 0) # BGR color for drawing the box
    },
    {
        'name': 'Black (V: 125)', # Note: This V value (125) is dim grey, not true black.
        'lower': np.array([6, 26, 75]),
        'upper': np.array([26, 126, 175]),
        'color_bgr': (0, 0, 0) 
    },
    {
        'name': 'Green (H: 35.4)', # Note: This is an unusual H value for Green.
        'lower': np.array([8, 173, 164]),
        'upper': np.array([28, 255, 255]),
        'color_bgr': (0, 255, 0)
    }
]

def classify_color(frame):
    """
    Analyzes the frame to classify the bag.
    
    Returns: 'garbage', 'recycling', 'compost', or 'unknown'
    """
    # 1. Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2. Iterate through color definitions
    for label, ranges in COLOR_RANGES.items():
        mask_total = None

        for (lower, upper) in ranges:
            mask = cv2.inRange(hsv, lower, upper)
            # Use addition (+) for masks (equivalent to bitwise_or)
            mask_total = mask if mask_total is None else mask_total + mask

        # Count the number of pixels within the color range
        coverage = cv2.countNonZero(mask_total)

        # --- 3. CRITICAL FIX: HIGH PIXEL COVERAGE THRESHOLD ---
        # A bag should cover a large portion of the 2304x1296 frame. 
        # Set to 30,000 pixels to eliminate background/shadow noise.
        if coverage > 30000:
             return label

    return "unknown"