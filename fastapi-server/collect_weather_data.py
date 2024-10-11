import requests_cache
import pandas as pd
from retry_requests import retry
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytz import timezone
from datetime import datetime, timedelta


# Load CSV files
try:
    locations = 'location_smog.csv'
except FileNotFoundError as e:
    locations = 'fastapi-server/location_smog.csv'

def get_pakistan_time():
    # Get the current date and time in Pakistan
    pakistan_timezone = timezone('Asia/Karachi')
    now = datetime.now(pakistan_timezone)
    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def get_average_weather(csv_path=locations):
    # Load CSV data
    location_data = pd.read_csv(csv_path)

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=86400)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

    # Get the current date and time in Pakistan
    current_datetime = datetime.strptime(get_pakistan_time(), '%Y-%m-%d %H:%M:%S')

    # Create an empty list to store the results
    result_list = []

    # Define a function to make API requests for a single location
    def fetch_weather_data(latitude, longitude):
        # Open-Meteo API request for current weather data
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }

        # Make the API request
        response = retry_session.get(url, params=params)
        weather_data = response.json()

        # Extract current temperature and wind speed data
        current_weather = weather_data.get('current_weather', {})
        current_temperature_2m = current_weather.get('temperature', 'N/A')
        current_wind_speed_10m = current_weather.get('windspeed', 'N/A')

        # Return the data in a dictionary format
        return {
            'latitude': latitude,
            'longitude': longitude,
            'time': current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature_2m': current_temperature_2m,
            'wind_speed_10m': current_wind_speed_10m
        }

    # Use ThreadPoolExecutor for parallel API requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a list of futures
        futures = [
            executor.submit(fetch_weather_data, row['latitude'], row['longitude'])
            for _, row in location_data.iterrows()
        ]

        # Collect the results as they complete
        for future in as_completed(futures):
            try:
                result_list.append(future.result())
            except Exception as e:
                print(f"Error occurred: {e}")

    # Convert the list of dictionaries to a DataFrame
    final_weather_df = pd.DataFrame(result_list)
    final_weather_df.columns = final_weather_df.columns.str.capitalize()

    # Load the original CSV file again to merge with weather data
    location_smog = pd.read_csv(csv_path)
    location_smog.columns = location_smog.columns.str.capitalize()

    # Left join the final_weather_df and location_smog dataframes on both Latitude and Longitude columns
    final_df = pd.merge(final_weather_df, location_smog, on=['Latitude', 'Longitude'], how='left')

    # Group by 'District' and calculate the mean for 'Temperature_2m' and 'Wind_speed_10m'
    average_weather_df = final_df.groupby('District').agg({
        'Temperature_2m': 'mean',
        'Wind_speed_10m': 'mean'
    }).reset_index()

    # Add the 'Time' column to the grouped DataFrame
    average_weather_df['Time'] = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    # Return the final processed DataFrame
    return average_weather_df[['District', 'Time', 'Temperature_2m', 'Wind_speed_10m']]