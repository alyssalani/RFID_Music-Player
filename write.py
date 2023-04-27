#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        id = input('Song ID:')
        print("Now place your tag to write")
        reader.write(id)
        print("Written")
        
finally:
        GPIO.cleanup()
