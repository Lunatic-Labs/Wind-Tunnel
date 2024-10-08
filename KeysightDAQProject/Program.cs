//using System;
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
            //connection.IO.Clear();
            //connection.WriteString("DISPlay:ANNotation?", true);
            //string result2 = connection.ReadString();
            //Console.WriteLine(result2);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
        }
    }
}