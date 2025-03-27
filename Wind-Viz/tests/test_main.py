import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from PyQt5 import QtWidgets, QtTest, QtCore
from main import DAQReaderApp

class MockConfigManager:
    def __init__(self):
        self.channels = {
            'ch1': {'name': 'Channel 1', 'type': 'pressure'},
            'ch2': {'name': 'Channel 2', 'type': 'temperature'}
        }
        self.graphs = {
            'Pressure': ['ch1'],
            'Temperature': ['ch2']
        }
    
    def load_config(self, filename):
        pass

class MockDAQInterface:
    def read_channels(self, channel_keys):
        return {
            'ch1': 10.5,
            'ch2': 25.3
        }

class TestDAQReaderApp(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = DAQReaderApp()
        
        # Patch dependencies with mocks
        self.window.config = MockConfigManager()
        self.window.daq = MockDAQInterface()

    def tearDown(self):
        """Clean up after each test."""
        self.window.close()
        self.app.quit()

    def test_initial_state(self):
        """Test the initial state of the application."""
        # Check window title and size
        self.assertEqual(self.window.windowTitle(), "DAQ970A Reader")
        self.assertEqual(self.window.size().width(), 1200)
        self.assertEqual(self.window.size().height(), 800)

        # Check initial button states
        self.assertTrue(self.window.start_button.isEnabled())
        self.assertFalse(self.window.stop_button.isEnabled())
        self.assertFalse(self.window.measuring)

    def test_start_measuring_without_config(self):
        """Test attempting to start measuring without a configuration."""
        # Clear channels to simulate no config
        self.window.config.channels = {}

        # Capture message box
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            QtTest.QTest.mouseClick(self.window.start_button, QtCore.Qt.LeftButton)
            
            # Verify warning was shown
            mock_warning.assert_called_once()
            self.assertFalse(self.window.measuring)
            self.assertTrue(self.window.start_button.isEnabled())
            self.assertFalse(self.window.stop_button.isEnabled())

    def test_start_and_stop_measuring(self):
        """Test starting and stopping the measurement process."""
        # Capture print outputs
        with patch('builtins.print') as mock_print:
            # Start measuring
            QtTest.QTest.mouseClick(self.window.start_button, QtCore.Qt.LeftButton)
            
            # Verify start state
            self.assertTrue(self.window.measuring)
            self.assertFalse(self.window.start_button.isEnabled())
            self.assertTrue(self.window.stop_button.isEnabled())
            mock_print.assert_called_with("Started measuring")

            # Stop measuring
            QtTest.QTest.mouseClick(self.window.stop_button, QtCore.Qt.LeftButton)
            
            # Verify stop state
            self.assertFalse(self.window.measuring)
            self.assertTrue(self.window.start_button.isEnabled())
            self.assertFalse(self.window.stop_button.isEnabled())
            mock_print.assert_called_with("Stopped measuring")

    def test_update_plots(self):
        """Test the update_plots method."""
        # Setup measuring state and config
        self.window.measuring = True
        
        # Mock the plot widgets
        mock_plot_widget = MagicMock()
        self.window.plot_widgets = {
            'Pressure': mock_plot_widget,
            'Temperature': mock_plot_widget
        }
        
        # Call update_plots
        self.window.update_plots()
        
        # Verify data logging and plot updates
        self.assertTrue(hasattr(self.window.logger, 'log_data'))
        mock_plot_widget.update_plot.assert_called()

    def test_load_config(self):
        """Test loading a configuration file."""
        # Mock file dialog to return a predefined filename
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', 
                   return_value=('../test_config.json', '')):
            # Mock config loading method
            with patch.object(self.window.config, 'load_config') as mock_load:
                # Simulate file selection
                self.window.load_config()
                
                # Verify config was loaded
                mock_load.assert_called_once_with('../test_config.json')

    def test_update_plot_layout(self):
        """Test updating the plot layout based on configuration."""
        # Trigger plot layout update
        self.window.update_plot_layout()
        
        # Verify plot widgets are created
        self.assertIsNotNone(self.window.plot_widgets['Pressure'])
        self.assertIsNotNone(self.window.plot_widgets['Temperature'])

def main():
    unittest.main()

if __name__ == '__main__':
    main()