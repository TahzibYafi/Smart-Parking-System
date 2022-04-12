import paho.mqtt.client as mqtt
import time

import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO

sensor = BMP085.BMP085()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
parked_cars = (29,31,37,16,18)
GPIO.setup(parked_cars, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Connect the client to a public broker
mqttBroker = "broker.hivemq.com"
client = mqtt.Client("Tahzib rasp")
client.connect(mqttBroker)

# Indicates if the warning is on or off
global warning
warning  = ""

# Publishes temperature
def send_temp():
    """
    Read temperature from sensor and publish it to the broker
    """
    temperature = sensor.read_temperature()   
    client.publish("TAY642_temperature", temperature)  
    time.sleep(0.1)

# Publishes parking state
def send_parking_state():
    """
    Read the state of parking lot from the raspberry pi and publish it to the broker
    """
    car1 = GPIO.input(29)
    car2 = GPIO.input(31)
    car3 = GPIO.input(37)
    car4 = GPIO.input(16)
    car5 = GPIO.input(18)
    parking_state = str(car1) + "," + str(car2) + "," + str(car3) + "," + str(car4) + "," + str(car5)
    client.publish("TAY642_parkingState", parking_state)
    time.sleep(0.1)

#Callback function for subscribing messages
def on_message(client, userdata, message):
    """
    Check the topic of the received message and take action accordingly
    """

    # Indicate if the warning is on or off
    if message.topic=="TAY642_warningLight":
        global warning_msg, warning
        warning_msg = int(message.payload.decode("utf-8"))
        if warning_msg:
            warning = 1
        else:
            warning = 0

    # Print the PA message in raspberry console
    if message.topic=="TAY642_PAmessage":
        global park_msg
        park_msg = message.payload.decode("utf-8")
        print(park_msg)

    
if __name__ == "__main__":
    
    client.subscribe("TAY642_PAmessage")
    client.subscribe("TAY642_warningLight")
    client.on_message = on_message
    client.loop_start()     # Start subscription loop
    
    while True:
        # Keep publishing messages
        send_temp()
        send_parking_state()
        
        # Flash the LED if warning is on, keep it off if warning is off
        if warning == 1:
            GPIO.output(12, True)
            time.sleep(0.5)
            GPIO.output(12, False)
            time.sleep(0.5)
        elif warning == 0:
            GPIO.output(12, False)
