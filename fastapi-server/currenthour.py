import pandas as pd
import requests_cache
from retry_requests import retry
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytz import timezone
from datetime import datetime

# Load CSV files
try:
    smog_file_path = 'location_smog.csv'
except FileNotFoundError as e:
    smog_file_path = 'fastapi-server/location_smog.csv'
    
smog_df = pd.read_csv(smog_file_path)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.currentcache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

# Weightage percentages for pollutants
weights = {
    'pm10': 0.25,
    'pm2_5': 0.25,
    'carbon_monoxide': 0.10,
    'nitrogen_dioxide': 0.15,
    'sulphur_dioxide': 0.10,
    'ozone': 0.10,
    'dust': 0.05
}

def get_pakistan_time():
    # Get the current date and time in Pakistan
    pakistan_timezone = timezone('Asia/Karachi')
    now = datetime.now(pakistan_timezone)
    
    # Format date with single digit for days 1-9
    day = str(now.day)  # This will give '1' instead of '01'
    month = str(now.month)  # This will give '1' instead of '01'
    formatted_time = f"{month}/{day}/{now.year} {now.hour}:00"
    
    return formatted_time

# Function to fetch current air quality values for a location
def get_current_air_quality(latitude, longitude):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"]
    }

    try:
        response = retry_session.get(url, params=params)
        weather_data = response.json()

        # Extract air quality data from the response
        current = weather_data.get('current', {})
        return {
            'pm10': current.get('pm10', 'N/A'),
            'pm2_5': current.get('pm2_5', 'N/A'),
            'carbon_monoxide': current.get('carbon_monoxide', 'N/A'),
            'nitrogen_dioxide': current.get('nitrogen_dioxide', 'N/A'),
            'sulphur_dioxide': current.get('sulphur_dioxide', 'N/A'),
            'ozone': current.get('ozone', 'N/A'),
            'dust': current.get('dust', 'N/A')
        }
    except Exception as e:
        return {'error': str(e)}

# Function to calculate AQI using the weighted percentages
def calculate_aqi(air_quality_data):
    total_aqi = 0
    for pollutant, weight in weights.items():
        total_aqi += air_quality_data.get(pollutant, 0) * weight
    return total_aqi

# Function to process each row for air quality and AQI
def process_row(row):
    air_quality = get_current_air_quality(row['latitude'], row['longitude'])
    aqi = calculate_aqi(air_quality)
    return {
        'District': row['district'],
        'AQI': aqi,
    }

# Parallel processing using ThreadPoolExecutor
def fetch_air_quality_parallel(smog_df):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_row, row) for _, row in smog_df.iterrows()]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error occurred: {e}")
    return pd.DataFrame(results)

# Main function to return district names and AQI in two lists within a dictionary
def current_main():
    # Fetch air quality and AQI data in parallel
    air_quality_df = fetch_air_quality_parallel(smog_df)
    
    # Group by district and calculate the max AQI
    district_aqi = air_quality_df.groupby('District')['AQI'].max().reset_index()

    # Get current date and hour
    current_time = get_pakistan_time()
    current_date, current_hour = current_time.split(' ')

    # Load existing combined hourly data
    try:
        combined_df = pd.read_csv('combined_hourly_data.csv')
    except FileNotFoundError:
        combined_df = pd.read_csv('fastapi-server/combined_hourly_data.csv')

    # Prepare new data for the current hour
    new_data = pd.DataFrame({
        'date': [current_date] * len(district_aqi),
        'hour': [current_hour] * len(district_aqi),
        'District': district_aqi['District'],
        'AQI': district_aqi['AQI']
    })

    # Append new data to the combined DataFrame
    combined_df = pd.concat([combined_df, new_data], ignore_index=True)
    
    # Drop duplicates while keeping the last occurrence
    combined_df.drop_duplicates(subset=['date', 'hour', 'District'], keep='last', inplace=True)

    # Save updated combined data back to CSV
    try:
        combined_df.to_csv('combined_hourly_data.csv', index=False)
    except:
        combined_df.to_csv('fastapi-server/combined_hourly_data.csv', index=False)

    # Return the updated data
    return {
        'districts': district_aqi['District'].values.tolist(),
        'aqi': district_aqi['AQI'].values.tolist()
    }

# Run the main function
if __name__ == '__main__':
    result = current_main()
    df = pd.DataFrame(result)
    print(df)
