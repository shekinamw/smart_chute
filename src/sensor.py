# sensor.py (Renamed from ir_sensor.py)
import RPi.GPIO as GPIO
import time

IR_PIN = 17  # GPIO connected to ADA2167 OUT pin

def setup_sensor():
    # Set mode to BCM (Broadcom chip numbering)
    GPIO.setmode(GPIO.BCM)
    # Set pin 17 as input with internal pull-up resistor enabled
    # This is critical for the open-collector output of the ADA2167
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("IR sensor ready.")

def wait_for_bag():
    """
    Blocks until the IR beam is broken (bag passes).
    """
    print("Waiting for bag...")

    # Sensor OUT pin is HIGH normally (due to PUD_UP)
    # Goes LOW when beam is broken
    while True:
        if GPIO.input(IR_PIN) == GPIO.LOW:
            print("Beam broken — bag detected!")
            # Increased debounce time for actual bag drop
            time.sleep(0.5) 
            return True
        time.sleep(0.01)

def cleanup():
    GPIO.cleanup()