# main.py (Simplified - Camera and Sensor Only)
import time
# RPi.GPIO is no longer imported here, as it's handled by sensor.py
from picamera2 import Picamera2 

# Ensure these files and functions exist in your directory:
from sensor import setup_sensor, wait_for_bag, cleanup
from classify_bag import classify_bag 
from sort_simulation import perform_sorting_simulation 
# Note: You must ensure classify_bag.py still works reliably under your ambient light!

def main():
    # 1. Setup IR Sensor (Assumes BCM 23 and sets GPIO.setmode(BCM))
    setup_sensor() 
    
    # 2. Initialize Picamera2
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (2304, 1296)})
    picam2.configure(config)
    picam2.start()
    
    # Allow camera sensor to stabilize
    time.sleep(2) 
    
    print("System ready. Press CTRL+C to stop.\n")

    try:
        while True:
            # 3. Wait until IR sensor detects the bag (BCM 23)
            wait_for_bag()

            # --- LED CONTROL LOGIC REMOVED ---

            # 4. Capture color image 
            # Note: The camera's auto-exposure will handle the lighting.
            frame_array = picam2.capture_array()
            
            # 5. Classify bag color
            label = classify_bag(frame_array)

            print("\n==============================")
            print(f"  Detected Bag Type: {label.upper()}")
            print("==============================")
            
            # 6. Perform Simulated Sorting Action
            perform_sorting_simulation(label)

            # Wait for the bag to clear before looping
            time.sleep(1.5) 

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        picam2.stop()
        cleanup()


if __name__ == "__main__":
    main()