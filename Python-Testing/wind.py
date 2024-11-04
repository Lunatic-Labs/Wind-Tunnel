import pyvisa
import sys
import os
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton, QComboBox, QTabWidget, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
from datetime import datetime


class MeasurementThread(QThread):
    data_ready = pyqtSignal(np.ndarray, np.ndarray)
    error_occurred = pyqtSignal(str)

    def __init__(self, connection, calibration_func):
        super().__init__()
        self.connection = connection
        self.calibration_func = calibration_func
        self.running = True
        self._is_paused = False
        self._pause_mutex = QMutex()
        self._pause_condition = QWaitCondition()
        self.start_time = time.time()
        self.csv_filename = None

    def set_csv_filename(self, filename):
        self.csv_filename = filename

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False
        self._pause_condition.wakeAll()

    def run(self):
        while self.running:
            try:
                # Handle pause state
                self._pause_mutex.lock()
                while self._is_paused:
                    self._pause_condition.wait(self._pause_mutex)
                self._pause_mutex.unlock()

                # Take measurements
                current_measurement = np.zeros((3, 1))
                for i, channel in enumerate([301, 302, 303]):
                    if not self.running:  # Check if we should stop
                        return
                    self.connection.write(f'MEAS:VOLT:DC? (@{channel})')
                    current_measurement[i, 0] = float(self.connection.read())
                
                # Log raw data to CSV
                if self.csv_filename:
                    elapsed_time = time.time() - self.start_time
                    with open(self.csv_filename, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([elapsed_time] + current_measurement.flatten().tolist())

                calibrated_force = self.calibration_func(current_measurement)
                self.data_ready.emit(current_measurement, calibrated_force)
                
                self.msleep(1)  # 1ms delay between measurements

            except Exception as e:
                self.error_occurred.emit(str(e))
                self.running = False

    def stop(self):
        self.running = False
        self.resume()  # Wake up the thread if it's paused
        self.quit()
        self.wait()


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
        self.measurement_thread = None
        
        self.setup_csv_logging()
        self.connect_to_instrument()

    def initUI(self):
        self.setWindowTitle("DAQ970A Matrix Data Display with Calibration")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Measurement Tab
        self.measurement_tab = QWidget()
        self.tabs.addTab(self.measurement_tab, "Measurements")
        self.setup_measurement_tab()

        # Configuration Tab
        self.config_tab = QWidget()
        self.tabs.addTab(self.config_tab, "Configuration")
        self.setup_config_tab()

    def setup_measurement_tab(self):
        layout = QHBoxLayout()

        # Left layout for data display and buttons
        left_layout = QVBoxLayout()

        # Labels for both raw and calibrated data
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        self.calibrated_data_label = QLabel("Calibrated Forces:\nNo data yet")
        left_layout.addWidget(self.raw_data_label)
        left_layout.addWidget(self.calibrated_data_label)

        # Status label
        self.status_label = QLabel("Status: Ready")
        left_layout.addWidget(self.status_label)

        # Buttons
        self.start_button = QPushButton("Start Measuring")
        self.start_button.clicked.connect(self.start_measuring)
        left_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        left_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop Measuring")
        self.stop_button.clicked.connect(self.stop_measuring)
        self.stop_button.setEnabled(False)
        left_layout.addWidget(self.stop_button)

        layout.addLayout(left_layout)

        # Right layout for graphs
        right_layout = QVBoxLayout()

        # Create a separate figure for each force
        self.figures = []
        self.canvases = []
        self.axes = []
        self.lines = []

        for i in range(3):
            figure = Figure()
            canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)
            ax.set_title(f"Force Component {i + 1}")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Force")
            ax.grid(True)
            right_layout.addWidget(canvas)
            
            self.figures.append(figure)
            self.canvases.append(canvas)
            self.axes.append(ax)
            line, = ax.plot([], [])
            self.lines.append(line)

        layout.addLayout(right_layout)
        self.measurement_tab.setLayout(layout)

    def setup_config_tab(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Configuration:"))

        self.config_selector = QComboBox()
        self.config_selector.addItems(['Normal', 'Side'])
        self.config_selector.currentIndexChanged.connect(self.change_configuration)
        layout.addWidget(self.config_selector)

        self.config_tab.setLayout(layout)

    def setup_csv_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_filename = f'logs/raw_data_{timestamp}.csv'
        
        with open(self.csv_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Channel_301', 'Channel_302', 'Channel_303'])

    def connect_to_instrument(self):
        try:
            devices = self.rm.list_resources('USB?*INSTR')
            
            if devices:
                self.connection = self.rm.open_resource(devices[2])
                self.connection.clear()
                self.connection.write('*IDN?')
                idn = self.connection.read()
                print(f"Connected to: {idn}")
                self.status_label.setText(f"Status: Connected to {idn}")
                
                # Configure the instrument
                self.connection.write('SYSTem:BEEPer:STATe Off')
                self.connection.write('CONF:VOLT:DC 1mV,0.00001,(@301,302,303)')
            else:
                self.status_label.setText("Status: No USB instruments found")
                print("No USB instruments found")
        except Exception as e:
            self.status_label.setText(f"Status: Connection error - {str(e)}")
            print(f"Connection error: {e}")

    def start_measuring(self):
        if self.connection and not self.measurement_thread:
            self.measurement_thread = MeasurementThread(self.connection, self.calibrate_forces)
            self.measurement_thread.set_csv_filename(self.csv_filename)
            self.measurement_thread.data_ready.connect(self.update_data)
            self.measurement_thread.error_occurred.connect(self.handle_measurement_error)
            
            # Reset plot data
            self.timestamps = []
            self.calibrated_forces = []
            for line in self.lines:
                line.set_data([], [])
            
            self.measurement_thread.start()
            self.status_label.setText("Status: Measuring")
            
            # Update button states
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    def toggle_pause(self):
        if self.measurement_thread:
            if self.measurement_thread._is_paused:
                self.measurement_thread.resume()
                self.pause_button.setText("Pause")
                self.status_label.setText("Status: Measuring")
            else:
                self.measurement_thread.pause()
                self.pause_button.setText("Resume")
                self.status_label.setText("Status: Paused")

    def stop_measuring(self):
        if self.measurement_thread:
            self.measurement_thread.stop()
            self.measurement_thread = None
            self.status_label.setText("Status: Stopped")
            print(f"Raw data logged to: {self.csv_filename}")
            
            # Reset button states
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.pause_button.setText("Pause")

    def handle_measurement_error(self, error_message):
        self.status_label.setText(f"Status: Error - {error_message}")
        self.stop_measuring()

    def update_data(self, current_measurement, calibrated_force):
        # Update display labels
        raw_matrix_str = (f"[{current_measurement[0,0]:.6f}]\n"
                         f"[{current_measurement[1,0]:.6f}]\n"
                         f"[{current_measurement[2,0]:.6f}]")
        self.raw_data_label.setText(f"Raw Voltages (V):\n{raw_matrix_str}")

        calibrated_str = (f"[{calibrated_force[0,0]:.3f}]\n"
                         f"[{calibrated_force[1,0]:.3f}]\n"
                         f"[{calibrated_force[2,0]:.3f}]")
        self.calibrated_data_label.setText(f"Calibrated Forces:\n{calibrated_str}")

        # Update plots
        elapsed_time = time.time() - self.measurement_thread.start_time
        self.timestamps.append(elapsed_time)
        self.calibrated_forces.append(calibrated_force)

        force_array = np.array(self.calibrated_forces)
        for i in range(3):
            self.lines[i].set_data(self.timestamps, force_array[:, i, 0])
            self.axes[i].relim()
            self.axes[i].autoscale_view()
            self.canvases[i].draw()

    def change_configuration(self):
        self.current_calibration = self.config_selector.currentText()
        print(f"Configuration changed to: {self.current_calibration}")

    def calibrate_forces(self, voltage_matrix):
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

        return term1 - term2

    def closeEvent(self, event):
        if self.measurement_thread:
            self.measurement_thread.stop()
        if self.connection:
            self.connection.close()
            self.connection = None
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = DAQ970AApp()
    mainWin.show()
    sys.exit(app.exec_())


