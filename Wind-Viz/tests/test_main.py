import sys
import pytest
from PyQt5 import QtWidgets, QtCore
from unittest.mock import Mock, patch, MagicMock
from src.main import DAQReaderApp

@pytest.fixture
def app(qtbot):
    with patch('src.main.ConfigManager') as MockConfigManager, \
         patch('src.main.DAQInterface') as MockDAQInterface, \
         patch('src.main.DataLogger') as MockDataLogger, \
         patch('src.main.PlotWidget') as MockPlotWidget:
        
        config = MockConfigManager.return_value
        config.channels = {}
        config.graphs = {}
        config.load_config = Mock()

        daq = MockDAQInterface.return_value
        daq.read_channels = Mock(return_value=None)

        logger = MockDataLogger.return_value
        logger.start_logging = Mock()
        logger.stop_logging = Mock()
        logger.log_data = Mock()

        test_app = DAQReaderApp()
        qtbot.addWidget(test_app)
        
        test_app.plot_widgets = {
            "Pressure": None, "Temperature": None, "Velocity": None, "STING": None
        }
        
        yield test_app, config, daq, logger, MockPlotWidget

def test_init(app, qtbot):
    test_app, _, _, _, _ = app
    assert test_app.windowTitle() == "DAQ970A Reader"
    assert test_app.measuring is False
    assert isinstance(test_app.timer, QtCore.QTimer)
    assert test_app.plot_widgets["Pressure"] is None

def test_setup_ui(app, qtbot):
    test_app, _, _, _, _ = app
    assert test_app.centralWidget().layout().count() == 2
    assert isinstance(test_app.start_button, QtWidgets.QPushButton)
    assert isinstance(test_app.stop_button, QtWidgets.QPushButton)
    assert test_app.start_button.isEnabled()
    assert not test_app.stop_button.isEnabled()
    assert test_app.menuBar().actions()[0].text() == "File"

def test_start_measuring_no_config(app, qtbot, capsys):
    test_app, config, _, logger, _ = app
    config.channels = {}
    
    with patch.object(QtWidgets.QMessageBox, 'warning') as mock_warning:
        test_app.start_measuring()
        mock_warning.assert_called_once_with(test_app, "No Config", "Please load a configuration file first.")
        assert test_app.measuring is False
        logger.start_logging.assert_not_called()
        assert test_app.timer.isActive() is False

def test_start_measuring_with_config(app, qtbot, capsys):
    test_app, config, _, logger, _ = app
    config.channels = {"CH1": "Pressure"}
    
    test_app.start_measuring()
    assert test_app.measuring is True
    logger.start_logging.assert_called_once_with(config.channels.keys())  # Match dict_keys
    assert test_app.timer.isActive()
    assert not test_app.start_button.isEnabled()
    assert test_app.stop_button.isEnabled()
    captured = capsys.readouterr()
    assert "Started measuring" in captured.out

def test_stop_measuring(app, qtbot, capsys):
    test_app, _, _, logger, _ = app
    test_app.measuring = True
    test_app.timer.start(100)
    test_app.start_button.setEnabled(False)
    test_app.stop_button.setEnabled(True)
    
    test_app.stop_measuring()
    assert test_app.measuring is False
    assert not test_app.timer.isActive()
    logger.stop_logging.assert_called_once()
    assert test_app.start_button.isEnabled()
    assert not test_app.stop_button.isEnabled()
    captured = capsys.readouterr()
    assert "Stopped measuring" in captured.out

def test_load_config_file_selected(app, qtbot):
    test_app, config, _, _, _ = app
    with patch.object(QtWidgets.QFileDialog, 'getOpenFileName', return_value=("../config.json", "*.json")):
        with patch.object(test_app, 'update_plot_layout') as mock_update:
            test_app.load_config()
            config.load_config.assert_called_once_with("../config.json")
            mock_update.assert_called_once()

def test_load_config_no_file(app, qtbot):
    test_app, config, _, _, _ = app
    with patch.object(QtWidgets.QFileDialog, 'getOpenFileName', return_value=("", "*.json")):
        with patch.object(test_app, 'update_plot_layout') as mock_update:
            test_app.load_config()
            config.load_config.assert_not_called()
            mock_update.assert_not_called()

def test_update_plot_layout(app, qtbot):
    test_app, config, _, _, MockPlotWidget = app
    config.graphs = {"Pressure": ["CH1"], "Temperature": ["CH2"]}
    config.channels = {"CH1": "Pressure", "CH2": "Temperature"}
    
    mock_widget = Mock()
    MockPlotWidget.return_value = mock_widget
    
    # Mock the layout's addWidget to avoid TypeError
    with patch.object(test_app.plot_layout, 'addWidget') as mock_add_widget:
        test_app.update_plot_layout()
        assert test_app.plot_widgets["Pressure"] == mock_widget
        assert test_app.plot_widgets["Temperature"] == mock_widget
        MockPlotWidget.assert_any_call("Pressure", {"CH1": "Pressure"})
        MockPlotWidget.assert_any_call("Temperature", {"CH2": "Temperature"})
        mock_widget.show.assert_called()
        assert mock_add_widget.call_count == 2

def test_update_plots_not_measuring(app, qtbot):
    test_app, _, daq, logger, _ = app
    test_app.measuring = False
    test_app.update_plots()
    daq.read_channels.assert_not_called()
    logger.log_data.assert_not_called()

def test_update_plots_no_channels(app, qtbot):
    test_app, config, daq, logger, _ = app
    test_app.measuring = True
    config.channels = {}
    test_app.update_plots()
    daq.read_channels.assert_not_called()
    logger.log_data.assert_not_called()

def test_update_plots_with_data(app, qtbot):
    test_app, config, daq, logger, _ = app
    config.channels = {"CH1": "Pressure"}
    config.graphs = {"Pressure": ["CH1"]}
    test_app.measuring = True
    daq.read_channels.return_value = {"CH1": 10.0}
    
    mock_widget = Mock()
    test_app.plot_widgets["Pressure"] = mock_widget
    
    test_app.update_plots()
    daq.read_channels.assert_called_once_with(config.channels.keys())  # Match dict_keys
    logger.log_data.assert_called_once_with({"CH1": 10.0})
    mock_widget.update_plot.assert_called_once_with({"CH1": 10.0})

def test_update_plots_no_data(app, qtbot):
    test_app, config, daq, logger, _ = app
    config.channels = {"CH1": "Pressure"}
    test_app.measuring = True
    daq.read_channels.return_value = None
    
    test_app.update_plots()
    daq.read_channels.assert_called_once_with(config.channels.keys())  # Match dict_keys
    logger.log_data.assert_not_called()

def test_main_execution(qtbot, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['main.py'])
    with patch('src.main.QtWidgets.QApplication') as MockApp, \
         patch('src.main.DAQReaderApp') as MockDAQReaderApp, \
         patch('sys.exit') as mock_exit:
        mock_app_instance = MockApp.return_value
        mock_app_instance.exec_.return_value = 0
        mock_window = MockDAQReaderApp.return_value
        
        # Run the main block directly instead of importing
        from src.main import __name__ as main_name
        if main_name == '__main__':
            import src.main
        else:
            with patch('src.main.__name__', '__main__'):
                import src.main
        
        mock_window.show.assert_called_once()
        mock_app_instance.exec_.assert_called_once()
        mock_exit.assert_called_once_with(0)