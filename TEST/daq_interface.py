import pyvisa

class DAQInterface:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        # Replace with your DAQ's actual resource string
        self.resource_string = "USB0::0x0957::0x5707::MY12345678::INSTR"  # Example USB string
        # For LAN: "TCPIP0::192.168.0.100::INSTR"
        self.instrument = None
        self.connected = False
        self.connect()

    def connect(self):
        try:
            self.instrument = self.rm.open_resource(self.resource_string)
            self.instrument.timeout = 5000  # 5 seconds timeout
            self.instrument.write("*RST")  # Reset the DAQ
            print("Connected to DAQ970A:", self.instrument.query("*IDN?"))
            self.connected = True
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False

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