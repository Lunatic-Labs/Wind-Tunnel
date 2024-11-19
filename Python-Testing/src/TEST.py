from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QComboBox, QTabWidget, QFormLayout, QLineEdit, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyvisa
import time
import numpy as np
import os
import sys
import csv
from datetime import datetime


class DAQ970AApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Calibration matrices (kept as in your original code)
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

        self.current_calibration = 'Normal'
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        self.selected_channels = [301, 302, 303]  # Default channels (301, 302, 303)

        # Initialize PyVisa resource manager
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.measurement_timer = QTimer()

        self.setup_csv_logging()
        self.connect_to_instrument()

        # Setup the GUI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DAQ970A Matrix Data Display with Calibration")
        self.setGeometry(100, 100, 1000, 800)  # Adjust the window size

        # Create a QTabWidget for managing tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_configuration_tab(), "Configuration")
        tabs.addTab(self.create_data_display_tab(), "Data Display")

        # Set the QTabWidget as the central widget
        self.setCentralWidget(tabs)

    def create_configuration_tab(self):
        """Create the Configuration tab with a drop-down for calibration and textboxes for channel selection."""
        config_tab = QWidget()
        layout = QVBoxLayout()

        # Create a form layout for configuration options
        form_layout = QFormLayout()

        # Dropdown for configuration selection (Normal / Side)
        self.config_selector = QComboBox()
        self.config_selector.addItems(['Normal', 'Side'])
        self.config_selector.currentIndexChanged.connect(self.change_configuration)
        form_layout.addRow("Select Configuration:", self.config_selector)

        # Input fields for channel selection
        self.channel1_input = QLineEdit()
        self.channel1_input.setPlaceholderText("Channel 1 (301-320)")

        self.channel2_input = QLineEdit()
        self.channel2_input.setPlaceholderText("Channel 2 (301-320)")

        self.channel3_input = QLineEdit()
        self.channel3_input.setPlaceholderText("Channel 3 (301-320)")

        form_layout.addRow("Enter Channel 1:", self.channel1_input)
        form_layout.addRow("Enter Channel 2:", self.channel2_input)
        form_layout.addRow("Enter Channel 3:", self.channel3_input)

        # Save button to confirm channel selection
        self.save_button = QPushButton("Save Channels")
        self.save_button.clicked.connect(self.save_channels)
        form_layout.addRow(self.save_button)

        layout.addLayout(form_layout)
        config_tab.setLayout(layout)

        return config_tab

    def create_data_display_tab(self):
        """Create the Data Display tab with start/stop buttons, channel selection, and plot."""
        data_tab = QWidget()
        layout = QVBoxLayout()

        # Add Start and Stop buttons
        self.start_button = QPushButton("Start Measuring")
        self.start_button.clicked.connect(self.start_measuring)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Measuring")
        self.stop_button.clicked.connect(self.stop_measuring)
        layout.addWidget(self.stop_button)

        # Labels for raw and calibrated data
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        self.calibrated_data_label = QLabel("Calibrated Forces:\nNo data yet")
        layout.addWidget(self.raw_data_label)
        layout.addWidget(self.calibrated_data_label)

        # Set up Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Set up the plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Live Calibrated Forces")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force")
        self.lines = []  # Store line objects for force components
        labels = ['Normal Force', 'Axial Force', 'Side Force']
        for i in range(3):
            line, = self.ax.plot([], [], label=labels[i])
            self.lines.append(line)
        self.ax.legend()
        self.ax.grid(True)

        data_tab.setLayout(layout)

        return data_tab

    def setup_csv_logging(self):
        """Setup CSV logging for storing measurements."""
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

    def save_channels(self):
        """Save the selected channels after validating input."""
        try:
            # Get values from the input fields
            channel1 = int(self.channel1_input.text())
            channel2 = int(self.channel2_input.text())
            channel3 = int(self.channel3_input.text())

            # Validate that channels are within the acceptable range and not the same
            if not (301 <= channel1 <= 320 and 301 <= channel2 <= 320 and 301 <= channel3 <= 320):
                self.show_error_message("Invalid channels", "Each channel must be between 301 and 320.")
                return

            if len({channel1, channel2, channel3}) != 3:
                self.show_error_message("Duplicate channels", "Channels must be unique.")
                return

            # If valid, update the selected channels
            self.selected_channels = [channel1, channel2, channel3]
            print(f"Selected channels: {self.selected_channels}")

        except ValueError:
            self.show_error_message("Invalid input", "Please enter valid channel numbers (301-320).")

    def show_error_message(self, title, message):
        """Display an error message dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

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
            self.connection = self.rm.open_resource(devices[2])  # Select the first device
            self.connection.clear()
            self.connection.write('*IDN?')
            idn = self.connection.read()
            print(f"Connected to: {idn}")

            # Configure the instrument for the selected channels
            channel_str = ','.join([f"@{ch}" for ch in self.selected_channels])
            self.connection.write(f'CONF:VOLT:DC 1mV,0.00001,({channel_str})')
            self.connection.write(f'ROUT:SCAN ({channel_str})')
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

                # Read all selected channels
                self.connection.write('READ?')
                result = self.connection.read()
                for i, value in enumerate(result.split(',')):
                    current_measurement[i, 0] = float(value)

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

                self.timestamps = self.timestamps[-50:]
                self.calibrated_forces = self.calibrated_forces[-50:]

                # Update display labels
                raw_matrix_str = (f"[{current_measurement[0, 0]:.6f}]\n"
                                  f"[{current_measurement[1, 0]:.6f}]\n"
                                  f"[{current_measurement[2, 0]:.6f}]")
                self.raw_data_label.setText(f"Raw Voltages (V):\n{raw_matrix_str}")

                calibrated_str = (f"[{calibrated_force[0, 0]:.3f}]\n"
                                  f"[{calibrated_force[1, 0]:.3f}]\n"
                                  f"[{calibrated_force[2, 0]:.3f}]")
                self.calibrated_data_label.setText(f"Calibrated Forces:\n{calibrated_str}")

                # Update plot with calibrated forces
                if self.calibrated_forces:
                    force_array = np.array(self.calibrated_forces)
                    timestamps = self.timestamps

                    # Update each line in the plot
                    for i, line in enumerate(self.lines):
                        line.set_data(timestamps, force_array[:, i, 0])

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