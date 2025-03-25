import pytest
from unittest.mock import Mock, patch, MagicMock
import pyvisa
from daq_interface import DAQInterface

@pytest.fixture
def daq():
    with patch('pyvisa.ResourceManager') as mock_rm:
        daq = DAQInterface()
        yield daq

def test_init_successful_connection(daq):
    assert daq.rm is not None
    assert daq.instrument is not None
    assert daq.connected is True

def test_init_no_devices():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_rm.return_value.list_resources.return_value = ()
        daq = DAQInterface()
        assert daq.connected is False
        assert daq.instrument is None

def test_connect_success():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_instrument = MagicMock()
        mock_rm.return_value.list_resources.return_value = ('USB0::INSTR',)
        mock_rm.return_value.open_resource.return_value = mock_instrument
        mock_instrument.read.return_value = "Test Instrument IDN"
        
        daq = DAQInterface()
        # Reset call counts since __init__ already called connect
        mock_instrument.clear.reset_mock()
        mock_instrument.write.reset_mock()
        mock_instrument.read.reset_mock()
        
        result = daq.connect()
        
        assert result is True
        assert daq.connected is True
        mock_instrument.clear.assert_called_once()
        mock_instrument.write.assert_called_with('*IDN?')
        mock_instrument.read.assert_called_once()

def test_connect_visa_error():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_instrument = MagicMock()
        mock_rm.return_value.list_resources.return_value = ('USB0::INSTR', 'USB1::INSTR')
        
        def open_resource_side_effect(resource):
            if resource == 'USB0::INSTR':
                raise pyvisa.errors.VisaIOError(1073676290)
            return mock_instrument
        
        mock_rm.return_value.open_resource.side_effect = open_resource_side_effect
        mock_instrument.read.return_value = "Test Instrument IDN"
        
        daq = DAQInterface()
        # Reset all mocks to clear calls from __init__
        mock_rm.return_value.open_resource.reset_mock()
        mock_instrument.clear.reset_mock()
        mock_instrument.write.reset_mock()
        mock_instrument.read.reset_mock()
        
        result = daq.connect()
        
        assert result is True
        assert daq.connected is True
        assert mock_rm.return_value.open_resource.call_count == 2
        mock_instrument.clear.assert_called_once()
        mock_instrument.write.assert_called_once_with('*IDN?')
        mock_instrument.read.assert_called_once()

def test_read_channels_success(daq):
    channel_ids = ['101', '102']
    daq.instrument.query.return_value = "5.678"
    
    # Reset write count from initialization
    daq.instrument.write.reset_mock()
    
    result = daq.read_channels(channel_ids)
    
    assert result == {'101': 5.678, '102': 5.678}
    assert daq.instrument.write.call_count == 2
    assert daq.instrument.query.call_count == 2
    assert daq.connected is True

def test_read_channels_not_connected():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_rm.return_value.list_resources.return_value = ()
        daq = DAQInterface()
        result = daq.read_channels(['101'])
        
        assert result is None
        assert daq.connected is False

def test_read_channels_reconnect_success():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_instrument = MagicMock()
        mock_rm.return_value.list_resources.return_value = ('USB0::INSTR',)
        mock_rm.return_value.open_resource.return_value = mock_instrument
        mock_instrument.read.return_value = "Test Instrument IDN"
        mock_instrument.query.return_value = "5.678"
        
        daq = DAQInterface()
        daq.connected = False
        result = daq.read_channels(['101'])
        
        assert result == {'101': 5.678}
        assert daq.connected is True

def test_read_channels_error():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_instrument = MagicMock()
        mock_rm.return_value.list_resources.return_value = ('USB0::INSTR',)
        mock_rm.return_value.open_resource.return_value = mock_instrument
        mock_instrument.read.return_value = "Test Instrument IDN"
        mock_instrument.query.side_effect = Exception("Read error")
        
        daq = DAQInterface()
        result = daq.read_channels(['101'])
        
        assert result is None
        assert daq.connected is False

def test_destructor():
    with patch('pyvisa.ResourceManager') as mock_rm:
        mock_instrument = MagicMock()
        mock_rm.return_value.open_resource.return_value = mock_instrument
        daq = DAQInterface()
        del daq
        mock_instrument.close.assert_called_once()

if __name__ == '__main__':
    pytest.main(['-v', '--cov=DAQInterface', '--cov-report=term-missing'])