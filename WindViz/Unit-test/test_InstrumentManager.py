import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import datetime

# Add the src directory to sys.path to import instrument_manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from instrument_manager import InstrumentManager

class TestInstrumentManager(unittest.TestCase):
    def setUp(self):
        self.manager = InstrumentManager()
        # Create mock for ResourceManager
        self.mock_rm = MagicMock()
        self.manager.rm = self.mock_rm
        
    def test_init(self):
        """Test that the InstrumentManager initializes correctly."""
        self.assertIsNone(self.manager.connection)
        self.assertEqual(self.manager.selected_channels, [301, 302, 303])
        
    @patch('pyvisa.ResourceManager')
    def test_connect_success(self, mock_resource_manager):
        """Test successful connection to an instrument."""
        # Setup mock device
        mock_device = MagicMock()
        mock_device.read.return_value = "DAQ970A,12345,A.01.01"
        
        # Setup the ResourceManager to return our mock device
        mock_rm = MagicMock()
        mock_rm.list_resources.return_value = ['USB0::0x2A8D::0x0101::MY12345678::INSTR']
        mock_rm.open_resource.return_value = mock_device
        mock_resource_manager.return_value = mock_rm
        
        # Create a new manager to use the mocked ResourceManager
        manager = InstrumentManager()
        
        # Test connect method
        result = manager.connect()
        
        # Verify results
        self.assertTrue(result)
        mock_rm.list_resources.assert_called_once_with('USB?*INSTR')
        mock_rm.open_resource.assert_called_once_with('USB0::0x2A8D::0x0101::MY12345678::INSTR')
        mock_device.write.assert_any_call('*IDN?')
        mock_device.read.assert_called()
        
        # Check that configure commands were called with the appropriate format
        mock_device.write.assert_any_call('FORM:READ:TIME:TYPE ABS')
        mock_device.write.assert_any_call('FORM:READ:TIME ON')
        
    def test_set_channels(self):
        """Test setting new channels."""
        # Create mock connection
        mock_connection = MagicMock()
        self.manager.connection = mock_connection
        
        # Test setting new channels
        new_channels = [304, 305, 306]
        self.manager.set_channels(new_channels)
        
        # Verify results
        self.assertEqual(self.manager.selected_channels, new_channels)
        
        # Check that the _configure_instrument method is called 
        self.assertTrue(mock_connection.write.called)
        
        # Get all the write calls made to the mock
        write_calls = [call[0][0] for call in mock_connection.write.call_args_list]
        
        # Check that at least one call contains each channel with @ prefix
        for channel in new_channels:
            self.assertTrue(any(f"@{channel}" in call for call in write_calls), 
                          f"Expected to find @{channel} in one of the calls: {write_calls}")
        
    def test_read_measurements(self):
        """Test reading measurements."""
        # Create mock connection with properly formatted data
        mock_connection = MagicMock()
        # Format corrected to ensure microsecond is within valid range 0-999999
        mock_connection.read.return_value = "0.00123,2024,2,18,12,30,45.123,0.00456,2024,2,18,12,30,45.234,0.00789,2024,2,18,12,30,45.345"
        self.manager.connection = mock_connection
        
        # Test reading measurements
        result = self.manager.read_measurements()
        
        # Verify results
        mock_connection.write.assert_called_with('READ?')
        mock_connection.read.assert_called_once()
        
        # Check the returned values - only if the result is not None
        if result is not None:
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)  # Should contain values and timestamps
            
            # Check values
            self.assertEqual(result[0], [0.00123, 0.00456, 0.00789])
            
            # Check timestamps
            self.assertEqual(len(result[1]), 3)  # Should have 3 timestamps
            for ts in result[1]:
                self.assertIsInstance(ts, float)
        else:
            self.fail("read_measurements returned None when it shouldn't have")
        
    def test_read_measurements_no_connection(self):
        """Test reading measurements with no connection."""
        # Ensure no connection
        self.manager.connection = None
        
        # Test reading measurements
        result = self.manager.read_measurements()
        
        # Verify results
        self.assertIsNone(result)
        
    def test_read_measurements_error(self):
        """Test reading measurements when an error occurs."""
        # Create mock connection that raises an exception
        mock_connection = MagicMock()
        mock_connection.read.side_effect = Exception("Test error")
        self.manager.connection = mock_connection
        
        # Test reading measurements
        result = self.manager.read_measurements()
        
        # Verify results
        mock_connection.write.assert_called_with('READ?')
        self.assertIsNone(result)
        
    def test_close(self):
        """Test closing the connection."""
        # Create mock connection
        mock_connection = MagicMock()
        self.manager.connection = mock_connection
        
        # Test closing connection
        self.manager.close()
        
        # Verify results
        mock_connection.close.assert_called_once()
        self.assertIsNone(self.manager.connection)
        
    def test_close_no_connection(self):
        """Test closing when there's no connection."""
        # Ensure no connection
        self.manager.connection = None
        
        # Test closing connection
        self.manager.close()  # Should not raise an exception

if __name__ == '__main__':
    unittest.main()