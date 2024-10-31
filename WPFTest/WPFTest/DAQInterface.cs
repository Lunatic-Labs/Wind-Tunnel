using Ivi.Visa.Interop;
using System;
using System.Diagnostics;
using System.IO;
using System.Text;

public class DAQInterface
{
    FormattedIO488 connection;

	public DAQInterface()
	{
        ResourceManager manager = new ResourceManager();
        string[] devices = manager.FindRsrc("USB?*INSTR");
        if (devices.Length > 0)
        {
            Debug.WriteLine(devices[0] + " was found!");
        }
        connection = new FormattedIO488();
        try
        {
            connection.IO = (IMessage)manager.Open(devices[0], AccessMode.NO_LOCK, 0, "");
            connection.IO.Clear();
            connection.WriteString("*IDN?", true);
            string result1 = connection.ReadString();
            Debug.WriteLine(result1);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"ERROR: {ex.Message}");
        }
    }

    ~DAQInterface()
    {
        if (connection.IO != null)
            connection.IO.Close();
    }

    //void ConfigureChannel()
    //{
    //    try
    //    {
    //        connection.WriteString()
    //    }
    //}

    string Read()
    {
        try
        {
            connection.WriteString($"READ?");
            return connection.ReadString();
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"ERROR: {ex}");
            return "ERROR";
        }
    }

    public async void Record(IProgress<int> progress)
    {
        try
        {
            connection.IO.Clear();
            connection.WriteString("CONF:VOLT:DC 1mV,0.00001,(@301)", true);
            connection.WriteString("CONF:VOLT:DC 10V,0.001,(@305)", true);
            connection.WriteString("CONF? (@301,305)", true);
            Debug.WriteLine($"{connection.ReadString()}");
            connection.WriteString("ROUT:SCAN (@301,305)");
            connection.WriteString("FORM:READ:TIME ON", true);
            connection.WriteString("FORM:READ:TIME:TYPE ABS", true);
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
            await Task.Run(async () =>
            {
                for (int i = 0; i < 100; i++)
                {
                    Task<string> measure = Task.Run(measureTask);
                    CancellationToken cancellationToken = new CancellationToken();
                    await measure.WaitAsync(cancellationToken);
                    resultList.Add(measure.Result);
                    Debug.WriteLine($"{measure.Result}");
                    progress.Report(i + 1);
                }
                FileStream fs = File.Create(System.IO.Path.Combine(Environment.CurrentDirectory, "test.csv"));
                Debug.Write("Creating CSV output... ");
                foreach (var result in resultList)
                {
                    fs.Write(Encoding.UTF8.GetBytes(JoinTimestamp(result)));
                }
                Debug.Write("Done!\nClosing file... ");
                fs.Close();
                Debug.WriteLine("Done!");
            });
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"ERROR: {ex.Message}");
        }
    }

    static string JoinTimestamp(string entry)
    {
        int firstComma = entry.IndexOf(",");
        string measurement = entry.Substring(0, firstComma);
        string timestamp = entry.Substring(firstComma + 1);

        string[] splitTimestamp = timestamp.Split(',');
        string date = string.Join('/', splitTimestamp[0], splitTimestamp[1], splitTimestamp[2]);
        string time = string.Join(":", splitTimestamp[3], splitTimestamp[4]);
        time = string.Join(".", time, splitTimestamp[5]);

        return string.Join(',', measurement, date, time);
    }
}
