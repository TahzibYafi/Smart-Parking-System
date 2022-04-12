from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import user_ui
from PyQt5.QtWidgets import QMessageBox
import paho.mqtt.client as mqtt
import time

mqttBroker = "broker.hivemq.com"

class MainWindow(QtWidgets.QMainWindow, user_ui.Ui_MainWindow):
    """UI Window class"""
    
    def __init__(self):
        """Initialize the window class"""
        super(MainWindow, self).__init__()
        self.client = mqtt.Client("Tahzib pc")
        self.client.connect(mqttBroker)
        self.setupUi(self)
        
        # Call the 2 subscription functions in the background
        self.timer_temp = QtCore.QTimer()
        self.timer_temp.timeout.connect(self.update_temp)
        self.timer_temp.start(5)
        
        self.timer_parking = QtCore.QTimer()
        self.timer_parking.timeout.connect(self.update_parking)
        self.timer_parking.start(5)
        
        # Pushbutton 1 sends message of PA, pushbutton 2 activates warning and pushbutton 3 removes warning
        self.pushButton_1.clicked.connect(self.send_PAmsg)
        self.pushButton_2.clicked.connect(self.raise_warning)
        self.pushButton_3.clicked.connect(self.remove_warning)
        
    def send_PAmsg(self):
        """
        Send out whatever is written in the textbox for PA
        """
        self.client.publish("TAY642_PAmessage",self.plainTextEdit.toPlainText())
        
    def raise_warning(self):
        """
        Display warning on in the GUI and publish it
        """
        self.plainTextEdit_2.setPlainText("WARNING ON!!")
        self.plainTextEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.client.publish("TAY642_warningLight", 1)
        time.sleep(0.1)
        
    def remove_warning(self):
        """
        Display warning off in the GUI and publish it
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
            
        # Indicate which of the 5 parking lots are empty or full, GREEN = empty and RED = full
        if message.topic=="TAY642_parkingState":
            global parked_cars
            parked_cars = message.payload.decode("utf-8")
            parkingState = parked_cars.split(",")
        
            if(int(parkingState[0])):
                self.textBrowser_1.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
            else:
                self.textBrowser_1.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")

            if(int(parkingState[1])):
                self.textBrowser_2.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
            else:
                self.textBrowser_2.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")

            if(int(parkingState[2])):
                self.textBrowser_3.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
            else:
                self.textBrowser_3.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")

            if(int(parkingState[3])):
                self.textBrowser_4.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
            else:
                self.textBrowser_4.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")    

            if(int(parkingState[4])):
                self.textBrowser_5.setStyleSheet("background-color: rgb(239, 41, 41);border-radius: 20px;")
            else:
                self.textBrowser_5.setStyleSheet("background-color: rgb(17, 166, 48);border-radius: 20px;")   
     
                
    def update_temp(self):
        # Start the subscription loop for temperatre
        self.client.subscribe("TAY642_temperature")
        self.client.on_message = self.on_message
        self.client.loop(1)
        
    def update_parking(self):
         # Start the subscription loop for parking state
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