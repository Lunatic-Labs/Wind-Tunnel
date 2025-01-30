from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                            QWidget, QPushButton, QComboBox, QTabWidget, 
                            QFormLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import time

class DAQ970AGui(QMainWindow):
    def __init__(self, App):
        super().__init__()
        self.initUI()
        self.app = App

        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.app.measure_task)
        
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        self.start_time = None
        
    def initUI(self):
        self.setWindowTitle("WindViz")
        self.setGeometry(100, 100, 1000, 800)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_data_display_tab(), "Data Display")
        
        self.setCentralWidget(self.tabs)

    
    def open_config_dialog(self):
        dialog = self.app.config
        dialog.exec_()
    
    def saved_channels(self):
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
            message = f"Selected channels: {self.selected_channels}" 
            print(message)
            QMessageBox.information(self, 'Success', message)

        except ValueError:
            self.show_error_message("Invalid input", "Please enter valid channel numbers (301-320).")

    def start_measuring(self):
        """Start the measurement process."""
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        self.start_time = time.time()
        self.measurement_timer.start(10)  # Measure every 10ms

    def stop_measuring(self):
        """Stop the measurement process."""
        self.measurement_timer.stop()
        self.raw_data_label.setText("Measuring stopped.")

    def create_data_display_tab(self):
        """Create data display tab with plot and controls."""
        data_tab = QWidget()
        layout = QVBoxLayout()

        '''Configure test hardware data buttons'''
        self.open_config_button = QPushButton("Configure Test")
        layout.addWidget(self.open_config_button)
        # Event listeners
        self.open_config_button.clicked.connect(self.open_config_dialog)


        # Control buttons
        self.start_button = QPushButton("Start Measuring")
        self.stop_button = QPushButton("Stop Measuring")
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.start_button.clicked.connect(self.start_measuring)
        self.stop_button.clicked.connect(self.stop_measuring)

        # Data labels
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        self.calibrated_data_label = QLabel("Calibrated Forces:\nNo data yet")
        layout.addWidget(self.raw_data_label)
        layout.addWidget(self.calibrated_data_label)

        # Plot setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Live Calibrated Forces")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force")
        self.lines = []
        
        labels = ['Normal Force', 'Axial Force', 'Side Force']
        for i in range(3):
            line, = self.ax.plot([], [], label=labels[i])
            self.lines.append(line)
            
        self.ax.legend()
        self.ax.grid(True)
        layout.addWidget(self.canvas)

        data_tab.setLayout(layout)
        return data_tab

    def show_error_message(self, title, message):
        """Display an error message dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def update_display(self, raw_data, calibrated_data):
        """Update the display with new measurements."""
        raw_matrix_str = '\n'.join([f"[{val:.6f}]" for val in raw_data])
        self.raw_data_label.setText(f"Raw Voltages (V):\n{raw_matrix_str}")

        calibrated_str = '\n'.join([f"[{val[0]:.3f}]" for val in calibrated_data])
        self.calibrated_data_label.setText(f"Calibrated Forces:\n{calibrated_str}")

    def update_plot(self, timestamps, calibrated_forces):
        """Update the plot with new data."""
        if not calibrated_forces:
            return
        
        latestTimestamps = timestamps[-50:]
        latestForces = np.array(calibrated_forces[-50:])

        force_array = np.array(latestForces)
        for i, line in enumerate(self.lines):
            line.set_data(latestTimestamps, force_array[:, i, 0])

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()