# sensor.py (FINAL VERSION - Corrected Pin 23)
import RPi.GPIO as GPIO
import time

IR_PIN = 23  # <--- FIXED: GPIO connected to ADA2167 OUT pin (BCM 23)

def setup_sensor():
    # Set mode to BCM (Broadcom chip numbering)
    # Using GPIO.setwarnings(False) to prevent 'mode already set' warnings
    GPIO.setwarnings(False) 
    
    # Check if the mode is already set before setting it
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    
    # Set pin 23 as input with internal pull-up resistor enabled
    # The logic is correct: pull_up=True, check for LOW signal.
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("IR sensor ready.")

def wait_for_bag():
    """
    Blocks until the IR beam is broken (bag passes).
    """
    print("Waiting for bag...")

    # Sensor OUT pin is HIGH normally (due to PUD_UP)
    # Goes LOW when beam is broken (confirmed by gpiozero test)
    while True:
        if GPIO.input(IR_PIN) == GPIO.LOW: # This condition is correct
            print("Beam broken — bag detected!")
            # Debounce time is set to 0.3s (from your snippet)
            time.sleep(0.3)  
            return True
        time.sleep(0.01)

def cleanup():
    # It's important to keep this for a clean exit
    GPIO.cleanup()