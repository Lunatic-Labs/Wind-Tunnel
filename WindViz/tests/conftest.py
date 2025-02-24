import os, sys
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.instrument_manager import InstrumentManager

@pytest.fixture
def instrument_manager():
    """Provide a fresh InstrumentManager with a mocked ResourceManager."""
    manager = InstrumentManager()
    manager.rm = MagicMock()  # Mock pyvisa's ResourceManager
    return manager

@pytest.fixture
def connected_instrument_manager():
    """Provide an InstrumentManager with a mocked connection."""
    manager = InstrumentManager()
    manager.rm = MagicMock()
    manager.connection = MagicMock()  # Mock the connection attribute
    return manager