# WindViz LU: Wind Tunnel Data Visualization for Lipscomb University's RBJCOE Wind Tunnel

## Description

WindViz LU is a powerful data visualization tool designed specifically for analyzing wind tunnel data. This software provides researchers and students with intuitive, real-time visualizations of aerodynamic data, enhancing the understanding and analysis of wind tunnel experiments.

## Features

- Real-time data visualization
- Data export capabilities
- User-friendly interface designed for researchers and students

## Installation

TODO: get this process streamlined and fully correct

```bash
git clone https://github.com/Lunatic-Labs/Wind-Tunnel.git
cd WindVizLU
```

## Usage

To run WindViz LU:

TODO: ensure the .csproj file is correct and try to setup new environment with it. Denote those steps below

```bash
dotnet run
```

For detailed usage instructions, please refer to the [User Manual](docs/user_manual.md).

## Requirements

- C#
  - .NET Core 2.0: [Download .NET Core 2.0](https://www.microsoft.com/en-us/download/details.aspx?id=6041)
  - .NET Core 8.0: [Download .NET Core 8.0](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- Keysight IO Suite: [Download Keysight IO Suite](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html)
  *Install both U1 Prerequisite and U1 Main
- Keysight DAQ970A IVI Driver: [Download DAQ970A IVI Driver](https://www.keysight.com/us/en/lib/software-detail/driver/daq970-data-acquisition-system-ivi-driver-2991469.html)
- NI VISA: [Download NI VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html?srsltid=AfmBOopWpHz2JSCe2sas8uBwxCpSWRfKR7p00LZsIhFgAtvyExIZo_Uy#544206)
- AvaloniaUI: [Download AvaloniaUI](https://avaloniaui.net/gettingstarted#installation)

## Setting up Keysight DAQ970A

There are a few setting that will potentially need to be modified to ensure the Keysight DAQ970A can be 
connected via USB.

- File Sharing Off
- USB Mode
- something else?

## Contributors
- Sam Wright samuel.wright@lipscomb.edu
- Mekeal Brown mtbrown@mail.lipscomb.edu
- Hayden Dewey hcdewey@mail.lipscomb.edu
- Maxwell Williams mwilliams4@mail.lipscomb.edu
