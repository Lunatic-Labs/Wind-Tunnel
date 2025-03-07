import sys
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class SimplePlotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Plot Test")
        self.resize(800, 600)
        
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        
        self.data = []
        self.curve = self.plot_widget.plot(pen='y')
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def update_plot(self):
        self.data.append(len(self.data))
        if len(self.data) > 50:
            self.data.pop(0)
        self.curve.setData(self.data)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SimplePlotApp()
    window.show()
    sys.exit(app.exec_())