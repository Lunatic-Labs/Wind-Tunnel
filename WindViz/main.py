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
        self.instrument = InstrumentManager()
        self.gui = DAQ970AGui(self)
        self.config = ChannelDialog(self)         
        self.calibration = CalibrationManager()
        self.data_logger = DataLogger()
        
        self.instrument.connect()

    def measure_task(self):
        """Perform a single measurement cycle."""
        raw_data = self.instrument.read_measurements()
        if not raw_data:
            return

        measurements, device_timestamps = raw_data
        pressure_vals, velocity_vals, temp_vals, sting_vals = measurements
        elapsed_time = time.time() - self.gui.start_time

        # Store raw measurements
        self.gui.pressure_data.append(pressure_vals)
        self.gui.velocity_data.append(velocity_vals)
        self.gui.temp_data.append(temp_vals)
        
        # Calibrate STING data if exactly 3 channels
        if len(sting_vals) == 3:
            sting_config = self.db.get_channel_data("sting").get("configuration", "Side")
            self.calibration.set_configuration(sting_config)
            sting_array = np.array(sting_vals).reshape(3, 1)
            calibrated_sting = self.calibration.calibrate_forces(sting_array).flatten()
            self.gui.sting_data.append(calibrated_sting)
        else:
            self.gui.sting_data.append(sting_vals)  # Raw if not 3 channels
        
        self.gui.timestamps.append(elapsed_time)

        # Log all measurements (raw data)
        self.data_logger.log_measurement(device_timestamps, measurements)

        # Update GUI with raw data for all except STING, which may be calibrated
        self.gui.update_display(measurements, [elapsed_time])

    def run(self):
        self.gui.show()

def main():
    app = QApplication(sys.argv)
    daq_app = DAQ970AApp()
    daq_app.run()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()