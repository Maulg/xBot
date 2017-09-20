#!/usr/bin/python

import os
import time
import random
import atexit
import threading
from TempSensorController import TempSensorController
import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

# Variables
speed = 150     #How fast?
turn = .9       #Inside wheel speed, small correction
rotate = .3     #Inside wheel speed, large correction,$
prevLine = 4    #Start going straight
waitCount = 0	#For obstacle logic
temp = 0
cookCount = 0	#For temp logic

# Create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# Create motor objects
rightMotor = mh.getMotor(1)
leftMotor = mh.getMotor(2)

# Recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)


# Infrared Sensors
GPIO.setmode(GPIO.BOARD)

leftPin = 35    # Connected to GPIO 19 pin 35
centerPin = 38  # Connected to GPIO 20 on pin 38
rightPin = 40   # Connected to GPIO 21 on pin 40

GPIO.setup(rightPin, GPIO.IN)
GPIO.setup(centerPin, GPIO.IN)
GPIO.setup(leftPin, GPIO.IN)

# Set pin mode to output
GPIO.setup(33, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
# Set pins to high(3.3V) to turn OFF led
GPIO.output(33, GPIO.HIGH)
GPIO.output(32, GPIO.HIGH)
GPIO.output(31, GPIO.HIGH)
# Set duty cycle
rPin = GPIO.PWM(32, 2000)
gPin = GPIO.PWM(31, 2000)
bPin = GPIO.PWM(33, 5000)

# Initial duty cycle 0 = OFF
rPin.start(0)
gPin.start(0)
bPin.start(0)

def setRGB(red, green, blue): # values may 0-100
    rPin.start(red)
    gPin.start(green)
    bPin.start(blue)

obstaclePin = 29
GPIO.setup(obstaclePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# IR LED config
irPin = 36    # pin 36

GPIO.setmode(GPIO.BOARD)      # Numbers GPIOs by physical location
GPIO.setup(irPin, GPIO.OUT)   # Set irPin's mode is output
GPIO.output(irPin, GPIO.HIGH) # Set irPin high(+3.3V) to off led

def irPulse():
    print '...led on'
    GPIO.output(irPin, GPIO.HIGH)  # led on
    time.sleep(0.15)
    print 'led off...'
    GPIO.output(irPin, GPIO.LOW) # led off
    time.sleep(0.15)

## Sound active buzzer

buzzerPin = 11 # GPIO 17
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.output(buzzerPin, GPIO.LOW)

def buzzer(switch):
    switch = switch
    if switch == 0:
        GPIO.output(buzzerPin, GPIO.LOW)
    if switch == 1:
        GPIO.output(buzzerPin, GPIO.HIGH)

# IR sensor states
def irState():
    position = (GPIO.input(leftPin) * 1) + (GPIO.input(centerPin) * 2) + (GPIO.input(rightPin) * 4)
    return position
    # 0 = all off, 1 = left sensor on, 2 = center sensor on, 3 = left and center sensor  on,
    # 4 = right sensor on, 5 = right and left sensor on, 6 = right and center sensors on, 7 all on

# Temp
tempcontrol = TempSensorController("28-01162e5364ee",1)
tempcontrol.start()

# Here is the script

try:
    while True:
        line = irState()
        temp = tempcontrol.temperature.C

        if temp > 28 and cookCount == 1:
            print ("I am melting!")
            print temp

        if temp < 28 and cookCount == 1:
            print ("Ready for the Oven")
            print temp
            cookCount = 0

        if temp > 28 and cookCount == 0:
            print ("Simmering at")
            print temp
            leftMotor.run(Adafruit_MotorHAT.RELEASE)
            rightMotor.run(Adafruit_MotorHAT.RELEASE)
            setRGB(0,0,100)
            time.sleep(10)
            cookCount = 1

        if GPIO.input(obstaclePin) == 1 and waitCount==1:
            print("Stop making noise")
            buzzer(0)
            waitCount = 0

        if GPIO.input(obstaclePin) == 0 and waitCount == 0:
            leftMotor.run(Adafruit_MotorHAT.RELEASE)
            rightMotor.run(Adafruit_MotorHAT.RELEASE)
            setRGB(100,0,0)
            print ("Obstacle detected!!!")
            time.sleep(5)
            print ("Look again")
            waitCount = 1

        if GPIO.input(obstaclePin) == 0 and waitCount == 1:
            leftMotor.run(Adafruit_MotorHAT.RELEASE)
            rightMotor.run(Adafruit_MotorHAT.RELEASE)
            setRGB(100,0,0)
            print("Make some noise")
            buzzer(1)
            print("Pulse IR 5 times, at 150ms on/off")
            irPulse() # 1
            irPulse() # 2
            irPulse() # 3
            irPulse() # 4
            irPulse() # 5

        if line == 0:   # No line
            print("Lost line! Use previous data.")
            line = prevLine
            setRGB(0,100,0)

        if line == 5:   # 104 Line is far left and right of center
            print("Choose left or right")
            pickLR = [1, 4]
            line = random.choice(pickLR)
            setRGB(0,100,0)

        if line == 7:   # 124 Line is every where!
            print("Line is everywhere!")
            pickLCR = [3, 6]
#            pickLCR = [2, 3, 6]
            line = random.choice(pickLCR)
            setRGB(0,100,0)

        if line == 1:   # Line is far left
            print("Rotate left.")
            leftMotor.run(Adafruit_MotorHAT.FORWARD)
            rightMotor.run(Adafruit_MotorHAT.FORWARD)
            leftMotor.setSpeed(int(speed*rotate))
            rightMotor.setSpeed(int(speed*turn))
            prevLine = 1
            setRGB(0,100,0)

        if line == 2:   # Line is center
            print("Move forward. Accelerate")
            leftMotor.run(Adafruit_MotorHAT.FORWARD)
            rightMotor.run(Adafruit_MotorHAT.FORWARD)
            leftMotor.setSpeed(speed)
            rightMotor.setSpeed(speed)
            prevLine = 2
            setRGB(0,100,0)

        if line == 3:   # Line left, near center
            print("Turn left.")
            leftMotor.run(Adafruit_MotorHAT.FORWARD)
            rightMotor.run(Adafruit_MotorHAT.FORWARD)
            leftMotor.setSpeed(int(speed*turn))
            rightMotor.setSpeed(int(speed))
            prevLine = 3
            setRGB(0,100,0)

        if line == 4:   # Line is far right
            print("Rotate right.")
            leftMotor.run(Adafruit_MotorHAT.FORWARD)
            rightMotor.run(Adafruit_MotorHAT.FORWARD)
            leftMotor.setSpeed(int(speed*turn))
            rightMotor.setSpeed(int(speed*rotate))
            prevLine = 4
            setRGB(0,100,0)

        if line == 6:   # 024 Line is right near center
            print("Turn right.")
            leftMotor.run(Adafruit_MotorHAT.FORWARD)
            rightMotor.run(Adafruit_MotorHAT.FORWARD)
            leftMotor.setSpeed(int(speed))
            rightMotor.setSpeed(int(speed*turn))
            prevLine = 6
            setRGB(0,100,0)

except KeyboardInterrupt:
    tempcontrol.stopController()
    rPin.stop()
    gPin.stop()
    bPin.stop()
    GPIO.output(33, GPIO.HIGH)
    GPIO.output(32, GPIO.HIGH)
    GPIO.output(31, GPIO.HIGH)
    GPIO.cleanup()
