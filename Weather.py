import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import argparse
import yaml
import webbrowser
import ctypes
import argparse



def set_console_color(foreground):
    color_dict = {
        'black': 0, 'blue': 1, 'green': 2, 'aqua': 3,
        'red': 4, 'purple': 5, 'yellow': 6, 'white': 7,
        'gray': 8, 'lightblue': 9, 'lightgreen': 10, 'lightaqua': 11,
        'lightred': 12, 'lightpurple': 13, 'lightyellow': 14, 'lightwhite': 15
    }

    ctypes.windll.kernel32.SetConsoleTextAttribute(
        ctypes.windll.kernel32.GetStdHandle(-11), color_dict[foreground]
    )


# Load location URLs from a YAML file
def load_locations():
    with open("locations.yaml", "r") as file:
        data = yaml.safe_load(file)
        return data['locations']


def load_locations_extra():
    with open("LocationsExtra.yaml", "r") as file:
        data = yaml.safe_load(file)
        return data['locationsExtra']





# Fetch and parse the weather page for the given URL
def fetch_weather_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup




def get_current_weather(soup):
    """Fetch and display current weather conditions, including today's forecast summary."""
    weather_card = soup.find('a', {'class': 'cur-con-weather-card'})
    today_card = soup.find('div', {'class': 'today-forecast-card content-module'})

    weather_data = []

    # Extract Current Weather
    if weather_card:
        temperature = weather_card.find('div', {'class': 'temp'})
        description = weather_card.find('span', {'class': 'phrase'})
        realfeel = weather_card.find('div', {'class': 'real-feel'})

        realfeel_temp = None
        if realfeel:
            realfeel_text = realfeel.get_text(strip=True)
            realfeel_temp = ''.join([c for c in realfeel_text if c.isdigit() or c == '°']).strip()

        details_section = soup.find_all('div', {'class': 'spaced-content detail'})
        wind, wind_gusts, air_quality = None, None, None

        for detail in details_section:
            label = detail.find('span', {'class': 'label'})
            value = detail.find('span', {'class': 'value'})
            if label and value:
                label_text = label.get_text(strip=True)
                value_text = value.get_text(strip=True)
                if "Wind" in label_text and "Gusts" not in label_text:
                    wind = value_text
                elif "Wind Gusts" in label_text:
                    wind_gusts = value_text
                elif "Air Quality" in label_text:
                    air_quality = value_text

        # Set the text color to yellow
        set_console_color('yellow')

        print("\n🌦️ Current Weather:")
        weather_data.append(["Temperature", temperature.get_text(strip=True) if temperature else "N/A"])
        weather_data.append(["Description", description.get_text(strip=True) if description else "N/A"])
        weather_data.append(["RealFeel", realfeel_temp if realfeel_temp else "N/A"])
        weather_data.append(["Wind", wind if wind else "N/A"])
        weather_data.append(["Wind Gusts", wind_gusts if wind_gusts else "N/A"])
        weather_data.append(["Air Quality", air_quality if air_quality else "N/A"])

        # Display the weather data in a table format using tabulate
        print(tabulate(weather_data, headers=["Metric", "Value"], tablefmt="grid"))
        print("\n")
    else:
        print("Weather card not found. ❌")

    # Extract Today's Forecast Card data
    forecast_data = []
    if today_card:
        # Get header information
        card_header = today_card.find('div', {'class': 'card-header'})
        forecast_title = card_header.find('h2').get_text(strip=True) if card_header and card_header.find(
            'h2') else "N/A"
        forecast_date = card_header.find('p', {'class': 'sub'}).get_text(
            strip=True) if card_header and card_header.find('p', {'class': 'sub'}) else "N/A"

        # Get body items (typically evening and next day forecasts)
        body_items = today_card.find_all('div', {'class': 'body-item'})

        for item in body_items:
            icon = item.find('img', {'class': 'icon'})
            icon_src = icon['src'] if icon else "N/A"

            description_element = item.find('p')
            if description_element:
                # Extract the text and temperature separately
                description_text = description_element.get_text(strip=True)
                temp_bold = description_element.find('b')

                if temp_bold:
                    temp_text = temp_bold.get_text(strip=True)
                    # Remove the temperature part from the description
                    description_text = description_text.replace(temp_text, '').strip()
                else:
                    temp_text = "N/A"

                forecast_data.append(
                    [description_text, temp_text, icon_src.split('/')[-1] if icon_src != "N/A" else "N/A"])

        # Display the forecast data
        if forecast_data:
            print(f"\n🔮 {forecast_title} - {forecast_date}:")
            print(tabulate(forecast_data, headers=["Forecast", "Temperature", "Icon"], tablefmt="grid"))
        else:
            print("Forecast details not found. ❌")
    else:
        print("Today's forecast card not found. ❌")


def get_hourly_forecast(soup):
    """Fetch and display hourly forecast."""
    hourly_section = soup.find('div', {'class': 'hourly-list__list'})
    hourly_data = []

    if hourly_section:
        hourly_items = hourly_section.find_all('a', {'class': 'hourly-list__list__item'})

        for hour in hourly_items:
            time = hour.find('span', {'class': 'hourly-list__list__item-time'})
            temp = hour.find('span', {'class': 'hourly-list__list__item-temp'})
            precip = hour.find('div', {'class': 'hourly-list__list__item-precip'})
            precip_value = precip.find('span') if precip else None

            if time and temp:
                hourly_data.append([
                    time.get_text(strip=True),
                    temp.get_text(strip=True),
                    precip_value.get_text(strip=True) if precip_value else "0%"
                ])

        print("\n⏳ Hourly Forecast:")
        print(tabulate(hourly_data, headers=["Time", "Temp", "Precip"], tablefmt="grid"))
    else:
        print("Hourly forecast data not found. ❌")


def get_10day_forecast(soup):
    """Fetch and display 10-day weather forecast."""
    daily_section = soup.find('div', {'class': 'daily-list content-module'})
    daily_data = []

    if daily_section:
        daily_items = daily_section.find_all('a', {'class': 'daily-list-item'})

        for day in daily_items:
            date = day.find('p', {'class': 'day'})
            high_temp = day.find('span', {'class': 'temp-hi'})
            low_temp = day.find('span', {'class': 'temp-lo'})
            phrase = day.find('p', {'class': 'no-wrap'})
            night_info = day.find('span', {'class': 'night'})
            precip = day.find('div', {'class': 'precip'})

            night_desc = None
            if night_info:
                night_text = night_info.find('p', {'class': 'no-wrap'})
                if night_text:
                    night_desc = night_text.get_text(strip=True)

            if date and high_temp and low_temp and phrase:
                daily_data.append([
                    date.get_text(strip=True),
                    high_temp.get_text(strip=True),
                    low_temp.get_text(strip=True),
                    phrase.get_text(strip=True),
                    night_desc if night_desc else "N/A",
                    precip.get_text(strip=True) if precip else "0%"
                ])

        print("\n📅 10-Day Forecast:")
        print(tabulate(daily_data, headers=["Day", "High", "Low", "Day Description", "Night Description", "Precip"],
                       tablefmt="grid"))
    else:
        print("10-day forecast data not found. ❌")


def get_sun_moon(soup):
    """Fetch and display sun and moon rise/set times and moon phase."""
    sun_moon_section = soup.find('div', {'class': 'sunrise-sunset content-module'})

    if sun_moon_section:
        sun_item = sun_moon_section.find_all('div', {'class': 'sunrise-sunset__item'})

        if len(sun_item) == 2:
            # Extracting Sun info
            sun_icon = sun_item[0].find('img')['src'] if sun_item[0].find('img') else "N/A"
            sun_phrase = sun_item[0].find('span', {'class': 'sunrise-sunset__phrase'}).get_text(strip=True)
            sun_rise = sun_item[0].find('span', {'class': 'sunrise-sunset__times-value'}).get_text(strip=True)
            sun_set = sun_item[0].find_all('span', {'class': 'sunrise-sunset__times-value'})[1].get_text(strip=True)

            # Extracting Moon info
            moon_icon = sun_item[1].find('img')['src'] if sun_item[1].find('img') else "N/A"
            moon_phrase = sun_item[1].find('span', {'class': 'sunrise-sunset__phrase'}).get_text(strip=True)
            moon_rise = sun_item[1].find_all('span', {'class': 'sunrise-sunset__times-value'})[0].get_text(strip=True)
            moon_set = sun_item[1].find_all('span', {'class': 'sunrise-sunset__times-value'})[1].get_text(strip=True)

            sun_moon_data = [
                ["Sunrise", sun_rise],
                ["Sunset", sun_set],
                ["Sun Icon", sun_icon],
                ["Moon Phase", moon_phrase],
                ["Moon Rise", moon_rise],
                ["Moon Set", moon_set],
                ["Moon Icon", moon_icon]
            ]

            print("\n🌅 Sun & Moon Info:")
            print(tabulate(sun_moon_data, headers=["Metric", "Value"], tablefmt="grid"))
        else:
            print("❌ Could not extract Sun and Moon data.")
    else:
        print("❌ Sun and Moon section not found.")


def get_air_quality(soup):
    """Fetch and display air quality information."""
    air_quality_section = soup.find('a', {'class': 'air-quality-module-wrapper'})
    if air_quality_section:
        air_quality_title = air_quality_section.find('span', {'class': 'air-quality-module__row__category'})
        air_quality_description = air_quality_section.find('p', {'class': 'air-quality-module__statement'})

        air_quality_data = []
        if air_quality_title and air_quality_description:
            air_quality_data.append(["Air Quality", air_quality_title.get_text(strip=True)])
            air_quality_data.append(["Description", air_quality_description.get_text(strip=True)])

            print("\n🌫️ Air Quality:")
            print(tabulate(air_quality_data, headers=["Metric", "Value"], tablefmt="grid"))
        else:
            print("❌ Could not extract air quality data.")
    else:
        print("❌ Air quality data not found.")


def get_allergy_data(soup):
    """Fetch and display allergy data such as pollen levels."""
    allergy_section = soup.find('div', {'class': 'health-activities health-activities-free'})

    if allergy_section:
        allergy_items = allergy_section.find_all('a', {'class': 'health-activities__item show'})

        allergy_data = []

        for item in allergy_items:
            name = item.find('span', {'class': 'health-activities__item__name'})
            category = item.find('span', {'class': 'health-activities__item__category'})

            if name and category:
                name_text = name.get_text(strip=True)
                category_text = category.get_text(strip=True)

                allergy_data.append([name_text, category_text])

        if allergy_data:
            print("\n🌾 Allergy Data:")
            print(tabulate(allergy_data, headers=["Allergy", "Pollen Level"], tablefmt="grid"))
        else:
            print("❌ Could not extract allergy data.")
    else:
        print("❌ Allergy section not found.")


def get_radar_image(soup):
    """Fetch and display the radar image URL, and open it in the browser."""
    radar_image_section = soup.find('img', {'class': 'component-image responsive-img lazy'})

    if radar_image_section:
        radar_url = radar_image_section.get('data-src')
        if radar_url:
            # Open the radar image URL in the default browser
            print(f"\n🌧️ Weather Radar Image: Opening in browser...")
            webbrowser.open(radar_url)
        else:
            print("❌ Radar image URL not found.")
    else:
        print("❌ Radar image section not found.")




# Set up argument parsing for command-line options
parser = argparse.ArgumentParser(description="Weather Scraper CLI")
parser.add_argument("-Location", type=str, help="Location to fetch weather for (e.g., 'Wichita,KS')")
parser.add_argument("-Current", action="store_true", help="Display current weather")
parser.add_argument("-Hour", action="store_true", help="Display hourly forecast")
parser.add_argument("-TenDay", action="store_true", help="Display 10-day forecast")
parser.add_argument("-Air", action="store_true", help="Display air quality information")
parser.add_argument("-SM", action="store_true", help="Display Sun and Moon information")
parser.add_argument("-Allergies", action="store_true", help="Display allergy information (e.g., pollen levels, mold)")
parser.add_argument("-Radar", action="store_true", help="Display weather radar image")
parser.add_argument("-Health", action="store_true", help="Display health data based on the weather")
parser.add_argument("-All", action="store_true", help="Display all available weather information")

args = parser.parse_args()

locations = load_locations()
locations_extra = load_locations_extra()



# Check if location is provided
if not args.Location:
    print("Error: Location argument is required. Use -Location followed by a location name.")
    parser.print_help()
    exit(1)

# Ensure a valid location is provided
if args.Location not in locations:
    print(f"Error: Location '{args.Location}' not found. Please check the location name.")
    exit(1)

# Get the URL for the given location
location_url = locations[args.Location]
soup = fetch_weather_data(location_url)

# Check if any option was selected or if no option was selected
if not (args.Current or args.Hour or args.TenDay or args.Air or args.SM or args.Allergies or args.Radar or args.Health or args.All):
    print("No display option selected. Please select at least one option:")
    parser.print_help()
    exit(1)

# If -All flag is used, show everything
if args.All:
    get_current_weather(soup)
    get_hourly_forecast(soup)
    get_10day_forecast(soup)
    get_air_quality(soup)
    get_sun_moon(soup)
    get_allergy_data(soup)
    get_radar_image(soup)
    get_health_data(soup)
else:
    # Process each selected option
    if args.Current:
        get_current_weather(soup)

    if args.Hour:
        get_hourly_forecast(soup)

    if args.TenDay:
        get_10day_forecast(soup)

    if args.Air:
        get_air_quality(soup)

    if args.SM:
        get_sun_moon(soup)

    if args.Health:
        get_health_data(soup)

    if args.Allergies:
        get_allergy_data(soup)

    if args.Radar:
        get_radar_image(soup)