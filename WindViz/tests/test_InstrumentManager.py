import pytest
from unittest.mock import MagicMock, patch
import pyvisa
import datetime

from instrument_manager import InstrumentManager
import src.instrument_manager as im

def test_init(instrument_manager):
    """
    Test the initialization of the InstrumentManager class.

    Verifies that the InstrumentManager instance is initialized with the correct default values:
    - `connection` is set to `None`.
    - `selected_channels` is set to `[301, 302, 303]`.
    """
    assert instrument_manager.connection is None
    assert instrument_manager.selected_channels == [301, 302, 303]

# ============================= TEST connect() FUNCTION ===============================================
def test_connect_success():
    """
    Test the successful connection to an instrument.

    Verifies that the `connect` method correctly:
    - Lists available resources.
    - Opens a connection to the first valid device.
    - Configures the instrument.
    - Returns `True` on successful connection.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_device = MagicMock()
    mock_device.read.return_value = "DAQ970A,12345,A.01.01"
    mock_device.clear.return_value = None
    
    mock_rm.list_resources.return_value = ['USB0::0x2A8D::0x0101::MY12345678::INSTR']
    mock_rm.open_resource.return_value = mock_device
    manager.rm = mock_rm
    
    with patch.object(InstrumentManager, '_configure_instrument', return_value=None) as mock_configure:
        result = manager.connect()
    
    assert result is True, "Connection should succeed with a valid device"
    mock_rm.list_resources.assert_called_once_with('USB?*INSTR')
    mock_rm.open_resource.assert_called_once_with('USB0::0x2A8D::0x0101::MY12345678::INSTR')
    mock_device.clear.assert_called_once()
    mock_device.write.assert_called_once_with('*IDN?')
    mock_device.read.assert_called_once()
    mock_configure.assert_called_once()

def test_connect_fail():
    """
    Test the `connect` method when no devices are found.

    Verifies that the `connect` method returns `False` when no devices are available.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_rm.list_resources.return_value = []  # No devices
    manager.rm = mock_rm
    
    result = manager.connect()
    
    assert result is False

def test_connect_multiple_devices():
    """
    Test the `connect` method when multiple devices are found.

    Verifies that the `connect` method:
    - Connects to the first valid device when multiple devices are available.
    - Returns `True` on successful connection.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_device1 = MagicMock()
    mock_device1.read.return_value = "DAQ970A,12345,A.01.01"
    mock_device1.clear.return_value = None
    
    mock_device2 = MagicMock()
    mock_device2.read.return_value = "DAQ970A,67890,A.01.01"
    mock_device2.clear.return_value = None
    
    mock_rm.list_resources.return_value = [
        'USB0::0x2A8D::0x0101::MY12345678::INSTR',
        'USB0::0x2A8D::0x0101::MY98765432::INSTR'
    ]
    mock_rm.open_resource.side_effect = [mock_device1, mock_device2]
    manager.rm = mock_rm
    
    with patch.object(InstrumentManager, '_configure_instrument', return_value=None) as mock_configure:
        result = manager.connect()
    
    assert result is True, "Should connect to the first valid device"
    mock_rm.open_resource.assert_called_once_with('USB0::0x2A8D::0x0101::MY12345678::INSTR')
    mock_device1.clear.assert_called_once()
    mock_device1.write.assert_called_once_with('*IDN?')
    mock_device1.read.assert_called_once()
    mock_configure.assert_called_once()

def test_connect_visa_io_error():
    """
    Test the `connect` method when a VisaIOError occurs.

    Verifies that the `connect` method returns `False` when a `VisaIOError` is raised during connection.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_rm.list_resources.return_value = ['USB0::0x2A8D::0x0101::MY12345678::INSTR']
    mock_rm.open_resource.side_effect = pyvisa.errors.VisaIOError(-107380733)
    manager.rm = mock_rm
    
    result = manager.connect()
    
    assert result is False

def test_connect_invalid_device_response():
    """
    Test the `connect` method when the device returns an invalid IDN response.

    Verifies that the `connect` method returns `False` when the device returns an invalid IDN response.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_device = MagicMock()
    mock_device.clear.return_value = None
    mock_device.read.return_value = "BAD_DEVICE"  # Invalid response
    
    mock_rm.list_resources.return_value = ['USB0::0x2A8D::0x0101::MY12345678::INSTR']
    mock_rm.open_resource.return_value = mock_device
    manager.rm = mock_rm
    
    result = manager.connect()
    
    assert result is False, "Should fail with invalid IDN response"
    mock_device.clear.assert_called_once()
    mock_device.write.assert_called_once_with('*IDN?')
    mock_device.read.assert_called_once()

def test_connect_configuration_failure():
    """
    Test the `connect` method when configuration commands fail.

    Verifies that the `connect` method returns `False` when a `VisaIOError` occurs during configuration.
    """
    manager = InstrumentManager()
    mock_rm = MagicMock()
    mock_device = MagicMock()
    mock_device.read.return_value = "DAQ970A,12345,A.01.01"
    mock_device.clear.return_value = None
    
    mock_rm.list_resources.return_value = ['USB0::0x2A8D::0x0101::MY12345678::INSTR']
    mock_rm.open_resource.return_value = mock_device
    manager.rm = mock_rm
    
    with patch.object(InstrumentManager, '_configure_instrument', side_effect=pyvisa.errors.VisaIOError(-107380733)) as mock_configure:
        result = manager.connect()
    
    assert result is False, "Should fail if config raises VisaIOError after IDN"
    

def test_configure_instrument(connected_instrument_manager):
    """
    Test the `_configure_instrument` method directly with a connected manager.

    Verifies that the `_configure_instrument` method correctly sends configuration commands to the instrument.
    """
    mock_connection = connected_instrument_manager.connection
    connected_instrument_manager.selected_channels = [304, 305]
    
    connected_instrument_manager._configure_instrument()
    
    mock_connection.write.assert_any_call('FORM:READ:TIME:TYPE ABS')
    mock_connection.write.assert_any_call('FORM:READ:TIME ON')
    mock_connection.write.assert_any_call('CONF:VOLT:DC 1mV,0.00001,(@304,@305)')
    mock_connection.write.assert_any_call('ROUT:SCAN (@304,@305)')

def test_set_channels_no_connection(instrument_manager):
    """
    Test the `set_channels` method when there is no connection.

    Verifies that the `set_channels` method updates the `selected_channels` attribute without attempting to configure the instrument.
    """
    new_channels = [304, 305, 306]
    instrument_manager.set_channels(new_channels)
    assert instrument_manager.selected_channels == new_channels
    # No connection, so _configure_instrument shouldn’t be called

def test_read_measurements_malformed_data(connected_instrument_manager):
    """
    Test the `read_measurements` method with malformed data.

    Verifies that the `read_measurements` method returns `None` when the data is malformed and cannot be parsed.
    """
    mock_connection = connected_instrument_manager.connection
    # Too few values to parse 3 channels with timestamps
    mock_connection.read.return_value = "0.00123,2024,2,18,12,30,45.123"
    
    result = connected_instrument_manager.read_measurements()
    
    mock_connection.write.assert_called_with('READ?')
    mock_connection.read.assert_called_once()
    assert result is None, "Should return None on malformed data"

def test_read_measurements_invalid_float(connected_instrument_manager):
    """
    Test the `read_measurements` method with invalid float values.

    Verifies that the `read_measurements` method returns `None` when the data contains invalid float values.
    """
    mock_connection = connected_instrument_manager.connection
    # "invalid" can’t be converted to float
    mock_connection.read.return_value = "invalid,2024,2,18,12,30,45.123,0.00456,2024,2,18,12,30,45.234,0.00789,2024,2,18,12,30,45.345"
    
    result = connected_instrument_manager.read_measurements()
    
    mock_connection.write.assert_called_with('READ?')
    mock_connection.read.assert_called_once()
    assert result is None, "Should return None on invalid float conversion"


def test_set_channels(connected_instrument_manager):
    """
    Test the `set_channels` method with a connected instrument.

    Verifies that the `set_channels` method updates the `selected_channels` attribute and sends the appropriate configuration commands to the instrument.
    """
    mock_connection = connected_instrument_manager.connection
    new_channels = [304, 305, 306]
    connected_instrument_manager.set_channels(new_channels)
    
    assert connected_instrument_manager.selected_channels == new_channels
    assert mock_connection.write.called
    write_calls = [call[0][0] for call in mock_connection.write.call_args_list]
    for channel in new_channels:
        assert any(f"@{channel}" in call for call in write_calls), f"Expected @{channel} in calls: {write_calls}"

def test_read_measurements(connected_instrument_manager):
    """
    Test the `read_measurements` method.

    Verifies that the `read_measurements` method correctly reads and parses measurements from the instrument.
    """
    mock_connection = connected_instrument_manager.connection
    mock_connection.read.return_value = "0.00123,2024,2,18,12,30,45.123,0.00456,2024,2,18,12,30,45.234,0.00789,2024,2,18,12,30,45.345"
    
    result = connected_instrument_manager.read_measurements()
    
    mock_connection.write.assert_called_with('READ?')
    mock_connection.read.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == [0.00123, 0.00456, 0.00789]
    assert len(result[1]) == 3
    for ts in result[1]:
        assert isinstance(ts, float)

def test_read_measurements_no_connection(instrument_manager):
    """
    Test the `read_measurements` method when there is no connection.

    Verifies that the `read_measurements` method returns `None` when there is no active connection.
    """
    result = instrument_manager.read_measurements()
    assert result is None

def test_read_measurements_error(connected_instrument_manager):
    """
    Test the `read_measurements` method when an error occurs.

    Verifies that the `read_measurements` method returns `None` when an exception is raised during the read operation.
    """
    mock_connection = connected_instrument_manager.connection
    mock_connection.read.side_effect = Exception("Test error")
    
    result = connected_instrument_manager.read_measurements()
    
    mock_connection.write.assert_called_with('READ?')
    assert result is None

def test_close(connected_instrument_manager):
    """
    Test the `close` method.

    Verifies that the `close` method correctly closes the connection and sets the `connection` attribute to `None`.
    """
    mock_connection = connected_instrument_manager.connection
    connected_instrument_manager.close()
    
    mock_connection.close.assert_called_once()
    assert connected_instrument_manager.connection is None

def test_close_no_connection(instrument_manager):
    """
    Test the `close` method when there is no connection.

    Verifies that the `close` method does not raise an exception when there is no active connection.
    """
    instrument_manager.close()  # Should not raise an exception
