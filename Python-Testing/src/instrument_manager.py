import pyvisa

class InstrumentManager:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.selected_channels = [301, 302, 303]  # Default channels

    def connect(self):
        """Connect to the DAQ970A instrument."""
        devices = self.rm.list_resources('USB?*INSTR')
        
        if devices:
            self.connection = self.rm.open_resource(devices[2])  # Select the third device
            self.connection.clear()
            self.connection.write('*IDN?')
            idn = self.connection.read()
            print(f"Connected to: {idn}")
            
            self._configure_instrument()
            return True
        else:
            print("No USB instruments found")
            return False

    def _configure_instrument(self):
        """Configure the DAQ970A settings."""
        channel_str = ','.join([f"@{ch}" for ch in self.selected_channels])
        self.connection.write(f'CONF:VOLT:DC 1mV,0.00001,({channel_str})')
        self.connection.write(f'ROUT:SCAN ({channel_str})')

    def set_channels(self, channels):
        """Update the selected channels and reconfigure the instrument."""
        self.selected_channels = channels
        if self.connection:
            self._configure_instrument()

    def read_measurements(self):
        """Read measurements from all channels."""
        if not self.connection:
            return None
            
        try:
            self.connection.write('READ?')
            result = self.connection.read()
            return [float(value) for value in result.split(',')]
        except Exception as ex:
            print(f"Error reading measurements: {ex}")
            return None

    def close(self):
        """Close the instrument connection."""
        if self.connection:
            self.connection.close()
            self.connection = None