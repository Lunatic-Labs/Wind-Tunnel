using System;
using System.Threading.Tasks;
//using System.Collections.Generic;
using Ivi.Visa;
using Ivi.Visa.Interop;
using System.Linq;
//using System.Linq.Expressions;
//using Keysight.Visa;

class Program
{
    static void Main()
    {        
        ResourceManager manager = new ResourceManager();
        string[] devices = manager.FindRsrc("USB?*INSTR");
        if (devices.Length > 0)
        {
            Console.WriteLine(devices[0] + " was found!");
        }
        FormattedIO488 connection = new FormattedIO488();
        try
        {
            connection.IO = (IMessage)manager.Open(devices[0], AccessMode.NO_LOCK, 0, "");
            connection.IO.Clear();
            connection.WriteString("*IDN?", true);
            string result = connection.ReadString();
            Console.WriteLine(result);
            connection.WriteString("SYSTem:BEEPer:STATe OFF", true);
            connection.WriteString("SYSTem:BEEPer:STATe?", true);
            string doesClick = connection.ReadString();
            Console.WriteLine(doesClick);
            var measureTask = async () =>
            {
                connection.IO.Clear();
                connection.WriteString("MEAS:VOLT:DC? 1mV,0.00001,(@301)", true);
                string result2 = connection.ReadString();
                Console.WriteLine(result2);
                await Task.Delay(10);
                return result2;
            };
            for (int i = 0; i < 30; i++)
                Task.Run(measureTask).Wait();
            //connection.IO.Clear();
            //connection.WriteString("ACQ:VOLT:DC MIN,DEF,DEF,(@301)", true);
            //connection.WriteString("MEAS:VOLT:DC? 1mV,0.00001,(@301)", true);
            //string result2 = connection.ReadString();
            //Console.WriteLine(result2);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
        }
    }
}