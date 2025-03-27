import unittest
import os
import tempfile
import time
import csv
import sys
import io

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_logger import DataLogger  # Adjust import based on actual module location

class TestDataLogger(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up files safely
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                # Try to close any open file handles
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except PermissionError:
                print(f"Could not remove {file_path}. It may be in use.")
        
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            print(f"Could not remove temp directory {self.temp_dir}")

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        logger = DataLogger(log_dir=self.temp_dir)
        
        # Check log directory is created
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # Check filename contains prefix and timestamp
        self.assertTrue('daq_data_' in str(logger.filename))
        self.assertTrue('.csv' in str(logger.filename))
        
        # Check initial state
        self.assertFalse(logger.is_logging)
        self.assertIsNone(logger.file)
        self.assertIsNone(logger.writer)

    def test_start_logging(self):
        """Test starting a logging session."""
        logger = DataLogger(log_dir=self.temp_dir)
        channel_ids = [1, 2, 3]
        
        # Capture print output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            logger.start_logging(channel_ids)
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__
        
        # Get the captured output
        output = captured_output.getvalue().strip()
        
        # Verify logging started
        self.assertTrue(logger.is_logging)
        self.assertIsNotNone(logger.file)
        self.assertIsNotNone(logger.writer)
        
        # Explicitly close the file to ensure writing
        logger.stop_logging()
        
        # Check file contents
        with open(logger.filename, 'r') as f:
            reader = csv.reader(f)
            header = list(reader)[0]
            self.assertEqual(header, ['Timestamp', 'Channel 1', 'Channel 2', 'Channel 3'])
        
        # Check print output
        self.assertTrue(f"Started logging to {logger.filename}" in output)

    def test_start_logging_already_logging(self):
        """Test attempting to start logging when already logging."""
        logger = DataLogger(log_dir=self.temp_dir)
        channel_ids = [1, 2]
        
        # Capture print output for first start
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            logger.start_logging(channel_ids)
        finally:
            sys.stdout = sys.__stdout__
        
        # Capture print output for second start attempt
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            logger.start_logging(channel_ids)
        finally:
            sys.stdout = sys.__stdout__
        
        # Check warning message
        output = captured_output.getvalue().strip()
        self.assertTrue("Already logging. Stop current session first" in output)
        
        # Clean up
        logger.stop_logging()

    def test_log_data(self):
        """Test logging data during an active session."""
        logger = DataLogger(log_dir=self.temp_dir)
        channel_ids = [1, 2, 3]
        
        # Start logging
        logger.start_logging(channel_ids)
        
        # Log some data
        data = {1: 10, 2: 20, 3: 30}
        logger.log_data(data)
        
        # Stop logging and check file contents
        logger.stop_logging()
        
        with open(logger.filename, 'r') as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 2)  # Header + 1 data row
            self.assertEqual(len(reader[1]), 4)  # Timestamp + 3 channel values
            # Check the data values (excluding timestamp)
            self.assertEqual(reader[1][1:], ['10', '20', '30'])

    def test_log_data_without_logging(self):
        """Test logging data when not in logging mode."""
        logger = DataLogger(log_dir=self.temp_dir)
        
        # Try logging without starting
        data = {1: 10, 2: 20}
        logger.log_data(data)  # Should not raise an exception
        
        # Verify no file was created
        self.assertEqual(len(os.listdir(self.temp_dir)), 0)

    def test_stop_logging(self):
        """Test stopping a logging session."""
        logger = DataLogger(log_dir=self.temp_dir)
        channel_ids = [1, 2]
        
        # Start logging
        logger.start_logging(channel_ids)
        
        # Capture print output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            logger.stop_logging()
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__
        
        # Get the captured output
        output = captured_output.getvalue().strip()
        
        # Verify logging stopped
        self.assertFalse(logger.is_logging)
        self.assertIsNone(logger.file)
        self.assertIsNone(logger.writer)
        
        # Check print output
        self.assertTrue(f"Stopped logging to {logger.filename}" in output)

    def test_stop_logging_not_started(self):
        """Test stopping logging when not started."""
        logger = DataLogger(log_dir=self.temp_dir)
        
        # Stop logging when not started (should not raise exception)
        logger.stop_logging()
        
        # Verify state remains unchanged
        self.assertFalse(logger.is_logging)
        self.assertIsNone(logger.file)
        self.assertIsNone(logger.writer)

    def test_destructor(self):
        """Test that file is closed when object is destroyed."""
        # Create the logger
        logger = DataLogger(log_dir=self.temp_dir)
        channel_ids = [1, 2]
        
        # Start logging
        logger.start_logging(channel_ids)
        filename = logger.filename
        
        # Ensure the file is closed
        logger.stop_logging()
        
        # Verify file exists and can be opened/read
        self.assertTrue(os.path.exists(filename))
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            # Verify header exists
            header = next(reader)
            self.assertEqual(header, ['Timestamp', 'Channel 1', 'Channel 2'])

def main():
    unittest.main()

if __name__ == '__main__':
    main()