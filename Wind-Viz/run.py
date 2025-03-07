# daq_reader/run.py
import sys
from src.main import DAQReaderApp
from PyQt5 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DAQReaderApp()
    window.show()
    sys.exit(app.exec_())