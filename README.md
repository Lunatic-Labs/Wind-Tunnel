# WindViz LU: Wind Tunnel Data Visualization

A real-time visualization tool for Lipscomb University's RBJCOE Wind Tunnel data analysis.

## Overview

WindViz LU provides researchers and students with intuitive, real-time visualizations of aerodynamic data from wind tunnel experiments. This software streamlines the data collection and analysis process, making it easier to interpret and understand experimental results.

## Features

- Real-time data visualization and monitoring
- Comprehensive data export capabilities
- User-friendly interface optimized for academic research
- Direct integration with Keysight DAQ970A hardware

## Prerequisites

- Python 3.13.0
- Keysight DAQ970A device
- Windows 10 or higher
- Microsoft Visual C++ 14.0 or higher
- NI-VISA
- Keysight IO Libraries (Main and Prerequisites)
- DAQ970A USB driver

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Lunatic-Labs/Wind-Tunnel.git
cd Wind-Tunnel
```

2. Choose your setup method:

### Automatic Setup (Recommended)
*Note: Execution policy needs to be set to 'remotesigned' if not done already

```bash
.\setup.ps1
```

### Manual Setup

1. Create a virtual environment:
```bash
python -m venv myvenv
```

2. Activate the virtual environment:

```bash
myvenv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Launch the application:
```bash
python combined.py
```
Exit the virtual environment:
```bash
deactivate
```

## Hardware Configuration

### Keysight DAQ970A Setup

Configure the following settings to enable USB connectivity:

#### Disable File Sharing
1. Press the Home key
2. Select User Settings
3. Select I/O
4. Select More 1 of 2
5. Select USB settings
6. Set File Access to Off

#### Enable USB SCPI
1. Press the Home key
2. Select User Settings
3. Select I/O
4. Select More 1 of 2
5. Select USB settings
6. Verify USB SCPI is enabled

## Contributing

We welcome contributions! Please contact our development team:

- Sam Wright - [samuel.wright@lipscomb.edu](mailto:samuel.wright@lipscomb.edu)
- Mekeal Brown - [mtbrown@mail.lipscomb.edu](mailto:mtbrown@mail.lipscomb.edu)
- Hayden Dewey - [hcdewey@mail.lipscomb.edu](mailto:hcdewey@mail.lipscomb.edu)
- Maxwell Williams - [mwilliams4@mail.lipscomb.edu](mailto:mwilliams4@mail.lipscomb.edu)

## License

[Add your license information here]
