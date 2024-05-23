import sys, platform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QDial,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QHBoxLayout
)
import serial
import time
import os
WINDOW_SIZE = 350
DISPLAY_HEIGHT = 35
BUTTON_SIZE = 40
ERROR_MSG = "ERROR"

os.environ['DISPLAY'] = ':0'


# -------------------- Camera Preview Code ---------------------------------------------------------
import time
from importlib.metadata import version



from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QLabel, QCheckBox,
                             QWidget, QTabWidget, QVBoxLayout, QGridLayout)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from picamera2 import __name__ as picamera2_name
from libcamera import controls
picam2 = Picamera2() 


preview_width= 1000
preview_height = int(picam2.sensor_resolution[1] * preview_width/picam2.sensor_resolution[0])
preview_config_raw = picam2.create_preview_configuration(main={"size": (preview_width, preview_height)},
                                                         raw={"size": picam2.sensor_resolution})
                                                         
picam2.configure(preview_config_raw)
picam2.set_controls({"ColourGains": (1.85, 1.85)}) #Tuple of two floating point numbers between 0.0 and 32.0.

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/usr/lib/python3/dist-packages/PyQt5'
# --------------------------------------------------------------------------------------------------

AF_Function = True
AF_Enable = True
try:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    print("Auto-Focus Function Enabled")
except RuntimeError as err:
    print("RuntimeError:", err)
    AF_Function = False
    



class ArduinoModel:
    """Model class representing the Arduino-related data and logic."""

    def __init__(self):
        self.led_state = False  # Initial state: LED is off
        self.rgb_led_color = None  # Initial state: RGB LED color is not selected
        self.servo_position = 0  # Initial state: Servo position is 0

    def toggle_led(self):
        self.led_state = not self.led_state

    def set_rgb_led_color(self, color):
        self.rgb_led_color = color

    def set_servo_position(self, position):
        self.servo_position = position

    def get_led_status(self):
        return self.led_state


class ArduinoController:
    """Controller class handling user input and updating the model."""

    def __init__(self, model):
        self.model = model
        self.serial_connection = serial.Serial('/dev/ttyACM0', 9600)

    def handle_led_button_click(self):
        self.model.toggle_led()
        led_data = f"{self.model.get_led_status()}\n"
        print(f"Toggle LED, message : {led_data}")
        self.send_serial_message(led_data)

    def handle_rgb_led_color_change(self, color):
        print(f"RGB LED Color : {color}")
        self.model.set_rgb_led_color(color)
        # Red = 1, Green = 2, Blue = 3
        color_data = None
        if (color == "Red"):
            color_data = f"RGB-1\n"
        elif (color == "Green"):
            color_data = f"RGB-2\n"
        else:
            color_data = f"RGB-3\n"
        print(f"Sending serial command : {color_data}")
        self.send_serial_message(color_data)

    def handle_servo_position_change(self, position):
        servo_data = f"SERVO-{position}\n"
        self.model.set_servo_position(position)
        print(f"Servo Position : {servo_data}")
        self.send_serial_message(servo_data)
        time.sleep(0.3)

    def send_serial_message(self, message):
        self.serial_connection.write(message.encode())


class PyControllerWindow(QMainWindow):
    """View class representing the user interface."""

    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Arduino Control")
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

        self.main_widget = MyMainWidget(self)

        self.controller = controller
        self._create_ui_display()

    def _create_ui_display(self):


        # Group Box for LED-related widgets
        led_group = QGroupBox("LED Control")
        led_layout = QVBoxLayout()

        led_label = QLabel("Turn On LED")
        led_button = QPushButton("Toggle LED")
        led_button.clicked.connect(self.controller.handle_led_button_click)

        led_layout.addWidget(led_label)
        led_layout.addWidget(led_button)

        led_group.setLayout(led_layout)
        self.layout.addWidget(led_group)

        # Create a button group for RGB LED
        radio_group = QGroupBox("RGB LED Control")
        radio_layout = QHBoxLayout()

        red = QRadioButton("Red", self)
        green = QRadioButton("Green", self)
        blue = QRadioButton("Blue", self)

        rgb_button_group = QButtonGroup(self)
        rgb_button_group.addButton(red)
        rgb_button_group.addButton(green)
        rgb_button_group.addButton(blue)
        rgb_button_group.buttonClicked.connect(self.handle_rgb_led_color_change)

        radio_layout.addWidget(red)
        radio_layout.addWidget(green)
        radio_layout.addWidget(blue)

        radio_group.setLayout(radio_layout)
        self.layout.addWidget(radio_group)

        # Group Box for Servo-related widgets
        servo_group = QGroupBox("Servo Control")
        servo_layout = QVBoxLayout()

        servo_label = QLabel("Set servo position")
        servo_dial = QDial()
        servo_dial.setMinimum(0)
        servo_dial.setMaximum(180)
        servo_dial.setNotchesVisible(True)
        servo_dial.setOrientation(Qt.Orientation.Horizontal)
        servo_dial.valueChanged.connect(self.handle_servo_position_change)

        servo_layout.addWidget(servo_label)
        servo_layout.addWidget(servo_dial)

        servo_group.setLayout(servo_layout)
        self.layout.addWidget(servo_group)

    def handle_rgb_led_color_change(self, button):
        color = button.text()
        self.controller.handle_rgb_led_color_change(color)

    def handle_servo_position_change(self, position):
        self.controller.handle_servo_position_change(position)


class MyMainWidget(QWidget):
    
    #--- MyPreviewWidget ---
    #inner class for Preview Window
    class MyPreviewWidget(QWidget):
        
        def __init__(self, subLayout):
            super(QWidget, self).__init__()
            self.setLayout(subLayout)
            
    #--- End of MyPreviewWidget ---
    
    def read_f(self, file):
        with open(file, encoding='UTF-8') as reader:
            content = reader.read()
        return content
    
    def read_pretty_name(self):
        with open("/etc/os-release", encoding='UTF-8') as f:
            os_release = {}
            for line in f:
                k,v = line.rstrip().split("=")
                os_release[k] = v.strip('"')
        return os_release['PRETTY_NAME']

    def AF_Enable_CheckBox_onStateChanged(self):
        if self.AF_Enable_CheckBox.isChecked():
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        else:
            picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})

    def on_Capture_Clicked(self):
        # There are two buttons on Main/Child Window connected here,
        # identify the sender for info only, no actual use.
        sender = self.sender()
        if sender is self.btnCapture:
            print("Capture button on Main Window clicked")
        if sender is self.btnChildCapture:
            print("Capture button on Child Preview Window clicked")

        self.btnCapture.setEnabled(False)
        
        cfg = picam2.create_still_configuration()
        
        timeStamp = time.strftime("%Y%m%d-%H%M%S")
        targetPath="/home/pi/Desktop/img_"+timeStamp+".jpg"
        print("- Capture image:", targetPath)
        
        picam2.switch_mode_and_capture_file(cfg, targetPath, signal_function=self.qpicamera2.signal_done)

    def capture_done(self, job):
        result = picam2.wait(job)
        self.btnCapture.setEnabled(True)
        print("- capture_done.")
        print(result)
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        
        #--- Prepare child Preview Window ----------
        self.childPreviewLayout = QVBoxLayout()
        
        # Check Auto-Focus feature
        # if AF_Function:
        #     self.AF_Enable_CheckBox = QCheckBox("Auto-Focus (Continuous)")
        #     self.AF_Enable_CheckBox.setChecked(True)
        #     self.AF_Enable_CheckBox.setEnabled(True)
        #     self.AF_Enable_CheckBox.stateChanged.connect(self.AF_Enable_CheckBox_onStateChanged)
        #     self.childPreviewLayout.addWidget(self.AF_Enable_CheckBox)
        #     print("show Auto-Focus Mode Change QCheckBox")
        # else:
        #     self.AF_Enable_CheckBox = QCheckBox("No Auto-Focus function")
        #     self.AF_Enable_CheckBox.setChecked(False)
        #     self.AF_Enable_CheckBox.setEnabled(False)
        #     print("No Auto-Focus Mode Change QCheckBox")
            
        # Preview qpicamera2
        self.qpicamera2 = QGlPicamera2(picam2,
                          width=preview_width, height=preview_height,
                          keep_ar=True)
        self.qpicamera2.done_signal.connect(self.capture_done)
        
        self.childPreviewLayout.addWidget(self.qpicamera2)
        
        # Capture button on Child Window
        self.btnChildCapture = QPushButton("Capture Image")
        self.btnChildCapture.setFont(QFont("Helvetica", 13, QFont.Bold))
        self.btnChildCapture.clicked.connect(self.on_Capture_Clicked)
        
        self.childPreviewLayout.addWidget(self.btnChildCapture)
        
        # pass layout to child Preview Window
        self.myPreviewWindow = self.MyPreviewWidget(self.childPreviewLayout)
        # roughly set Preview windows size according to preview_width x preview_height
        self.myPreviewWindow.setGeometry(10, 10, preview_width+10, preview_height+100)
        self.myPreviewWindow.setWindowTitle("Preview size - " +
                                            str(preview_width) + " x " + str(preview_height))
        self.myPreviewWindow.show()

        #--- End of Prepare child Preview Window ---

        self.layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabControl = QWidget()
        self.tabInfo = QWidget()

        # Add tabs
        self.tabs.addTab(self.tabControl,"Control")
        self.tabs.addTab(self.tabInfo,   " Info  ")
        
        #=== Tab Capture ===
        # Create first tab
        self.tabControl.layout = QVBoxLayout()
        
        self.btnCapture = QPushButton("Capture Image")
        self.btnCapture.setFont(QFont("Helvetica", 15, QFont.Bold))
        self.btnCapture.clicked.connect(self.on_Capture_Clicked)
        
        self.tabControl.layout.addWidget(self.btnCapture)
        
        self.labelMore = QLabel("...more will place here in coming exercise.")
        self.tabControl.layout.addWidget(self.labelMore)
        
        self.tabControl.layout.addStretch()
        
        self.tabControl.setLayout(self.tabControl.layout)

        #=== Tab Info ===
        self.tabInfo.layout = QVBoxLayout()
        
        infoGridLayout = QGridLayout()
        
        rowSpan = 1
        columnSpan0 = 1
        columnSpan1 = 5
        infoGridLayout.addWidget(QLabel('Python', self), 0, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel(platform.python_version(), self), 0, 1, rowSpan, columnSpan1)
        
        infoGridLayout.addWidget(QLabel(picamera2_name, self), 1, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel(version(picamera2_name), self), 1, 1, rowSpan, columnSpan1)
        
        infoGridLayout.addWidget(QLabel(' ', self), 2, 0, rowSpan, columnSpan0)        
        infoGridLayout.addWidget(QLabel('Camera Module:', self), 3, 0, rowSpan, columnSpan0)
        
        cam_properties = picam2.camera_properties
        cam_Model = cam_properties['Model']
        infoGridLayout.addWidget(QLabel('Model', self), 4, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel(cam_Model, self), 4, 1, rowSpan, columnSpan1)
        cam_PixelArraySize = str(cam_properties['PixelArraySize'][0]) + " x " + str(cam_properties['PixelArraySize'][1])
        infoGridLayout.addWidget(QLabel('PixelArraySize', self), 5, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel(cam_PixelArraySize, self), 5, 1, rowSpan, columnSpan1)
        
        infoGridLayout.addWidget(QLabel(' ', self), 6, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel('Machine:', self), 7, 0, rowSpan, columnSpan0)
        infoGridLayout.addWidget(QLabel('Board', self), 8, 0, rowSpan, columnSpan0, Qt.AlignTop)
        board_def = "/proc/device-tree/model"
        board_info = self.read_f("/proc/device-tree/model") +"\n(" + board_def +")"
        infoGridLayout.addWidget(QLabel(board_info, self), 8, 1, rowSpan, columnSpan0)
        
        infoGridLayout.addWidget(QLabel('OS', self), 9, 0, rowSpan, columnSpan0, Qt.AlignTop)
        os_info = self.read_pretty_name() + "\n" + os.uname()[3]
        infoGridLayout.addWidget(QLabel(os_info, self), 9, 1, rowSpan, columnSpan1)
        
        self.tabInfo.layout.addLayout(infoGridLayout)
        self.tabInfo.layout.addStretch()
        
        self.tabInfo.setLayout(self.tabInfo.layout)
        
        #==================================
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        picam2.start()


def main():
    model = ArduinoModel()
    controller = ArduinoController(model)
    controllerApp = QApplication([])
    controllerWindow = PyControllerWindow(controller)
    controllerWindow.show()
    sys.exit(controllerApp.exec())


if __name__ == "__main__":
    main()
