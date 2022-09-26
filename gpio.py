import RPi.GPIO as GPIO
import time


def gpio_power_on():
    power_key = list(range(1-40))
    print('SIM7600X power on:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(1)
    print('SIM7600X is starting up')


def gpio_power_off():
    power_key = list(range(1-40))
    print('SIM7600X power off ')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(2)
