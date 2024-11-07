
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
        self.setGeometry(100, 100, 600, 400)  # Adjust size for better visibility

        layout = QVBoxLayout()

        # Labels for raw and calibrated data
        self.raw_data_label = QLabel("Raw Voltages (V):")
        self.calibrated_data_label = QLabel("Calibrated Forces:")

        # Matplotlib figure setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title('Calibrated Forces Over Time')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Calibrated Forces')
        self.ax.grid(True)
        self.lines = [self.ax.plot([], [])[0] for _ in range(3)]  # Assuming 3 lines for each force component

        # Add widgets to layout
        layout.addWidget(self.raw_data_label)
        layout.addWidget(self.calibrated_data_label)
        layout.addWidget(self.canvas)

        # Container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_plot(self):
        if self.calibrated_forces:
            force_array = np.array(self.calibrated_forces[-100:])  # Only take the latest 100 data points
            timestamps = self.timestamps[-100:]  # Only take the latest 100 timestamps

            # Update each line in the plot
            for i, line in enumerate(self.lines):
                line.set_data(timestamps, force_array[:, i, 0])

            # Adjust plot limits
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

    def process_measurement(self, current_measurement):
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
        raw_matrix_str = (f"[{current_measurement[0,0]:.6f}]
"
                          f"[{current_measurement[1,0]:.6f}]
"
                          f"[{current_measurement[2,0]:.6f}]")
        self.raw_data_label.setText(f"Raw Voltages (V):
{raw_matrix_str}")

        calibrated_str = (f"[{calibrated_force[0,0]:.3f}]
"
                          f"[{calibrated_force[1,0]:.3f}]
"
                          f"[{calibrated_force[2,0]:.3f}]")
        self.calibrated_data_label.setText(f"Calibrated Forces:
{calibrated_str}")

        # Update plot with calibrated forces
        self.update_plot()

    # Other methods remain unchanged...

def main():
    app = QApplication(sys.argv)
    window = DAQ970AApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
