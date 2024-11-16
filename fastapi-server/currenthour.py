import pandas as pd
import requests_cache
from retry_requests import retry
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytz import timezone
from datetime import datetime
from connect_db import insert_pivot_data

# Load CSV files
try:
    smog_file_path = 'location_smog.csv'
except FileNotFoundError as e:
    smog_file_path = 'fastapi-server/location_smog.csv'
    
smog_df = pd.read_csv(smog_file_path)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.currentcache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

api_key = "dmjxSgVmXqx5O1Iq"
url = "https://customer-air-quality-api.open-meteo.com/v1/air-quality"

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
    params = {
        "apikey": api_key,
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

    # Prepare new data for the current hour
    new_data = pd.DataFrame({
        'date': [current_date] * len(district_aqi),
        'hour': [current_hour] * len(district_aqi),
        'District': district_aqi['District'],
        'AQI': district_aqi['AQI']
    })
    
    # Pivot the data to have unique districts as columns
    pivot_data = new_data.pivot_table(index=['date', 'hour'], columns='District', values='AQI', fill_value=None)
    # Reset the index to flatten the DataFrame
    pivot_data.reset_index(inplace=True)
    # Adding to DB
    new_data = insert_pivot_data(pivot_data)
    print(new_data)
    # Provided district names
    district_names = [
        'Attock', 'Bahawalnagar', 'Bahawalpur', 'Bhakkar', 'Chakwal', 'Chiniot', 'Dera Ghazi Khan', 
        'Faisalabad', 'Gujranwala', 'Gujrat', 'Hafizabad', 'Jhang', 'Jhelum', 'Kasur', 'Khanewal', 
        'Khushab', 'Lahore', 'Layyah', 'Lodhran', 'Mandi Bahuddin', 'Mianwali', 'Multan', 
        'Muzaffargarh', 'Nankana Sahib', 'Narowal', 'Okara', 'Pakpattan', 'Rahim Yar Khan', 
        'Rajanpur', 'Rawalpindi', 'Sahiwal', 'Sargodha', 'Sheikhupura', 'Sialkot', 'Toba Tek Singh', 
        'Vehari'
    ]

    # Define the columns with 'date' and 'hour' followed by district names
    columns = ['date', 'hour'] + district_names

    # Convert to DataFrame
    df = pd.DataFrame(new_data, columns=columns)
    
    # Melt the DataFrame to get the desired long format
    df_melted = pd.melt(df, id_vars=['date', 'hour'], value_vars=district_names,
                        var_name='District', value_name='AQI')

    # Sort by date, hour, and district for better readability (optional)
    df_melted = df_melted.sort_values(by=['date', 'hour', 'District']).reset_index(drop=True)
    
    result = {
        'districts': df_melted['District'].tolist(),
        'aqi': df_melted['AQI'].tolist()
    }
    return result

# Run the main function
if __name__ == '__main__':
    result = current_main()
    print(result)
