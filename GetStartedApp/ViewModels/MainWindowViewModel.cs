namespace GetStartedApp.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
#pragma warning disable CA1822 // Mark members as static
    public string Greeting => "Welcome to Avalonia! This is my added text.";
#pragma warning restore CA1822 // Mark members as static
}
