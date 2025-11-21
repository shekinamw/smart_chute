# sensor.py
import RPi.GPIO as GPIO
import time

IR_PIN = 17  # GPIO connected to ADA2167 OUT pin

def setup_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("IR sensor ready.")

def wait_for_bag():
    """
    Blocks until the IR beam is broken (bag passes).
    """
    print("Waiting for bag...")

    # Sensor OUT pin is HIGH normally
    # Goes LOW when beam is broken
    while True:
        if GPIO.input(IR_PIN) == GPIO.LOW:
            print("Beam broken — bag detected!")
            time.sleep(0.3)  # Debounce
            return True
        time.sleep(0.01)

def cleanup():
    GPIO.cleanup()
