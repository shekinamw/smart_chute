# main.py (Updated for Camera Module 3)
import time
import cv2
import numpy as np
from picamera2 import Picamera2 # Use this library for Pi 5 CSI Camera

from sensor import setup_sensor, wait_for_bag, cleanup
from classify_bag import classify_bag # Now imports the COLOR logic


def main():
    setup_sensor()
    
    # --- Initialize Picamera2 ---
    picam2 = Picamera2()
    
    # Configure the camera for the IMX708 sensor (12MP)
    # Using a 2304x1296 resolution for good detail while keeping processing manageable
    config = picam2.create_still_configuration(main={"size": (2304, 1296)})
    picam2.configure(config)
    picam2.start()
    
    # Allow camera sensor to stabilize its exposure
    time.sleep(2) 
    
    print("System ready. Press CTRL+C to stop.\n")

    try:
        while True:
            # 1. Wait until IR sensor detects the bag
            wait_for_bag()

            # 2. Capture color image 
            # Capture frame as a NumPy array (BGR format for OpenCV)
            frame_array = picam2.capture_array()
            
            # 3. Classify bag color
            label = classify_bag(frame_array)

            print("\n==============================")
            print(f"  Detected Bag Type: {label.upper()}")
            # The sorting action (servo control) would go here
            print("==============================\n")
            
            # Wait for the bag to clear the chute before looping
            time.sleep(1.5) 

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        picam2.stop()
        cleanup()


if __name__ == "__main__":
    main()