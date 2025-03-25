import pytest
import json
from unittest.mock import mock_open, patch
from config_manager import ConfigManager  # Updated import path

def test_init_without_config_path():
    """Test initialization without a config path"""
    config_mgr = ConfigManager()
    assert isinstance(config_mgr.channels, dict)
    assert isinstance(config_mgr.graphs, dict)
    assert len(config_mgr.channels) == 0
    assert len(config_mgr.graphs) == 0

def test_init_with_config_path():
    """Test initialization with a config path"""
    mock_config = {
        'channels': {'channel1': 'value1'},
        'graphs': {'graph1': 'value1'}
    }
    mock_file_content = json.dumps(mock_config)
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        config_mgr = ConfigManager('dummy/path/config.json')
        assert config_mgr.channels == mock_config['channels']
        assert config_mgr.graphs == mock_config['graphs']

def test_load_config_success():
    """Test load_config with valid config file"""
    mock_config = {
        'channels': {'channel1': 'value1', 'channel2': 'value2'},
        'graphs': {'graph1': 'value1', 'graph2': 'value2'}
    }
    mock_file_content = json.dumps(mock_config)
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        config_mgr = ConfigManager()
        config_mgr.load_config('dummy/path/config.json')
        assert config_mgr.channels == mock_config['channels']
        assert config_mgr.graphs == mock_config['graphs']

def test_load_config_empty_file():
    """Test load_config with empty config file"""
    mock_config = {}
    mock_file_content = json.dumps(mock_config)
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        config_mgr = ConfigManager()
        config_mgr.load_config('dummy/path/config.json')
        assert config_mgr.channels == {}
        assert config_mgr.graphs == {}

def test_load_config_partial_config():
    """Test load_config with partial config (missing some keys)"""
    mock_config = {'channels': {'channel1': 'value1'}}
    mock_file_content = json.dumps(mock_config)
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        config_mgr = ConfigManager()
        config_mgr.load_config('dummy/path/config.json')
        assert config_mgr.channels == mock_config['channels']
        assert config_mgr.graphs == {}

def test_load_config_file_not_found():
    """Test load_config with file not found error"""
    with patch('builtins.open', side_effect=FileNotFoundError):
        config_mgr = ConfigManager()
        with pytest.raises(FileNotFoundError):
            config_mgr.load_config('nonexistent/path/config.json')

def test_load_config_invalid_json():
    """Test load_config with invalid JSON"""
    invalid_json = "this is not json"
    with patch('builtins.open', mock_open(read_data=invalid_json)):
        config_mgr = ConfigManager()
        with pytest.raises(json.JSONDecodeError):
            config_mgr.load_config('dummy/path/config.json')

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file for testing"""
    config = {
        'channels': {'test_channel': 'value'},
        'graphs': {'test_graph': 'value'}
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return str(config_file)

def test_init_with_real_file(temp_config_file):
    """Test initialization with a real temporary file"""
    config_mgr = ConfigManager(temp_config_file)
    assert config_mgr.channels == {'test_channel': 'value'}
    assert config_mgr.graphs == {'test_graph': 'value'}