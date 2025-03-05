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
        self.im = App.instrument
        
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.app.measure_task)
        
        self.pressure_data = []
        self.velocity_data = []
        self.temp_data = []
        self.sting_data = []  # Will hold calibrated forces for STING
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
        test_group = QGroupBox("Test Control")
        test_layout = QVBoxLayout()
        self.start_button = QPushButton("Start Measuring")
        self.stop_button = QPushButton("Stop Measuring")
        test_layout.addWidget(self.start_button)
        test_layout.addWidget(self.stop_button)
        test_group.setLayout(test_layout)

        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        self.open_config_button = QPushButton("Configure Test")
        self.load_config_button = QPushButton("Load Configuration")
        config_layout.addWidget(self.open_config_button)
        config_layout.addWidget(self.load_config_button)
        config_group.setLayout(config_layout)

        control_panel.addWidget(test_group)
        control_panel.addWidget(config_group)
        main_layout.addLayout(control_panel)

        data_group = QGroupBox("Raw Data")
        data_layout = QVBoxLayout()
        self.raw_data_label = QLabel("Raw Voltages (V):\nNo data yet")
        data_layout.addWidget(self.raw_data_label)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        measurement_types = {
            'Pressure': ('Pressure (V)', self.pressure_data),
            'Velocity': ('Velocity (V)', self.velocity_data),
            'Temperature': ('Temperature (V)', self.temp_data),
            'STING': ('Calibrated Forces (N)', self.sting_data)  # Updated label
        }
        
        self.plots = {}
        for mtype, (ylabel, data_store) in measurement_types.items():
            container = QHBoxLayout()
            fig = Figure(figsize=(10, 3))
            canvas = FigureCanvas(fig)
            canvas.setMinimumHeight(250)
            ax = fig.add_subplot(111)
            
            self.plots[mtype] = {
                'fig': fig,
                'canvas': canvas,
                'ax': ax,
                'lines': [],
                'data': data_store
            }
            
            line, = ax.plot([], [], label=mtype)
            self.plots[mtype]['lines'].append(line)
            
            ax.set_title(mtype)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(ylabel)
            ax.grid(True)
            ax.legend()
            fig.tight_layout()
            
            label = QLabel(mtype)
            label.setFixedWidth(100)
            container.addWidget(canvas)
            container.addWidget(label)
            
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
    
            if "channels" not in config_data:
                print("Invalid JSON format: missing 'channels' key")
                return 1
    
            pressure_values = []
            velocity_values = []
            temperature_values = []
            sting_values = []
    
            for channel_type, channel_info in config_data["channels"].items():
                if channel_type not in self.db.data["channels"]:
                    print(f"Skipping invalid channel type: {channel_type}")
                    continue
    
                values = channel_info.get('values', [])
                config = channel_info.get('configuration', None)
    
                if channel_type == "pressure":
                    pressure_values = [int(v) for v in values if v]
                elif channel_type == "velocity":
                    velocity_values = [int(v) for v in values if v]
                elif channel_type == "temperature":
                    temperature_values = [int(v) for v in values if v]
                elif channel_type == "sting":
                    sting_values = [int(v) for v in values if v]
    
                self.db.set_channel_data(channel_type, values, config)
            
            print(f"\n\n{self.db.get_channel_data('pressure')}")
            self.im.set_channels(pressure_values, velocity_values, temperature_values, sting_values)
    
            self.show_success()
            return 0
            
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return 1

    def show_success(self):
        QMessageBox.information(self, "Success", "Configuration successfully loaded!")

    def start_measuring(self):
        self.pressure_data.clear()
        self.velocity_data.clear()
        self.temp_data.clear()
        self.sting_data.clear()
        self.timestamps.clear()
        self.start_time = time.time()
        self.measurement_timer.start(100)

    def stop_measuring(self):
        self.measurement_timer.stop()
        self.raw_data_label.setText("Measuring stopped.")

    def update_display(self, measurements, timestamps):
        if not measurements:
            return

        pressure_vals, velocity_vals, temp_vals, sting_vals = measurements
        
        raw_str = (f"Pressure: {pressure_vals}\n"
                  f"Velocity: {velocity_vals}\n"
                  f"Temperature: {temp_vals}\n"
                  f"STING (Raw): {sting_vals}")
        self.raw_data_label.setText(f"Raw Voltages (V):\n{raw_str}")

        plot_data = {
            'Pressure': self.pressure_data,
            'Velocity': self.velocity_data,
            'Temperature': self.temp_data,
            'STING': self.sting_data  # Calibrated forces
        }
        
        for mtype, data in plot_data.items():
            plot = self.plots[mtype]
            latest_data = data[-50:]
            ts = self.timestamps[-50:]
            
            if latest_data:
                data_array = np.array(latest_data)
                # Ensure enough lines exist
                while len(plot['lines']) < (data_array.shape[1] if data_array.ndim > 1 else 1):
                    line, = plot['ax'].plot([], [], label=f"{mtype} Ch{len(plot['lines'])+1}")
                    plot['lines'].append(line)
                    plot['ax'].legend()
                
                for i, line in enumerate(plot['lines']):
                    if i == 0 and data_array.ndim == 1:
                        line.set_data(ts, data_array)
                    elif i < data_array.shape[1]:
                        line.set_data(ts, data_array[:, i])
                    else:
                        line.set_data([], [])  # Clear unused lines
                
                plot['ax'].relim()
                plot['ax'].autoscale_view()
                plot['canvas'].draw()

if __name__ == "__main__":
    print("Dont do that\n\n>.>\n\n")