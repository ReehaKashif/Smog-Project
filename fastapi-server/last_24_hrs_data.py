import pandas as pd
import requests_cache
from retry_requests import retry
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytz import timezone
from datetime import datetime, timedelta

# Load CSV files
try:
    smog_file_path = 'fastapi-server/location_smog.csv'
except FileNotFoundError as e:
    smog_file_path = 'fastapi-server/location_smog.csv'
    
smog_df = pd.read_csv(smog_file_path)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.last24hrscache', expire_after=3600)
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
    pakistan_timezone = timezone('Asia/Karachi')
    now = datetime.now(pakistan_timezone)
    return now

def get_time_range():
    current_time = get_pakistan_time()
    # Get 24 hours before the current time
    start_time = current_time - timedelta(hours=24)
    # Include current hour by adding 1 hour to end time
    end_time = current_time + timedelta(hours=1)
    return start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d')

# Modified function to fetch 24-hour air quality values
def get_24hr_air_quality(latitude, longitude):
    start_date, end_date = get_time_range()
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
        "start_date": start_date,
        "end_date": end_date
    }

    try:
        response = retry_session.get(url, params=params)
        weather_data = response.json()

        # Extract hourly data
        hourly_data = weather_data.get('hourly', {})
        time_array = hourly_data.get('time', [])
        
        # Create a list to store hourly measurements
        hourly_measurements = []
        
        for i in range(len(time_array)):
            hour_data = {
                'time': time_array[i],
                'pm10': hourly_data.get('pm10', [])[i],
                'pm2_5': hourly_data.get('pm2_5', [])[i],
                'carbon_monoxide': hourly_data.get('carbon_monoxide', [])[i],
                'nitrogen_dioxide': hourly_data.get('nitrogen_dioxide', [])[i],
                'sulphur_dioxide': hourly_data.get('sulphur_dioxide', [])[i],
                'ozone': hourly_data.get('ozone', [])[i],
                'dust': hourly_data.get('dust', [])[i]
            }
            hourly_measurements.append(hour_data)
            
        return hourly_measurements
    except Exception as e:
        return {'error': str(e)}

# Function to calculate AQI using the weighted percentages
def calculate_aqi(air_quality_data):
    total_aqi = 0
    for pollutant, weight in weights.items():
        if pollutant in air_quality_data and air_quality_data[pollutant] != 'N/A':
            total_aqi += air_quality_data[pollutant] * weight
    return total_aqi

# Modified function to process each row for 24-hour data
def process_row(row):
    hourly_data = get_24hr_air_quality(row['latitude'], row['longitude'])
    
    if isinstance(hourly_data, list):
        district_hours = []
        for hour_data in hourly_data:
            aqi = calculate_aqi(hour_data)
            district_hours.append({
                'District': row['district'],
                'Time': hour_data['time'],
                'AQI': aqi,
                'Pollutants': {
                    'PM10': hour_data['pm10'],
                    'PM2.5': hour_data['pm2_5'],
                    'Carbon Monoxide': hour_data['carbon_monoxide'],
                    'Nitrogen Dioxide': hour_data['nitrogen_dioxide'],
                    'Sulphur Dioxide': hour_data['sulphur_dioxide'],
                    'Ozone': hour_data['ozone'],
                    'Dust': hour_data['dust']
                }
            })
        return district_hours
    return None

# Modified parallel processing function
def fetch_air_quality_parallel(smog_df):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_row, row) for _, row in smog_df.iterrows()]
        for future in as_completed(futures):
            try:
                district_data = future.result()
                if district_data:
                    results.extend(district_data)
            except Exception as e:
                print(f"Error occurred: {e}")
    return pd.DataFrame(results)

# Modified main function to return 25-hour data (current + past 24 hours)
def get_24hr_data():
    # Fetch 25-hour air quality and AQI data in parallel
    air_quality_df = fetch_air_quality_parallel(smog_df)
    
    # Convert Time column to datetime for proper sorting
    air_quality_df['Time'] = pd.to_datetime(air_quality_df['Time'])
    
    # Create a new DataFrame with the columns we want to save
    save_df = pd.DataFrame({
        'District': air_quality_df['District'],
        'Time': air_quality_df['Time'].dt.strftime('%Y-%m-%d %H:%M'),
        'AQI': air_quality_df['AQI'],  # AQI is already calculated for each data point
        'PM10': air_quality_df['Pollutants'].apply(lambda x: x['PM10']),
        'PM2.5': air_quality_df['Pollutants'].apply(lambda x: x['PM2.5']),
        'Carbon_Monoxide': air_quality_df['Pollutants'].apply(lambda x: x['Carbon Monoxide']),
        'Nitrogen_Dioxide': air_quality_df['Pollutants'].apply(lambda x: x['Nitrogen Dioxide']),
        'Sulphur_Dioxide': air_quality_df['Pollutants'].apply(lambda x: x['Sulphur Dioxide']),
        'Ozone': air_quality_df['Pollutants'].apply(lambda x: x['Ozone']),
        'Dust': air_quality_df['Pollutants'].apply(lambda x: x['Dust'])
    })
    
    # Group by District and Time, taking only the maximum AQI value
    save_df = (save_df.groupby(['District', 'Time'])
               .agg({
                   'AQI': 'max',  # Take max of pre-calculated AQI
                   'PM10': 'first',  # Keep corresponding pollutant values
                   'PM2.5': 'first',
                   'Carbon_Monoxide': 'first',
                   'Nitrogen_Dioxide': 'first',
                   'Sulphur_Dioxide': 'first',
                   'Ozone': 'first',
                   'Dust': 'first'
               })
               .reset_index())
    
    # Sort by District and Time
    save_df = save_df.sort_values(['District', 'Time'])
    
    # Ensure we have exactly 25 hours of data per district
    pakistan_tz = timezone('Asia/Karachi')
    current_time = get_pakistan_time().replace(tzinfo=None)  # Remove timezone info
    start_time = current_time - timedelta(hours=25)
    
    # Convert save_df Time to datetime without timezone
    save_df['Time'] = pd.to_datetime(save_df['Time']).dt.tz_localize(None)
    
    # Filter to keep only the last 25 hours of data
    save_df = save_df[
        (save_df['Time'] >= start_time) & 
        (save_df['Time'] <= current_time)
    ]
    
    # Convert time back to string format
    save_df['Time'] = save_df['Time'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Save to CSV
    try:
        save_df.to_csv('last_24hrs_results.csv', index=False)
    except:
        save_df.to_csv('fastapi-server/last_24hrs_results.csv', index=False)
    
    return save_df

# Run the main function
if __name__ == '__main__':
    result = get_24hr_data()
    print("Results saved to last_24hrs_results.csv")
