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
            Task recording = Task.Run(() => DAQInterface.Record(progress));
        }
    }
}