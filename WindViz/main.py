import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from src.gui import DAQ970AGui
from src.data_logger import DataLogger
from src.calibration import CalibrationManager
from src.instrument_manager import InstrumentManager
from src.configure_test import ChannelDialog
from src.db import Database

class DAQ970AApp:
    def __init__(self):
        self.db = Database()

        self.gui = DAQ970AGui(self)
        self.config = ChannelDialog(self)        
        self.instrument = InstrumentManager()
        self.calibration = CalibrationManager()
        self.data_logger = DataLogger()
        
        
        # Connect to instrument
        self.instrument.connect()

    def measure_task(self):
        """Perform a single measurement cycle."""
        raw_data = self.instrument.read_measurements()
        if not raw_data:
            return

        current_measurement = np.array(raw_data[0]).reshape((3, 1))
        device_timestamps = raw_data[1]
        elapsed_time = time.time() - self.gui.start_time
        
        # Store and log data
        self.gui.measurements.append(current_measurement)
        self.gui.timestamps.append(elapsed_time)
        self.data_logger.log_measurement(device_timestamps, current_measurement)
        
        # Calculate calibrated forces
        calibrated_force = self.calibration.calibrate_forces(current_measurement)
        self.gui.calibrated_forces.append(calibrated_force)
        
        # Update GUI
        self.gui.update_display(raw_data[0], calibrated_force)
        self.gui.update_plot(self.gui.timestamps, self.gui.calibrated_forces)

    def run(self):
        """Start the application."""
        self.gui.show()

def main():
    app = QApplication(sys.argv)
    daq_app = DAQ970AApp()
    daq_app.run()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()