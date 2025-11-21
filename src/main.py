# main.py
import time
import cv2
import numpy as np
from picamera2 import Picamera2 # Use this library for Pi 5 CSI Camera

from sensor import setup_sensor, wait_for_bag, cleanup
from classify_bag import classify_bag 


def main():
    setup_sensor()
    
    # --- Initialize Picamera2 ---
    picam2 = Picamera2()
    
    # Configure the camera for fast capture (still configuration)
    config = picam2.create_still_configuration(main={"size": (1456, 1088)})
    picam2.configure(config)
    picam2.start()
    
    # Allow camera sensor to stabilize its exposure
    time.sleep(2) 
    
    print("System ready. Press CTRL+C to stop.\n")

    try:
        while True:
            # 1. Wait until IR sensor detects the bag
            wait_for_bag()

            # 2. Capture image 
            # Capture frame as a NumPy array (monochrome data duplicated across 3 channels)
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


#Color detection code commented 
# # main.py
# import cv2
# import time
# from sensor import setup_sensor, wait_for_bag, cleanup
# from detect_color import classify_color

# def main():
#     setup_sensor()

#     # Use USB cam → 0
#     # Use Pi camera (libcamera driver) → try 0 or /dev/video0
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Camera error: cannot open video stream")
#         cleanup()
#         return

#     print("System ready. Press CTRL+C to stop.\n")

#     try:
#         while True:
#             # Wait until IR sensor detects the bag
#             wait_for_bag()

#             # Capture image
#             ret, frame = cap.read()
#             if not ret:
#                 print("❌ Failed to capture frame")
#                 continue

#             # Classify bag color
#             label = classify_color(frame)

#             print("\n==============================")
#             print(f"  Detected Bag Type: {label.upper()}")
#             print("==============================\n")

#             time.sleep(1)

#     except KeyboardInterrupt:
#         print("Shutting down...")

#     finally:
#         cap.release()
#         cleanup()


# if __name__ == "__main__":
#     main()
