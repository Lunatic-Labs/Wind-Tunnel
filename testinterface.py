import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QGroupBox, QScrollArea)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MultiGraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Channel Graphs')
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
        
        test_group = QGroupBox("Test")
        test_layout = QVBoxLayout()
        start_button = QPushButton("Start")
        stop_button = QPushButton("Stop")
        test_layout.addWidget(start_button)
        test_layout.addWidget(stop_button)
        test_group.setLayout(test_layout)
        
        config_group = QGroupBox("Configure")
        config_layout = QVBoxLayout()
        config_button = QPushButton("Configure")
        load_button = QPushButton("Load Configuration")
        config_layout.addWidget(config_button)
        config_layout.addWidget(load_button)
        config_group.setLayout(config_layout)
        
        control_panel.addWidget(test_group)
        control_panel.addWidget(config_group)
        
        main_layout.addLayout(control_panel)
        
        # Sample data
        x = np.linspace(0, 10, 100)
        data = [
            ('Velocity', np.sin(x)),
            ('Pressure', np.cos(x)),
            ('Temperature', np.sin(x) * np.cos(x)),
            ('STING', np.exp(-x/5) * np.sin(x))
        ]

        for channel_name, y in data:
            container = QHBoxLayout()
            
            # Create graph
            fig = Figure(figsize=(10, 3))
            canvas = FigureCanvas(fig)
            canvas.setMinimumHeight(250)
            
            ax = fig.add_subplot(111)
            ax.plot(x, y)
            ax.set_title(channel_name)
            fig.tight_layout()
            
            label = QLabel(channel_name)
            label.setFixedWidth(100)
            
            container.addWidget(canvas)
            container.addWidget(label)
            
            container_widget = QWidget()
            container_widget.setLayout(container)
            container_widget.setMinimumHeight(280)
            
            main_layout.addWidget(container_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiGraphWindow()
    window.show()
    sys.exit(app.exec_())