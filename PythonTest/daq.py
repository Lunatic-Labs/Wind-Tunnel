import pyvisa
def check_daq970a_connection():
    # Create a resource manager
    rm = pyvisa.ResourceManager()
    try:
        # List all connected devices
        resources = rm.list_resources()
        print("Connected resources:", resources)
        # Specify the USB resource string (you may need to adjust this)
        daq970a_address = 'USB0::0x2A8D::0x5001::MY58006867::INSTR'  # Change MY123456 to your device's ID
        # Open a connection to the DAQ970A
        daq970a = rm.open_resource(daq970a_address)
        print("Connecting to: ", daq970a_address)
        # Query the identification string
        idn = daq970a.query('*IDN?')
        print("Connected to:", idn)
        # Close the connection
        daq970a.close()
    except pyvisa.VisaIOError as e:
        print("Could not connect to the DAQ970A:", e)
    except Exception as e:
        print("An error occurred:", e)
if __name__ == '__main__':
    check_daq970a_connection()