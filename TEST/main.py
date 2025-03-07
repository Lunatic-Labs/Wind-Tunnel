import sys
from PyQt5 import QtWidgets, QtCore
from config_manager import ConfigManager
from daq_interface import DAQInterface
import pyqtgraph as pg
import time

class PlotWidget(QtWidgets.QWidget):
    def __init__(self, title, channels, parent=None):
        super().__init__(parent)
        self.channels = channels
        self.channel_ids = list(channels.keys())
        self.max_points = 50
        self.update_interval = 0.1
        
        self.data = {ch: [] for ch in self.channel_ids}
        self.times = []
        self.start_time = None
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Time (s)')
        layout.addWidget(self.plot_widget)
        
        self.colors = ['r', 'g', 'b', 'y', 'c', 'm', 'w']
        
        self.plot_widget.addLegend()
        self.curves = {}
        for i, (ch_id, ch_info) in enumerate(channels.items()):
            color = self.colors[i % len(self.colors)]
            self.curves[ch_id] = self.plot_widget.plot(pen=pg.mkPen(color, width=2), 
                                                       name=ch_info['name'])
        
        self.plot_widget.setXRange(0, self.max_points * self.update_interval, padding=0)
        self.plot_widget.enableAutoRange('y', True)

    def update_plot(self, new_data):
        if new_data is None:
            print("No valid data received. Plot update skipped.")
            return
        
        if self.start_time is None:
            self.start_time = time.time()
        
        current_time = time.time() - self.start_time
        
        self.times.append(current_time)
        for ch_id in self.channel_ids:
            self.data[ch_id].append(new_data[ch_id])
        
        if len(self.times) > self.max_points:
            self.times.pop(0)
            for ch_id in self.channel_ids:
                self.data[ch_id].pop(0)
        
        for ch_id in self.channel_ids:
            self.curves[ch_id].setData(self.times, self.data[ch_id])
            print(f"Updating {ch_id}: time={self.times[-5:]}, y={self.data[ch_id][-5:]}")
        
        if self.times:
            latest_time = self.times[-1]
            self.plot_widget.setXRange(max(0, latest_time - (self.max_points * self.update_interval)), 
                                     latest_time, padding=0)
        
        self.plot_widget.repaint()

class DAQReaderApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DAQ970A Reader")
        self.resize(1200, 800)

        self.config = ConfigManager()
        self.daq = DAQInterface()
        self.measuring = False  # Track measuring state
        
        self.setup_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        # Timer starts stopped; activated by "Start Measuring"

    def setup_ui(self):
        # Central widget with layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)  # Main vertical layout

        # Control panel for buttons
        control_panel = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Start Measuring")
        self.start_button.clicked.connect(self.start_measuring)
        control_panel.addWidget(self.start_button)

        self.stop_button = QtWidgets.QPushButton("Stop Measuring")
        self.stop_button.clicked.connect(self.stop_measuring)
        self.stop_button.setEnabled(False)  # Disabled until started
        control_panel.addWidget(self.stop_button)

        main_layout.addLayout(control_panel)

        # Plot area
        self.plot_container = QtWidgets.QWidget()
        self.plot_layout = QtWidgets.QGridLayout(self.plot_container)
        main_layout.addWidget(self.plot_container)

        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        load_action = QtWidgets.QAction('Load Config', self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)

        self.plot_widgets = {}
        graph_types = ["Pressure", "Temperature", "Velocity", "STING"]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for g_type, pos in zip(graph_types, positions):
            self.plot_widgets[g_type] = None
            self.plot_layout.addWidget(QtWidgets.QLabel(f"{g_type} (No Config)"), *pos)

    def start_measuring(self):
        if not self.config.channels:
            QtWidgets.QMessageBox.warning(self, "No Config", "Please load a configuration file first.")
            return
        self.measuring = True
        self.timer.start(100)  # Start timer at 100ms interval
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        print("Started measuring")

    def stop_measuring(self):
        self.measuring = False
        self.timer.stop()  # Stop the timer
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        print("Stopped measuring")

    def load_config(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Config", "", "JSON Files (*.json)")
        if file_name:
            self.config.load_config(file_name)
            self.update_plot_layout()

    def update_plot_layout(self):
        for i in reversed(range(self.plot_layout.count())):
            self.plot_layout.itemAt(i).widget().setParent(None)

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, (g_type, channel_ids) in enumerate(self.config.graphs.items()):
            channels_to_plot = {ch: self.config.channels[ch] for ch in channel_ids}
            self.plot_widgets[g_type] = PlotWidget(g_type, channels_to_plot)
            print(f"Adding {g_type} at {positions[i]}")
            self.plot_layout.addWidget(self.plot_widgets[g_type], *positions[i])
            self.plot_widgets[g_type].show()
        self.plot_container.update()
        self.plot_container.show()

    def update_plots(self):
        if not self.measuring or not self.config.channels:
            return
        data = self.daq.read_channels(self.config.channels.keys())
        for g_type, widget in self.plot_widgets.items():
            if widget:
                widget.update_plot(data)
        self.centralWidget().repaint()
        self.repaint()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DAQReaderApp()
    window.show()
    sys.exit(app.exec_())