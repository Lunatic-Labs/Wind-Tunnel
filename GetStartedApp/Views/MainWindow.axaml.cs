using System;
using System.Diagnostics;
using Avalonia.Controls;
using Avalonia.Interactivity;

namespace GetStartedApp.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    public void CalculateCelsius(object source, RoutedEventArgs args)
    {
        if (double.TryParse(fahrenheit.Text, out double F))
        {
            double C = (F - 32) * (5d / 9d);
            celsius.Text = C.ToString("0.0");
        }
        else
        {
            celsius.Text = "0";
            fahrenheit.Text = "0";
        }
    }

    public void CalculateFahrenheit(object source, RoutedEventArgs args)
    {
        if (double.TryParse(celsius.Text, out double C))
        {
            double F = C * (9d / 5d) + 32;
            fahrenheit.Text = F.ToString("0.0");
        }
        else
        {
            celsius.Text = "0";
            fahrenheit.Text = "0";
        }
    }
}