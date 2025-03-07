import pyvisa

class DAQInterface:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = None
        self.connected = False
        self.connect()

    def connect(self):
        """Connect to the DAQ970A instrument."""
        devices = self.rm.list_resources('USB?*INSTR')
        
        if devices:
            n = 0
            while True:
                try:
                    self.instrument = self.rm.open_resource(devices[n])
                    self.instrument.clear()
                    self.instrument.write('*IDN?')
                    idn = self.instrument.read()
                    print(f"Connected to: {idn}")

                    #self._configure_instrument()
                    self.connected = True
                    return True
                except pyvisa.errors.VisaIOError:
                    n += 1
        else:
            print("No USB instruments found")
            return False

    def read_channels(self, channel_ids):
        if not self.connected:
            self.connect()
            if not self.connected:
                print("No connection to DAQ970A. Skipping data read.")
                return None  # Return None if connection fails
        
        data = {}
        try:
            for ch in channel_ids:
                # Configure and read (example for DC voltage)
                self.instrument.write(f":CONF:VOLT:DC (@{ch})")
                value = float(self.instrument.query(f":MEAS:VOLT:DC? (@{ch})"))
                data[ch] = value
            return data
        except Exception as e:
            print(f"Error reading channels: {e}")
            self.connected = False  # Mark as disconnected for next attempt
            return None  # Return None on read error

    def __del__(self):
        if self.instrument:
            self.instrument.close()