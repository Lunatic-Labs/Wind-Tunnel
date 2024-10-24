using Ivi.Visa.Interop;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace WPFTest
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        ProgressBar progressBar;
        Progress<int> progress;

        public MainWindow()
        {
            InitializeComponent();
            progressBar = FindName("ProgressBar") as ProgressBar;
            if (progressBar != null)
            {
                progressBar.Minimum = 0;
                progressBar.Maximum = 100;
                progressBar.Value = 0;
                progressBar.UpdateLayout();
            }
        }

        private void Start_Recording_Button_Click(object sender, RoutedEventArgs e)
        {
            Debug.WriteLine("Recording...");
            progressBar.Value = 0;
            progress = new Progress<int>(value => { progressBar.Value = value; });
            Task recording = Task.Run(() => Record(progress));
        }

        private async void Record(IProgress<int> progress)
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
                //connection.WriteString("SYSTem:BEEPer:STATe Off", true);
                //connection.WriteString("SYSTem:BEEPer:STATe?", true);
                //string doesClick = connection.ReadString();
                //Console.WriteLine(doesClick);
                //connection.IO.Clear();
                //connection.WriteString("MEAS:VOLT:DC? 1mV,0.00001,(@305)", true);
                //string result2 = connection.ReadString();
                //Console.WriteLine(result2);
                connection.IO.Clear();
                connection.WriteString("CONF:VOLT:DC 1mV,0.00001,(@301)", true);
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
                await Task.Run(() =>
                {
                    for (int i = 0; i < 100; i++)
                    {
                        resultList.Add(measureTask());
                        progress.Report(i+1);
                    }
                    FileStream fs = File.Create(System.IO.Path.Combine(Environment.CurrentDirectory, "test.csv"));
                    foreach (var result in resultList)
                    {
                        fs.Write(Encoding.UTF8.GetBytes(JoinTimestamp(result)));
                    }
                    fs.Close();

                });
                
                connection.IO.Close();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex.Message}");
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
}