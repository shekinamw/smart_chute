# main.py
import cv2
import time
from sensor import setup_sensor, wait_for_bag, cleanup
from detect_color import classify_color

def main():
    setup_sensor()

    # Use USB cam → 0
    # Use Pi camera (libcamera driver) → try 0 or /dev/video0
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera error: cannot open video stream")
        cleanup()
        return

    print("System ready. Press CTRL+C to stop.\n")

    try:
        while True:
            # Wait until IR sensor detects the bag
            wait_for_bag()

            # Capture image
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                continue

            # Classify bag color
            label = classify_color(frame)

            print("\n==============================")
            print(f"  Detected Bag Type: {label.upper()}")
            print("==============================\n")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        cap.release()
        cleanup()


if __name__ == "__main__":
    main()
