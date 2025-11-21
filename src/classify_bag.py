# classify_bag.py (Renamed from detect_color.py)
import cv2
import numpy as np

def classify_bag(frame):
    """
    Analyzes the frame (from the MONOCHROME camera) using brightness and contrast
    to classify the bag.
    
    Returns: 'garbage', 'recycling', 'compost', or 'unknown'
    """
    
    # Check if the frame is 3-channel (color/BGR) or 1-channel (grayscale)
    if len(frame.shape) == 3:
        # Convert to Grayscale if it's a 3-channel image 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    else:
        # Already grayscale
        gray = frame 

    # Focus on a central region of interest (ROI) to analyze the bag itself
    h, w = gray.shape
    # Use 50% of the center area (from 25% to 75% for both height and width)
    roi = gray[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]
    
    # Calculate simple metrics: Average Brightness and Standard Deviation (Contrast)
    avg_brightness = np.mean(roi)
    contrast_std_dev = np.std(roi)
    
    # Print metrics for CALIBRATION (CRITICAL STEP)
    print(f"Analysis: Avg Brightness={avg_brightness:.2f}, Contrast StdDev={contrast_std_dev:.2f}")

    # --- MONOCHROME CLASSIFICATION LOGIC (DUMMY VALUES) ---
    # REPLACE THESE THRESHOLDS with values measured from your bags.

    # 1. BLACK BAGS (Garbage) - should have the lowest brightness
    if avg_brightness < 50 and contrast_std_dev < 20: 
        return "garbage"  
    
    # 2. COMPOST (Green Bag) - Example: Brighter than Black, but low contrast
    if avg_brightness > 50 and contrast_std_dev < 30:
        return "compost"
    
    # 3. RECYCLING (Blue Bag) - Example: Brighter than Black, potentially higher contrast (shinier)
    if avg_brightness > 50 and contrast_std_dev >= 30:
        return "recycling"

    return "unknown"