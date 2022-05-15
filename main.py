"""
Tahzib Yafi
"""

# Libraries for PyQt5 and MQTT client
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import user_ui
from PyQt5.QtWidgets import QMessageBox
import paho.mqtt.client as mqtt
import time

# Broker to be used
mqttBroker = "broker.hivemq.com"

class MainWindow(QtWidgets.QMainWindow, user_ui.Ui_MainWindow):
    """UI Window class"""
    
    def __init__(self):
        """Initialize the window class"""
        super(MainWindow, self).__init__()
        self.client = mqtt.Client("Tahzib pc")
        self.client.connect(mqttBroker)
        self.setupUi(self)
        
        # Call the 2 subscription functions every 5ms
        self.timer_temp = QtCore.QTimer()
        self.timer_temp.timeout.connect(self.update_temp)
        self.timer_temp.start(5)
        
        self.timer_parking = QtCore.QTimer()
        self.timer_parking.timeout.connect(self.update_parking)
        self.timer_parking.start(5)
        
        # Pushbutton_1 sends PA's message, pushbutton_2 activates warning and pushbutton_3 removes warning
        self.pushButton_1.clicked.connect(self.send_PAmsg)
        self.pushButton_2.clicked.connect(self.raise_warning)
        self.pushButton_3.clicked.connect(self.remove_warning)
        
    def send_PAmsg(self):
        """
        Send out whatever is written in the textbox for PA
        """
        self.client.publish("TAY642_PAmessage",self.plainTextEdit.toPlainText())

    def setParkingState(self, textbrowser, occupied):
        """
        Change the parking state text browser to RED if it is occupied, GREEN otherwise
        """
        if occupied:
            textbrowser.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
        else:
            textbrowser.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")
        
    def raise_warning(self):
        """
        Display 'warning on' in the GUI and publish a 1
        """
        self.plainTextEdit_2.setPlainText("WARNING ON!!")
        self.plainTextEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.client.publish("TAY642_warningLight", 1)
        time.sleep(0.1)
        
    def remove_warning(self):
        """
        Display 'warning off' in the GUI and publish a 0
        """
        self.plainTextEdit_2.setPlainText("WARNING OFF")
        self.plainTextEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.client.publish("TAY642_warningLight", 0)
        time.sleep(0.1)
        
    def on_message(self, client, userdata, message):
        """
        Check the topic of the received message and take action accordingly
        """

        # Display the temperature on the GUI
        if message.topic=="TAY642_temperature":
            global temp
            temp = message.payload.decode("utf-8")

            try:
                val = float(temp)
                self.lcdNumber.display(val)
            except ValueError:
                print("error: Not a number")
            
        # Indicate which of the 5 parking lots are empty or full
        if message.topic=="TAY642_parkingState":
            global parked_cars
            parked_cars = message.payload.decode("utf-8")
            parkingState = parked_cars.split(",")
        
            self.setParkingState(self.textBrowser_1,int(parkingState[0]))
            self.setParkingState(self.textBrowser_2,int(parkingState[1]))
            self.setParkingState(self.textBrowser_3,int(parkingState[2]))
            self.setParkingState(self.textBrowser_4,int(parkingState[3]))
            self.setParkingState(self.textBrowser_5,int(parkingState[4]))
     
                
    def update_temp(self):
        # Subscribe to receive temperature
        self.client.subscribe("TAY642_temperature")
        self.client.on_message = self.on_message
        self.client.loop(1)
        
    def update_parking(self):
        # Subscribe to receive the parking state
        self.client.subscribe("TAY642_parkingState")
        self.client.on_message = self.on_message
        self.client.loop(1)
        
            
    def exit_func(self):
        exit()
        
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
