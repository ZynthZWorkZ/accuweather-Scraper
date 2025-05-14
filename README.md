# Weather Scraper

A command-line tool that scrapes and displays detailed weather information for specified locations.

## Features

- Current weather conditions
- Hourly forecast
- 10-day forecast
- Air quality information
- Sun and Moon data
- Allergy information
- Weather radar images
- Health-related weather data

## Requirements

- Python 3.6 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - tabulate
  - pyyaml

## Installation

1. Clone this repository or download the source code
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

The tool requires two YAML files for location configuration:

1. `locations.yaml`: Contains the mapping of location names to their weather URLs
2. `LocationsExtra.yaml`: Contains additional location information

Example `locations.yaml`:
```yaml
locations:
  "Wichita,KS": "https://www.accuweather.com/en/us/wichita/67202/weather-forecast/348426"
  "New York,NY": "https://weather.com/weather/today/l/New+York+NY"
```

## Usage

Run the script from the command line with the following options:

```bash
python Weather.py -Location "LOCATION_NAME" [OPTIONS]
```

### Available Options

- `-Location`: Specify the location to check weather for (required)
- `-Current`: Display current weather
- `-Hour`: Display hourly forecast
- `-TenDay`: Display 10-day forecast
- `-Air`: Display air quality information
- `-SM`: Display Sun and Moon information
- `-Allergies`: Display allergy information
- `-Radar`: Display weather radar image
- `-Health`: Display health-related weather data
- `-All`: Display all available weather information

### Examples

1. Get current weather for Wichita:
```bash
python Weather.py -Location "Wichita,KS" -Current
```

2. Get hourly and 10-day forecast for New York:
```bash
python Weather.py -Location "New York,NY" -Hour -TenDay
```

3. Get all available weather information:
```bash
python Weather.py -Location "Wichita,KS" -All
```

## Output Format

The tool displays information in formatted tables with the following sections:
- 🌦️ Current Weather
- ⏳ Hourly Forecast
- 📅 10-Day Forecast
- 🌅 Sun & Moon Info
- 🌫️ Air Quality
- 🌾 Allergy Data
- 🌧️ Weather Radar

## Notes

- The tool requires an internet connection to fetch weather data
- Weather radar images will open in your default web browser
- Location names must match exactly with those in your `locations.yaml` file
- At least one display option must be selected when running the script

## Troubleshooting

If you encounter any issues:
1. Ensure all required packages are installed
2. Verify your internet connection
3. Check that the location name matches exactly with your configuration
4. Make sure you have selected at least one display option
5. Verify that your YAML configuration files are properly formatted

## License

This project is open source and available under the MIT License. 
