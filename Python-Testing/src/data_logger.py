import csv
import os
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.csv_filename = self._setup_csv_file()
        
    def _setup_csv_file(self):
        """Create and setup CSV file with headers."""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/raw_data_{timestamp}.csv'
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp_301', 'Channel_301', 'Timestamp_302', 'Channel_302', 'Timestamp_303', 'Channel_303'])
        
        return filename

    def log_measurement(self, device_timestamps, measurements):
        """Log a single measurement to CSV file."""
        with open(self.csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writeOut = []
            for index in range(3):
                writeOut.append(device_timestamps[index])
                writeOut.append(measurements[index, 0])
            writer.writerow(writeOut)
