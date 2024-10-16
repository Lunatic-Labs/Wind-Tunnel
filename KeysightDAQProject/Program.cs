using System;
using System.Threading.Tasks;
//using System.Collections.Generic;
using Ivi.Visa;
using Ivi.Visa.Interop;
using System.Linq;
using System.Text;
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
            string result1 = connection.ReadString();
            Console.WriteLine(result1);
            connection.WriteString("SYSTem:BEEPer:STATe Off", true);
            connection.WriteString("SYSTem:BEEPer:STATe?", true);
            string doesClick = connection.ReadString();
            Console.WriteLine(doesClick);
            connection.IO.Clear();
            connection.WriteString("MEAS:VOLT:DC? 1mV,0.00001,(@301)", true);
            string result2 = connection.ReadString();
            Console.WriteLine(result2);
            connection.IO.Clear();
            connection.WriteString("CONF:VOLT:DC 1mV,0.00001,(@301)", true);
            connection.WriteString("FORM:READ:TIME ON", true);
            connection.WriteString("FORM:READ:TIME:TYPE ABS", true);
            //string result2 = connection.ReadString();
            Console.WriteLine("CONF:VOLT:DC");
            var measureTask = () =>
            {
                connection.WriteString($"READ?");
                string result3 = connection.ReadString();
                Console.WriteLine($"{result3}");
                //await Task.Delay(10);
                return result3;
            };

            List<string> resultList = new List<string>();
            for (int i = 0; i < 1000; i++)
            {
                resultList.Add(measureTask());
            }
            FileStream fs = File.Open(Path.Combine(Environment.CurrentDirectory,"test.txt"), FileMode.OpenOrCreate, FileAccess.ReadWrite);
            foreach (var result in resultList)
            {
                fs.Write(Encoding.UTF8.GetBytes(result));
            }
            fs.Close();
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