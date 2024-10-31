import pyvisa
import sys
import os
import time
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DAQ970AApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.measurement_timer = QTimer()
        
        # Store measurements and timestamps
        self.measurements = []
        self.timestamps = []
        
        # Attempt to connect to the instrument
        self.connect_to_instrument()

    def initUI(self):
        self.setWindowTitle("DAQ970A Live Data Display")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.data_label = QLabel("No data yet")
        layout.addWidget(self.data_label)

        self.start_button = QPushButton("Start Measuring")
        self.start_button.clicked.connect(self.start_measuring)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Measuring")
        self.stop_button.clicked.connect(self.stop_measuring)
        layout.addWidget(self.stop_button)

        # Set up Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Live Measurements")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def connect_to_instrument(self):
        devices = self.rm.list_resources('USB?*INSTR')
        
        if devices:
            self.connection = self.rm.open_resource(devices[0])
            self.connection.clear()
            self.connection.write('*IDN?')
            idn = self.connection.read()
            print(f"Connected to: {idn}")
            
            # Configure the instrument
            self.connection.write('SYSTem:BEEPer:STATe Off')
            self.connection.write('CONF:VOLT:DC 1mV,0.00001,(@303)')
            #self.connection.write('FORM:READ:TIME ON')
            #self.connection.write('FORM:READ:TIME:TYPE ABS')
        else:
            print("No USB instruments found")

    def start_measuring(self):
        self.measurements.clear()  # Clear previous measurements
        self.timestamps.clear()  # Clear previous timestamps
        self.start_time = time.time()  # Record the start time
        self.measurement_timer.timeout.connect(self.measure_task)
        self.measurement_timer.start(10)  # Measure every second

    def stop_measuring(self):
        self.measurement_timer.stop()  # Stop the timer
        self.data_label.setText("Measuring stopped.")

    def measure_task(self):
        if self.connection:
            try:
                self.connection.write('READ?')
                result = float(self.connection.read())
                self.data_label.setText(f"Measurement: {result:.6f} V")
                self.measurements.append(result)

                # Calculate elapsed time and append to timestamps
                elapsed_time = time.time() - self.start_time
                self.timestamps.append(elapsed_time)

                # Update the plot
                self.ax.clear()
                self.ax.plot(self.timestamps, self.measurements, marker='o', markersize=4)
                self.ax.set_title("Live Measurements")
                self.ax.set_xlabel("Time (s)")
                self.ax.set_ylabel("Voltage (V)")
                self.canvas.draw()  # Redraw the canvas with the new data
            except Exception as ex:
                print(f"ERROR: {ex}")

    def closeEvent(self, event):
        if self.connection:
            self.connection.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = DAQ970AApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


