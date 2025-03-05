import pyvisa
import datetime

class InstrumentManager:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.channels_pressure = []
        self.channels_velocity = []
        self.channels_temp = []
        self.channels_sting = []

    def connect(self):
        devices = self.rm.list_resources('USB?*INSTR')
        if not devices:
            print("No USB instruments found")
            return False
            
        for device in devices:
            try:
                self.connection = self.rm.open_resource(device)
                self.connection.clear()
                self.connection.write('*IDN?')
                idn = self.connection.read()
                
                if "DAQ970A" not in idn:
                    print(f"Invalid response from device {device}")
                    continue
                
                print(f"Connected to: {idn}")
                self._configure_instrument()
                return True
            except pyvisa.errors.VisaIOError:
                print(f"Error connecting to device {device}")
                continue
        return False

    def _configure_instrument(self):
        if not self.connection:
            return
            
        self.connection.write('FORM:READ:TIME:TYPE ABS')
        self.connection.write('FORM:READ:TIME ON')

        all_channels = (self.channels_pressure + self.channels_velocity + 
                       self.channels_temp + self.channels_sting)
        if not all_channels:
            return
            
        channel_str = ','.join([f"@{ch}" for ch in all_channels])
        self.connection.write(f'CONF:VOLT:DC 1mV,0.00001,({channel_str})')
        self.connection.write(f'ROUT:SCAN ({channel_str})')

    def set_channels(self, pressure, velocity, temp, sting):
        self.channels_pressure = pressure
        self.channels_velocity = velocity
        self.channels_temp = temp
        self.channels_sting = sting
        if self.connection:
            self._configure_instrument()

    def read_measurements(self):
        if not self.connection:
            return None
            
        try:
            self.connection.write('READ?')
            result = self.connection.read()
            split_result = result.split(',')

            total_channels = (len(self.channels_pressure) + len(self.channels_velocity) + 
                            len(self.channels_temp) + len(self.channels_sting))
            
            if len(split_result) < total_channels * 7:
                print("Incomplete data received")
                return None

            values = []
            timestamps = []
            for i in range(total_channels):
                values.append(float(split_result[i * 7]))
                second_split = split_result[i * 7 + 6].split('.')
                timestamps.append(
                    datetime.datetime(
                        int(split_result[i * 7 + 1]), 
                        int(split_result[i * 7 + 2]), 
                        int(split_result[i * 7 + 3]), 
                        int(split_result[i * 7 + 4]), 
                        int(split_result[i * 7 + 5]), 
                        int(second_split[0]), 
                        int(second_split[1]) * 1000
                    ).timestamp()
                )

            p_end = len(self.channels_pressure)
            v_end = p_end + len(self.channels_velocity)
            t_end = v_end + len(self.channels_temp)
            
            pressure_vals = values[:p_end]
            velocity_vals = values[p_end:v_end]
            temp_vals = values[v_end:t_end]
            sting_vals = values[t_end:]
            
            return [pressure_vals, velocity_vals, temp_vals, sting_vals], timestamps
            
        except Exception as ex:
            print(f"Error reading measurements: {ex}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

if __name__ == "__main__":
    print("Why'd you do that..\n\n")