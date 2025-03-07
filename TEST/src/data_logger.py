import csv
import time
from pathlib import Path

class DataLogger:
    def __init__(self, log_dir="../logs", filename_prefix="daq_data"):
        # Ensure log directory exists relative to TEST/
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.filename = self.log_dir / f"{filename_prefix}_{timestamp}.csv"
        self.file = None
        self.writer = None
        self.is_logging = False

    def start_logging(self, channel_ids):
        """Start logging with channel IDs as headers."""
        if self.is_logging:
            print("Already logging. Stop current session first.")
            return
        
        try:
            self.file = open(self.filename, 'w', newline='')
            self.writer = csv.writer(self.file)
            # Write header: Timestamp + channel IDs
            header = ['Timestamp'] + [f"Channel {ch}" for ch in channel_ids]
            self.writer.writerow(header)
            self.is_logging = True
            print(f"Started logging to {self.filename}")
        except Exception as e:
            print(f"Failed to start logging: {e}")
            self.is_logging = False

    def log_data(self, data):
        """Log a single row of data with a timestamp."""
        if not self.is_logging or self.writer is None or data is None:
            return
        
        try:
            # Human-readable timestamp
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            # Data row: timestamp + values for each channel
            row = [current_time] + [data[ch] for ch in data.keys()]
            self.writer.writerow(row)
            self.file.flush()  # Ensure data is written immediately
        except Exception as e:
            print(f"Error logging data: {e}")

    def stop_logging(self):
        """Stop logging and close the file."""
        if not self.is_logging:
            return
        
        try:
            if self.file:
                self.file.close()
            self.is_logging = False
            print(f"Stopped logging to {self.filename}")
        except Exception as e:
            print(f"Error stopping logging: {e}")
        finally:
            self.file = None
            self.writer = None

    def __del__(self):
        """Ensure file is closed when object is destroyed."""
        self.stop_logging()