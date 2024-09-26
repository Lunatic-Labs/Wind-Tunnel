//using System;
//using System.Collections.Generic;
using Ivi.Visa.Interop;
//using System.Linq.Expressions;
//using Keysight.Visa;

class Program
{
    static void Main()
    {
        string resourceString = "USB0::0x2A8D::0x5001::MY58006867::INSTR";
        ResourceManager manager = new ResourceManager();
        FormattedIO488 connection = new FormattedIO488();
        try
        {
            connection.IO = (IMessage)manager.Open(resourceString, AccessMode.NO_LOCK, 0, "");
            connection.IO.Clear();
            connection.WriteString("*IDN?", true);
            string result = connection.ReadString();
            Console.WriteLine(result);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
        }

        // Create a resource manager
        //using (ResourceManager rm = new ResourceManager())
        //{
        //    try
        //    {
        //        // Find all USB devices
        //        IEnumerable<string> resources = GlobalResourceManager.Find("USB?*");
        //
        //        // Look for the Keysight DAQ
        //        string daqAddress = null;
        //        foreach (string resource in resources)
        //        {
        //            Console.WriteLine($"{resource}");
        //            if (resource.Contains("0x2A8D") && resource.Contains("0x5101")) // Keysight USB identifiers
        //            {
        //                daqAddress = resource;
        //                break;
        //            }
        //        }
        //
        //        if (daqAddress == null)
        //        {
        //            Console.WriteLine("Keysight DAQ not found. Make sure it's connected via USB.");
        //            return;
        //        }
        //
        //        // Open a session to the DAQ
        //        using (IMessageBasedSession daq = (IMessageBasedSession)rm.Open(daqAddress))
        //        {
        //            Console.WriteLine("daq made");
        //            // Query the device identification
        //            daq.FormattedIO.WriteLine("*IDN?");
        //            string idn = daq.FormattedIO.ReadString();
        //            Console.WriteLine($"Connected to: {idn}");
        //
        //            // Configure a voltage measurement on channel 101
        //            daq.FormattedIO.WriteLine("CONF:VOLT:DC 10, 0.003, (@101)");
        //
        //            // Set the trigger source to immediate
        //            daq.FormattedIO.WriteLine("TRIG:SOUR IMM");
        //
        //            // Set the sample count to 1
        //            daq.FormattedIO.WriteLine("SAMP:COUN 1");
        //
        //            // Initiate the measurement
        //            daq.FormattedIO.WriteLine("INIT");
        //
        //            // Wait for the measurement to complete
        //            daq.FormattedIO.WriteLine("*OPC?");
        //            daq.FormattedIO.ReadString();
        //
        //            // Fetch the result
        //            daq.FormattedIO.WriteLine("FETC?");
        //            string result = daq.FormattedIO.ReadString();
        //
        //            Console.WriteLine($"Measurement result: {result} V");
        //        }
        //    }
        //    catch (Exception e)
        //    {
        //        Console.WriteLine($"Error: {e.Message}");
        //    }
        //}
        //
        //Console.WriteLine("Press any key to exit...");
        //Console.ReadKey();
    }
}