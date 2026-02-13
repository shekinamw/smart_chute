"""IR Sensor - handles bag detection."""

import RPi.GPIO as GPIO
import time

IR_PIN_DEFAULT = 23

class IRSensor:
    """Detects bags using IR breakbeam sensor."""

    def __init__(self, pin=IR_PIN_DEFAULT):
        self.pin = pin
        GPIO.setwarnings(False)
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_clear(self):
        """Check if beam is clear."""
        return GPIO.input(self.pin) == GPIO.HIGH

    def is_broken(self):
        """Check if beam is broken (bag detected)."""
        return GPIO.input(self.pin) == GPIO.LOW

    def wait_for_bag(self, debounce_ms=80):
        """Wait until bag is detected."""
        while self.is_clear():
            time.sleep(0.01)

        # Debounce
        time.sleep(debounce_ms / 1000.0)
        return True

    def cleanup(self):
        """Clean up GPIO."""
        try:
            GPIO.cleanup(self.pin)
        except:
            pass