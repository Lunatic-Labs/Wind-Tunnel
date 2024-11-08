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
            writer.writerow(['Timestamp', 'Channel_301', 'Channel_302', 'Channel_303'])
        
        return filename

    def log_measurement(self, timestamp, measurements):
        """Log a single measurement to CSV file."""
        with open(self.csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp] + measurements.flatten().tolist())
