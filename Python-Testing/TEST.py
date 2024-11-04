import pyvisa
import sys
import os
import time
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton, QComboBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
from datetime import datetime

class DAQ970AApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Calibration matrices
        self.norm_C1_inv = np.array([[34685, -6.0667, -34.774],
                                      [804.64, 21210, 225.29],
                                      [-1387.3, 73.623, 38938]])
        
        self.norm_C1_inv_C2 = np.array([[0.00090131, 0.00071979, -0.00059586],
                                         [-0.0085693, -0.00072414, -0.00050641],
                                         [-0.00079632, 0.028777, -9.6631e-06]])

        self.side_C_inv = np.array([[-34668, 49.226, 41.308],
                                     [-837.96, 21224, -15.823],
                                     [1395.9, -399.31, -38930]])
        
        self.side_C1_inv_C2 = np.array([[-0.0016532, 0.00094694, 0.00058309],
                                         [-0.0025937, 0.00027556, -0.0010782],
                                         [0.0014352, -0.001701, 2.3735e-05]])

        # Default to normal configuration
        self.current_calibration = 'Normal'

        self.initUI()
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.measurement_timer = QTimer()

        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        
        self.setup_csv_logging()
        self.connect_to_instrument()

    def initUI(self):
        self.setWindowTitle("DAQ970A Matrix Data Display with Calibration")
        self.setGeometry(100, 100, 400, 300)  # Adjust size for visibility

        layout = QVBoxLayout()

        self.setWindowTitle("DAQ970A Matrix Data Display with Calibration")
        self.setGeometry(100, 100, 1000, 800)

        layout = QVBoxLayout()

        # Labels for both raw and calibrated data
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        self.calibrated_data_label = QLabel("Calibrated Forces:\nNo data yet")
        layout.addWidget(self.raw_data_label)
        layout.addWidget(self.calibrated_data_label)

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
        self.ax.set_title("Live Calibrated Forces")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force")
        
        self.lines = []  # Will store line objects for each force component
        labels = ['Normal Force', 'Axial Force', 'Side Force']
        for i in range(3):
            line, = self.ax.plot([], [], label=labels[i])
            self.lines.append(line)
        self.ax.legend()
        self.ax.grid(True)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Label for configuration
        layout.addWidget(QLabel("Select Configuration:"))

        # Dropdown for configuration selection
        self.config_selector = QComboBox()
        self.config_selector.addItems(['Normal', 'Side'])
        self.config_selector.currentIndexChanged.connect(self.change_configuration)
        layout.addWidget(self.config_selector)  # Add the combo box to the layout

        # Set up the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def setup_csv_logging(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_filename = f'logs/raw_data_{timestamp}.csv'
        
        # Create and setup CSV file with headers
        with open(self.csv_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Channel_301', 'Channel_302', 'Channel_303'])

    def change_configuration(self):
        """Change calibration matrices based on selected configuration."""
        self.current_calibration = self.config_selector.currentText()
        print(f"Configuration changed to: {self.current_calibration}")

    def calibrate_forces(self, voltage_matrix):
        """Apply calibration based on the current configuration."""
        R = voltage_matrix.reshape((3, 1))
        
        if self.current_calibration == 'Normal':
            term1 = np.dot(self.norm_C1_inv, R)
            C1_inv_abs = np.abs(self.norm_C1_inv)
            magnitude_term = np.dot(C1_inv_abs, R)
            term2 = np.dot(self.norm_C1_inv_C2, magnitude_term)
        else:  # Side configuration
            term1 = np.dot(self.side_C_inv, R)
            C1_inv_abs = np.abs(self.side_C_inv)
            magnitude_term = np.dot(C1_inv_abs, R)
            term2 = np.dot(self.side_C1_inv_C2, magnitude_term)

        F = term1 - term2
        return F
        

    def connect_to_instrument(self):
        devices = self.rm.list_resources('USB?*INSTR')
        
        if devices:
            self.connection = self.rm.open_resource(devices[2])
            self.connection.clear()
            self.connection.write('*IDN?')
            idn = self.connection.read()
            print(f"Connected to: {idn}")
            
            # Configure the instrument for all three channels
            self.connection.write('SYSTem:BEEPer:STATe Off')
            self.connection.write('CONF:VOLT:DC 1mV,0.00001,(@301,302,303)')
        else:
            print("No USB instruments found")

    def start_measuring(self):
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        self.start_time = time.time()
        self.measurement_timer.timeout.connect(self.measure_task)
        self.measurement_timer.start(10)  # Measure every 10ms

    def stop_measuring(self):
        self.measurement_timer.stop()
        self.raw_data_label.setText("Measuring stopped.")
        print(f"Raw data logged to: {self.csv_filename}")

    def measure_task(self):
        if self.connection:
            try:
                # Create a 3x1 matrix for current measurements
                current_measurement = np.zeros((3, 1))
                
                # Read all three channels
                for i, channel in enumerate([301, 302, 303]):
                    self.connection.write(f'MEAS:VOLT:DC? (@{channel})')
                    current_measurement[i, 0] = float(self.connection.read())

                # Store raw measurement matrix
                self.measurements.append(current_measurement)
                
                # Get timestamp
                elapsed_time = time.time() - self.start_time
                self.timestamps.append(elapsed_time)
                
                # Log raw data to CSV
                with open(self.csv_filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([elapsed_time] + current_measurement.flatten().tolist())

                # Calculate calibrated forces
                calibrated_force = self.calibrate_forces(current_measurement)
                self.calibrated_forces.append(calibrated_force)

                # Update display labels
                raw_matrix_str = (f"[{current_measurement[0,0]:.6f}]\n"
                                f"[{current_measurement[1,0]:.6f}]\n"
                                f"[{current_measurement[2,0]:.6f}]")
                self.raw_data_label.setText(f"Raw Voltages (V):\n{raw_matrix_str}")

                calibrated_str = (f"[{calibrated_force[0,0]:.3f}]\n"
                                f"[{calibrated_force[1,0]:.3f}]\n"
                                f"[{calibrated_force[2,0]:.3f}]")
                self.calibrated_data_label.setText(f"Calibrated Forces:\n{calibrated_str}")

                # Update plot with calibrated forces
                if self.calibrated_forces:
                    force_array = np.array(self.calibrated_forces)
                    
                    # Update each line in the plot
                    for i, line in enumerate(self.lines):
                        line.set_data(self.timestamps, force_array[:, i, 0])

                    # Adjust plot limits
                    self.ax.relim()
                    self.ax.autoscale_view()
                    self.canvas.draw()

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