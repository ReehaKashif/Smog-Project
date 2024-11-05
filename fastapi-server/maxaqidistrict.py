
import requests_cache
import pandas as pd
from retry_requests import retry
import openmeteo_requests  # Assuming you have the openmeteo_requests module
import os
import datetime

# Load longitude, latitude, and district values from the uploaded CSV
csv_path = "location_smog1.csv"
location_data = pd.read_csv(csv_path)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.max_cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Set date for current day's data
current_date = datetime.date.today()

# Create an empty list to store the results
result_list = []

# Directory for saving individual district files
output_dir = "Pollutant"
os.makedirs(output_dir, exist_ok=True)

# Iterate over rows in the DataFrame
for index, row in location_data.iterrows():
    latitude = row['Latitude']
    longitude = row['Longitude']
    district = row['District']

    # Make API requests for air quality
    air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    air_quality_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
        "start_date": "2024-11-04",
    "end_date": "2024-11-07"
    }

    # Fetch air quality data
    air_quality_response = openmeteo.weather_api(air_quality_url, params=air_quality_params)[0]
    print(f"Air Quality Data for {latitude}°N, {longitude}°E in {district}")

    # Process air quality data
    air_quality_hourly = air_quality_response.Hourly()
    hourly_pm10 = air_quality_hourly.Variables(0).ValuesAsNumpy()
    hourly_pm2_5 = air_quality_hourly.Variables(1).ValuesAsNumpy()
    hourly_carbon_monoxide = air_quality_hourly.Variables(2).ValuesAsNumpy()
    hourly_nitrogen_dioxide = air_quality_hourly.Variables(3).ValuesAsNumpy()
    hourly_sulphur_dioxide = air_quality_hourly.Variables(4).ValuesAsNumpy()
    hourly_ozone = air_quality_hourly.Variables(5).ValuesAsNumpy()
    hourly_dust = air_quality_hourly.Variables(6).ValuesAsNumpy()

    # Create a DataFrame for hourly data
    time_index = pd.date_range(
        start=pd.to_datetime(air_quality_hourly.Time(), unit="s"),
        end=pd.to_datetime(air_quality_hourly.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=air_quality_hourly.Interval()),
        inclusive="left"
    )

    # Format date and hour
    date_column = time_index.strftime('%m/%d/%Y')
    hour_column = time_index.strftime('%H:%M')

    hourly_data = {
        "date": date_column,
        "hour": hour_column,
        "PM10": hourly_pm10,
        "PM2.5": hourly_pm2_5,
        "Carbon Monoxide": hourly_carbon_monoxide,
        "Nitrogen Dioxide": hourly_nitrogen_dioxide,
        "Sulphur Dioxide": hourly_sulphur_dioxide,
        "Ozone": hourly_ozone,
        "Dust": hourly_dust,
        "Latitude": latitude,
        "Longitude": longitude,
        "District": district
    }

    # Convert hourly data to DataFrame
    hourly_dataframe = pd.DataFrame(data=hourly_data)

    # Calculate AQI based on formula
    hourly_dataframe["AQI"] = (
        (hourly_dataframe["PM10"] * 0.25) +
        (hourly_dataframe["PM2.5"] * 0.25) +
        (hourly_dataframe["Carbon Monoxide"] * 0.1) +
        (hourly_dataframe["Nitrogen Dioxide"] * 0.15) +
        (hourly_dataframe["Sulphur Dioxide"] * 0.1) +
        (hourly_dataframe["Ozone"] * 0.1) +
        (hourly_dataframe["Dust"] * 0.05)
    )

    # Reorder columns
    hourly_dataframe = hourly_dataframe[
        ["date", "hour", "PM10", "PM2.5", "Carbon Monoxide", "Nitrogen Dioxide", "Sulphur Dioxide",
         "Ozone", "Dust", "Latitude", "Longitude", "District", "AQI"]
    ]

    # Save the dataframe to a CSV file in the Colab directory
    csv_filename = f"{output_dir}/hourly_data_{latitude}_{longitude}.csv"
    hourly_dataframe.to_csv(csv_filename, index=False)
    print(f"Air quality data saved to {csv_filename}")

# Combine all individual CSV files into one
combined_csv_path = "/content/combined_hourly_data.csv"

# List all CSV files in the directory
csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
# Initialize a list to store DataFrames
dataframes = []

# Read each CSV file and append to the list
for csv_file in csv_files:
    file_path = os.path.join(output_dir, csv_file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Combine all DataFrames into one
combined_df = pd.concat(dataframes, ignore_index=True)

# Ensure the column order in the combined DataFrame
combined_df = combined_df[
    ["date", "hour", "PM10", "PM2.5", "Carbon Monoxide", "Nitrogen Dioxide", "Sulphur Dioxide",
     "Ozone", "Dust", "Latitude", "Longitude", "District", "AQI"]
]

# Save the combined DataFrame
combined_df.to_csv(combined_csv_path, index=False)
print(f"Combined hourly air quality data saved to {combined_csv_path}")