from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                            QWidget, QPushButton, QComboBox, QTabWidget, 
                            QFormLayout, QLineEdit, QMessageBox, QGroupBox,
                            QScrollArea, QFileDialog)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import time
import json

class DAQ970AGui(QMainWindow):
    def __init__(self, App):
        super().__init__()
        self.app = App
        self.db = App.db
        
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.app.measure_task)
        
        self.measurements = []
        self.calibrated_forces = []
        self.timestamps = []
        self.start_time = None
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("WindViz")
        self.setGeometry(100, 100, 1000, 800)

        main_scroll = QScrollArea()
        self.setCentralWidget(main_scroll)
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(1)

        content_widget = QWidget()
        content_widget.setMinimumHeight(1200)
        main_scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(20)

        control_panel = QHBoxLayout()

        """ Test control group """
        test_group = QGroupBox("Test Control")
        test_layout = QVBoxLayout()
        self.start_button = QPushButton("Start Measuring")
        self.stop_button = QPushButton("Stop Measuring")
        test_layout.addWidget(self.start_button)
        test_layout.addWidget(self.stop_button)
        test_group.setLayout(test_layout)

        """ Configuration group """
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        self.open_config_button = QPushButton("Configure Test")
        self.load_config_button = QPushButton("Load Configuration")
        config_layout.addWidget(self.open_config_button)
        config_layout.addWidget(self.load_config_button)
        config_group.setLayout(config_layout)

        """ Add groups """
        control_panel.addWidget(test_group)
        control_panel.addWidget(config_group)
        
				# add to layout
        main_layout.addLayout(control_panel)

        """ Data display group """
        data_group = QGroupBox("Raw Data")
        data_layout = QVBoxLayout()
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        self.calibrated_data_label = QLabel("Calibrated Forces:\nNo data yet")
        data_layout.addWidget(self.raw_data_label)
        data_layout.addWidget(self.calibrated_data_label)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        """ Create graphs """
        measurement_types = ['Calibrated Forces', 'Raw Voltages', 'Temperature', 'STING']
        for mtype in measurement_types:
            container = QHBoxLayout()
            
            fig = Figure(figsize=(10, 3))
            canvas = FigureCanvas(fig)
            canvas.setMinimumHeight(250)
            ax = fig.add_subplot(111)
            
            if mtype == 'Calibrated Forces':
                self.figure = fig
                self.canvas = canvas
                self.ax = ax
                self.lines = []
                labels = ['Normal Force', 'Axial Force', 'Side Force']
                for label in labels:
                    line, = ax.plot([], [], label=label)
                    self.lines.append(line)
                ax.legend()
            else:
                ax.plot([], [])  # empty plot for now
            
            ax.set_title(mtype)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Value")
            ax.grid(True)
            fig.tight_layout()
            
            # add label and canvas
            label = QLabel(mtype)
            label.setFixedWidth(100)
            container.addWidget(canvas)
            container.addWidget(label)
            
            # add container
            container_widget = QWidget()
            container_widget.setLayout(container)
            container_widget.setMinimumHeight(280)
            main_layout.addWidget(container_widget)

        self.start_button.clicked.connect(self.start_measuring)
        self.stop_button.clicked.connect(self.stop_measuring)
        self.open_config_button.clicked.connect(self.open_config_dialog)
        self.load_config_button.clicked.connect(self.load_config_from_json)

    def open_config_dialog(self):
        dialog = self.app.config
        dialog.exec_()
        
    def load_config_from_json(self):
        options = QFileDialog.Options()
        json_file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        try:
            with open(json_file_path, 'r') as file:
                config_data = json.load(file)

            # set db values based on the read data
            for channel_type, channel_info in config_data.items():
                if channel_type not in self.db.data["channels"]:
                    print(f"Skipping invalid channel type: {channel_type}")
                    continue

                # get the 'channels' list from the JSON data
                channels = channel_info.get('channels', [])
                config = channel_info.get('configuration', None)

                # get channel names and ids
                values = [{"id": channel["id"], "name": channel["name"]} for channel in channels]

                # set db
                try:
                    self.db.set_channel_data(channel_type, values, config)
                except ValueError as e:
                    print(f"Error setting channel data for {channel_type}: {e}")
            
            print(self.db.get_channel_data("pressure"))

            self.show_success()
            
            return 0

        except FileNotFoundError:
            print(f"Error: The file {json_file_path} was not found.")
            return 1
        except json.JSONDecodeError:
            print(f"Error: Failed to decode the JSON from {json_file_path}.")
            return 2
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 3
    
    def show_success(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Configuration successfully loaded!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
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
        

if __name__ == "__main__":
    print("Dont do that\n\n>.>\n\n")