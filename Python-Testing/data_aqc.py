import pyvisa
import time
import os
from pathlib import Path

def main():
    # Create resource manager
    rm = pyvisa.ResourceManager()
    
    # Find USB devices
    devices = rm.list_resources('USB?*INSTR')
    
    if devices:
        print(f"{devices[0]} was found!")
    else:
        print("No USB instruments found")
        return
        
    try:
        # Open connection to the instrument
        connection = rm.open_resource(devices[0])
        
        # Clear the device
        connection.clear()
        
        # Get device identification
        connection.write('*IDN?')
        result1 = connection.read()
        print(result1)
        
        # Configure beeper state
        connection.write('SYSTem:BEEPer:STATe Off')
        connection.write('SYSTem:BEEPer:STATe?')
        does_click = connection.read()
        print(does_click)
        
        # Clear and take initial measurement
        connection.clear()
        connection.write('MEAS:VOLT:DC? 1mV,0.00001,(@301)')
        result2 = connection.read()
        print(result2)
        
        # Configure voltage measurements
        connection.clear()
        connection.write('CONF:VOLT:DC 1mV,0.00001,(@301)')
        connection.write('FORM:READ:TIME ON')
        connection.write('FORM:READ:TIME:TYPE ABS')
        print("CONF:VOLT:DC")
        
        def measure_task():
            connection.write('READ?')
            result3 = connection.read()
            print(f"{result3}")
            return result3
        
        # Take 1000 measurements
        result_list = []
        for i in range(1000):
            result_list.append(measure_task())
            
        # Write results to file
        file_path = Path(os.getcwd()) / 'test.txt'
        with open(file_path, 'w', encoding='utf-8') as f:
            for result in result_list:
                f.write(result)
                
    except Exception as ex:
        print(f"ERROR: {ex}")
    finally:
        if 'connection' in locals():
            connection.close()
            
if __name__ == "__main__":
    main()