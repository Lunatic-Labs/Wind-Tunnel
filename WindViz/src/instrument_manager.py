import pyvisa
import datetime

class InstrumentManager:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.selected_channels = [301, 302, 303]  # Default channels

    def connect(self):
        """Connect to the DAQ970A instrument."""
        devices = self.rm.list_resources('USB?*INSTR')
        
        if devices:
            n = 0
            while True:
                try:
                    self.connection = self.rm.open_resource(devices[n])
                    self.connection.clear()
                    self.connection.write('*IDN?')
                    idn = self.connection.read()
                    print(f"Connected to: {idn}")

                    self._configure_instrument()
                    return True
                except pyvisa.errors.VisaIOError:
                    n += 1
        else:
            print("No USB instruments found")
            return False

    def _configure_instrument(self):
        """Configure the DAQ970A settings."""

        # get timestamp included in DAQ970A readings
        self.connection.write('FORM:READ:TIME:TYPE ABS')
        self.connection.write('FORM:READ:TIME ON')

        # configure selected channels to read them all at once
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
            # print(result)
            splitResult = result.split(',')

            timestamps = []
            for index in range(3):
                secondSplit = splitResult[(index * 7) + 6].split('.')
                timestamps.append(
                    datetime.datetime(
                        int(splitResult[(index * 7) + 1]), 
                        int(splitResult[(index * 7) + 2]), 
                        int(splitResult[(index * 7) + 3]), 
                        int(splitResult[(index * 7) + 4]), 
                        int(splitResult[(index * 7) + 5]), 
                        int(secondSplit[0]), 
                        int(secondSplit[1]) * 1000
                        ).timestamp()
                )
            # print(timestamps)

            return [[float(value) for value in [splitResult[0], splitResult[7], splitResult[14]]], timestamps]
        except Exception as ex:
            print(f"Error reading measurements: {ex}")
            return None

    def close(self):
        """Close the instrument connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            

if __name__ == "__main__":
    print("Dont do that\n\n>.>\n\n")