# LEDCAVA-WS2812 (rpi_ws281x version)

## Overview

Real-time audio visualization project for WS2812B LED panels using the [rpi_ws281x](https://github.com/jgarff/rpi_ws281x) library.

## Key Features

- Real-time audio visualization
- Multiple visual effects (sci-fi inspired)
- Automatic effect cycling
- Configuration via `settings.json` file

## Hardware Requirements

- Raspberry Pi (tested on Pi 3, 4, and 5)
- WS2812B LED panels
- Adequate 5V power supply

### Connections

| WS2812B | Raspberry Pi |
|---------|--------------|
| VCC     | 5V           |
| GND     | GND          |
| DIN     | GPIO18       |

## Installation

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install build-essential python3-dev
   ```

2. Clone repository:
   ```bash
   git clone https://github.com/thestreamdigger/ledcava-ws2812-rpi_ws281x.git
   cd ledcava-ws2812-rpi_ws281x
   ```

3. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Set permissions:
   ```bash
   chmod +x fix_permissions.sh
   sudo ./fix_permissions.sh
   ```

## Configuration

Edit `settings.json` to adjust:
- Display parameters (brightness, dimensions, GPIO)
- Audio settings
- Effect parameters

## Usage

Start the project:
```bash
sudo python3 main.py
```

Run specific effect:
```bash
sudo python3 main.py --effect BlueWave
```

## License

GNU General Public License v3.0 