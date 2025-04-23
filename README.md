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
python main.py
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

## Rustdesk

Rustdesk is a remote desktop application that is used for non-local development. This allows for a remote connection to a computer that is connected to the DAQ970A. Due to latency, it is recommended to develop on your own machine and use the remote connected machine to test any new code.

### Access the Rustdesk connection
1. Install Rustdesk
2. In "Control Remote Desktop" section, insert "254 214 958" for the ID.
3. Insert "WindTunnel2025" for the password.
4. Click connect

## Responsible Parties

- Sam Wright - [samuel.wright@lipscomb.edu](mailto:samuel.wright@lipscomb.edu)
- Mekeal Brown - [mtbrown@mail.lipscomb.edu](mailto:mtbrown@mail.lipscomb.edu)
- Hayden Dewey - [hcdewey@mail.lipscomb.edu](mailto:hcdewey@mail.lipscomb.edu)
- Maxwell Williams - [mwilliams4@mail.lipscomb.edu](mailto:mwilliams4@mail.lipscomb.edu)
