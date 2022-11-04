#!/usr/bin/python
import spidev
import time
import os
import RPi.GPIO as GPIO
import pio
import Ports

pio.uart = Ports.UART()  # Define serial port

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Open SPI bus

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E = 11
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 15
LCD_D7 = 16
En = 26
Motor_1 = 29
Motor_2 = 31
Pusher_1 = 38
Pusher_2 = 40
Green_LED = 37
'''
define pin for lcd
'''
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
delay = 1

GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT)  # RS
GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
GPIO.setup(LCD_D7, GPIO.OUT)  # DB7
GPIO.setup(En, GPIO.OUT)  # MOTOR En
GPIO.setup(Motor_1, GPIO.OUT)  # Motor_1
GPIO.setup(Motor_2, GPIO.OUT)  # Motor_1
GPIO.setup(Pusher_1, GPIO.OUT, initial=GPIO.HIGH)  # Pusher
# GPIO.setup(Pusher_2, GPIO.OUT, initial = GPIO.LOW)# Pusher
GPIO.setup(Green_LED, GPIO.OUT)  # Green LED
# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# PWM
pwm = GPIO.PWM(En, 100)
pwm.start(0)
'''
Function Name :lcd_init()
Function Description : this function is used to initialized lcd by sending the different commands
'''


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


'''
Function Name :lcd_byte(bits ,mode)
Fuction Name :the main purpose of this function to convert the byte data into bit and send to lcd port
'''


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()


'''
Function Name : lcd_toggle_enable()
Function Description:basically this is used to toggle Enable pin
'''


def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)


'''
Function Name :lcd_string(message,line)
Function  Description :print the data on lcd 
'''


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


# Define delay between readings
delay = 5
lcd_init()
lcd_string("welcome ", LCD_LINE_1)
time.sleep(1)
lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
lcd_string("Waiting for data...", LCD_LINE_1)
while 1:
    # conveyor belt
    time.sleep(1)
    GPIO.output(Motor_1, GPIO.LOW)
    GPIO.output(Motor_2, GPIO.HIGH)
    pwm.ChangeDutyCycle(50)

    Data = pio.uart.recv()

    # pio.uart.print(Data)
    if (Data == "1"):
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        lcd_string(" Defect ", LCD_LINE_1)
        lcd_string(" Detected", LCD_LINE_2)

        time.sleep(2)

        # lcd_byte(0x01,LCD_CMD) # 000001 Clear display
        # lcd_string("Gate Open",LCD_LINE_2)
        '''GPIO.output(Motor_1, True)
        GPIO.output(Motor_2, False)
        time.sleep(1)
        GPIO.output(Motor_1, False)
        GPIO.output(Motor_2, True)
        time.sleep(1)
        GPIO.output(Motor_1, False)
        GPIO.output(Motor_2, False)
        time.sleep(1)'''
        # For pusher
        time.sleep(1)
        GPIO.output(Pusher_1, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(Pusher_1, GPIO.HIGH)
    elif (Data == '0'):
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        lcd_string(" NOT Defect", LCD_LINE_1)
        lcd_string(" Detected", LCD_LINE_2)
        # Green LED ON
        time.sleep(0.5)
        GPIO.output(Green_LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(Green_LED, GPIO.LOW)
    else:
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        lcd_string(" No Object", LCD_LINE_1)
        lcd_string(" Found ", LCD_LINE_2)
        time.sleep(0.5)