import requests_cache
import pandas as pd
from retry_requests import retry
import openmeteo_requests 
import os
import datetime
import time


def recent_data_update(start_date:str, end_date:str):
    
    # Load longitude and latitude values from CSV file
    csv_path = "locations.csv"  # Update with your actual CSV file path
    location_data = pd.read_csv(csv_path)

    # creating a data store directory
    os.makedirs("data_store", exist_ok=True)

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    #date
    # startyr, startmonth, startday = start_date.split("-")
    # end_dateyr, end_datemonth, end_dateday = end_date.split("-")
    # start_date = datetime.date(int(startyr), int(startmonth), int(startday))
    # end_date = datetime.date(int(end_dateyr), int(end_datemonth), int(end_dateday))

    # Create an empty list to store the results
    result_list = []

    # Iterate over rows in the DataFrame
    for index, row in location_data.iterrows():
        latitude = row['latitude']  # Replace 'latitude_column_name' with the actual column name
        longitude = row['longitude']  # Replace 'longitude_column_name' with the actual column name

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
            "start_date": start_date,
            "end_date": end_date
        }

        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Append latitude, longitude, and elevation to the result_list
        result_list.append({
            "Latitude": response.Latitude(),
            "Longitude": response.Longitude(),
            "Elevation": response.Elevation()
        })

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
        hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
        hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
        hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()
        hourly_ozone = hourly.Variables(5).ValuesAsNumpy()
        hourly_dust = hourly.Variables(6).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["pm10"] = hourly_pm10
        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
        hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
        hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide
        hourly_data["ozone"] = hourly_ozone
        hourly_data["dust"] = hourly_dust
        hourly_data["latitude"] = latitude
        hourly_data["longitude"] = longitude

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Save the dataframe to a CSV file in Google Drive
        csv_filename = f"./data_store/hourly_data_{latitude}_{longitude}.csv"
        hourly_dataframe.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")

        # adding 5ms delay to avoid rate limiting
        time.sleep(0.2)

    return "Completed"