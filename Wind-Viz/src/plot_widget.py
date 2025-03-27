from PyQt5 import QtWidgets
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
            print(ch_info)
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
        
        # Apply coefficient and offset (y = mx + b) to each channel's data
        for ch_id in self.channel_ids:
            # Get raw value from DAQ
            raw_value = new_data[ch_id]
            # Get coefficient and offset from channel config, converting to float
            m = float(self.channels[ch_id]['coefficient'])
            b = float(self.channels[ch_id]['offset'])
            # Apply transformation: y = mx + b
            transformed_value = (m * raw_value) + b
            # Store the transformed value
            self.data[ch_id].append(transformed_value)
        
        # Trim data if exceeding max_points
        if len(self.times) > self.max_points:
            self.times.pop(0)
            for ch_id in self.channel_ids:
                self.data[ch_id].pop(0)
        
        # Update plot curves with transformed data
        for ch_id in self.channel_ids:
            self.curves[ch_id].setData(self.times, self.data[ch_id])
        
        # Adjust X range
        if self.times:
            latest_time = self.times[-1]
            self.plot_widget.setXRange(max(0, latest_time - (self.max_points * self.update_interval)), 
                                     latest_time, padding=0)
        
        self.plot_widget.repaint()