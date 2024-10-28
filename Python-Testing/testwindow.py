import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot(self, data):
        self.axes.clear()
        self.axes.plot(data)
        self.axes.set_title("Sample Graph")
        self.axes.grid(True)
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurements and Graphs")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a horizontal layout
        h_layout = QHBoxLayout()

        # Create table for measurements
        self.table = QTableWidget(5, 2)  # 5 rows, 2 columns
        self.table.setHorizontalHeaderLabels(["Data Point", "Value"])
        self.table.setFixedWidth(200)  # Set fixed width for the table

        # Initialize plots list
        self.plots = [PlotCanvas(self) for _ in range(4)]

        # Populate the table after initializing self.plots
        self.populate_table()

        # Create a grid layout for plots
        plot_layout = QGridLayout()
        for i, plot in enumerate(self.plots):
            plot_layout.addWidget(plot, i // 2, i % 2)  # 2 columns of plots

        # Add table and plots layout to horizontal layout
        h_layout.addWidget(self.table)

        # Create a vertical layout for the right side
        right_layout = QVBoxLayout()
        right_layout.addLayout(plot_layout)

        # Add buttons below the table
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.export_button = QPushButton("Export")

        # Connect buttons to functions (placeholders for now)
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.export_button.clicked.connect(self.export)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.export_button)

        right_layout.addLayout(button_layout)

        # Add right layout to the main horizontal layout
        h_layout.addLayout(right_layout)

        # Set the main layout
        central_widget.setLayout(h_layout)

    def populate_table(self):
        data = [("Temperature", 25), ("Pressure", 1.2), ("Humidity", 60), ("Flow", 5), ("Speed", 120)]
        for row, (name, value) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))

        # Populate plots with sample data
        for plot in self.plots:
            plot.plot([1, 2, 3, 4, 5])  # Replace with actual data

    def start(self):
        print("Start button clicked")

    def stop(self):
        print("Stop button clicked")

    def export(self):
        print("Export button clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
