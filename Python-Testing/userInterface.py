from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton, QComboBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class UserInterface(QMainWindow):
    def __init__(self, start_measuring_callback, stop_measuring_callback, change_config_callback):
        super().__init__()
        self.initUI(start_measuring_callback, stop_measuring_callback, change_config_callback)

    def initUI(self, start_measuring_callback, stop_measuring_callback, change_config_callback):
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
        self.start_button.clicked.connect(start_measuring_callback)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Measuring")
        self.stop_button.clicked.connect(stop_measuring_callback)
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
        self.config_selector.currentIndexChanged.connect(change_config_callback)
        layout.addWidget(self.config_selector)  # Add the combo box to the layout

        # Set up the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def reset_plot(self):
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []

    def update_plot(self, current_measurement, calibrated_force, elapsed_time):

        self.measurements.append(current_measurement)
        self.calibrated_forces.append(calibrated_force)
        self.timestamps.append(elapsed_time)

        self.timestamps = self.timestamps[-50:]
        self.calibrated_forces = self.calibrated_forces[-50:]
        
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
            timestamps = self.timestamps
            
            # Update each line in the plot
            for i, line in enumerate(self.lines):
                line.set_data(timestamps, force_array[:, i, 0])

            # Adjust plot limits
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()