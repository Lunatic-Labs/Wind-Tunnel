import csv
import os
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.csv_filename = self._setup_csv_file()
        self.channel_counts = {'pressure': 0, 'velocity': 0, 'temperature': 0, 'sting': 0}

    def _setup_csv_file(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/raw_data_{timestamp}.csv'
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([])
        
        return filename

    def log_measurement(self, device_timestamps, measurements):
        pressure_vals, velocity_vals, temp_vals, sting_vals = measurements
        
        if not self.channel_counts['pressure']:
            self.channel_counts = {
                'pressure': len(pressure_vals),
                'velocity': len(velocity_vals),
                'temperature': len(temp_vals),
                'sting': len(sting_vals)
            }
            self._write_headers()

        row = []
        total_channels = sum(self.channel_counts.values())
        if len(device_timestamps) != total_channels:
            print(f"Timestamp count ({len(device_timestamps)}) doesn't match channel count ({total_channels})")
            return

        idx = 0
        for p in pressure_vals:
            row.extend([device_timestamps[idx], p])
            idx += 1
        for v in velocity_vals:
            row.extend([device_timestamps[idx], v])
            idx += 1
        for t in temp_vals:
            row.extend([device_timestamps[idx], t])
            idx += 1
        for s in sting_vals:
            row.extend([device_timestamps[idx], s])
            idx += 1

        with open(self.csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def _write_headers(self):
        headers = []
        for ch_type, count in self.channel_counts.items():
            for i in range(count):
                headers.extend([f"Timestamp_{ch_type}_{i+1}", f"Channel_{ch_type}_{i+1}"])
        
        with open(self.csv_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

if __name__ == "__main__":
    print("Dont do that\n\n>.>\n\n")
