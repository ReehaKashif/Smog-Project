from fastapi import FastAPI, Query ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta
import random  # Add this import at the top of your file
from collect_weather_data import get_average_weather
from currenthour import current_main
from pollutant_contribution import process_openmeteo_data
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests_cache
import pandas as pd
from retry_requests import retry
import openmeteo_requests
import os
from connect_db import fetch_hourly_aqi_from_db, load_db_and_group_by_district
from typing import Optional, List
from octoberapiautomisation import process_air_quality_data

from fastapi import BackgroundTasks

app = FastAPI()

# Allow all origins (unsafe for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV files
try:
    LastMonth = pd.read_csv("LastMonth.csv")
    forecasted_pollutant_df = pd.read_csv('new_xgb_hr_forecasts.csv')
    forecasted_pollutants = pd.read_csv('combined_forecast.csv')
    latest_forecast_df = pd.read_csv("new_xgb_hr_forecasts.csv")
    latest_daily_forecast_df = pd.read_csv("new_xgb_daily_forecasts.csv")
    daily_forecast =  pd.read_csv('new_xgb_daily_forecasts.csv')
    last_year_data = pd.read_csv('new_last_year_daily_data.csv')
    OctoberSource =  pd.read_csv('Octapi.csv')
    miscellaneous = pd.read_excel('MiscellaneousPtsData v1.xlsx')
    daily_aqi_min_max = pd.read_csv("daily_aqi_summary.csv")
except FileNotFoundError as e:
    LastMonth = pd.read_csv("fastapi-server/LastMonth.csv")
    forecasted_pollutant_df = pd.read_csv('fastapi-server/new_xgb_hr_forecasts.csv')
    forecasted_pollutants = pd.read_csv('fastapi-server/combined_forecast.csv')
    latest_forecast_df = pd.read_csv("fastapi-server/new_xgb_hr_forecasts.csv")
    latest_daily_forecast_df = pd.read_csv("fastapi-server/new_xgb_daily_forecasts.csv")
    daily_forecast =  pd.read_csv('fastapi-server/new_xgb_daily_forecasts.csv')
    last_year_data = pd.read_csv('fastapi-server/new_last_year_daily_data.csv')
    OctoberSource =  pd.read_csv('fastapi-server/Octapi.csv')
    miscellaneous = pd.read_excel('fastapi-server/MiscellaneousPtsData.xlsx')
    daily_aqi_min_max = pd.read_csv("fastapi-server/daily_aqi_summary.csv")

def get_pakistan_time():
    # Example of getting the current date and time in Pakistan
    now = datetime.now(timezone('Asia/Karachi'))
    # returning it in this format '2024-07-01 00:00:00'
    formatted_time = now.strftime('%Y-%m-%d %H:00:00')
    print(formatted_time)
    return formatted_time


# Function to get AQI color and color code based on value
def get_AQI_color(aqi):
    if aqi <= 50:
        return 'Green', '#00FF00'
    elif aqi <= 100:
        return 'Yellow', '#FFFF00'
    elif aqi <= 150:
        return 'Orange', '#FFA500'
    elif aqi <= 200:
        return 'Red', '#FF0000'
    elif aqi <= 300:
        return 'Purple', '#800080'
    else:
        return 'Maroon', '#800000'


color_palette = [
  "#00FF00", "#24FF00", "#48FF00", "#6CFF00", "#90FF00", "#B4FF00",
  "#D8FF00", "#FCFF00", "#FFF500", "#FFEB00", "#FFE100", "#FFD700",
  "#FFCC00", "#FFC200", "#FFB800", "#FFAD00", "#FFA300", "#FF9900",
  "#FF8E00", "#FF8400", "#FF7A00", "#FF6F00", "#FF6500", "#FF5B00",
  "#FF5100", "#FF4600", "#FF3C00", "#FF3200", "#FF2800", "#FF1D00",
  "#FF1300", "#FF0900", "#FF0000", "#F50000", "#EB0000", "#E10000",
]


# Define the pollutant to districts mapping
pollutant_districts = {
    "Vehicle": [
        "Attock", "Faisalabad", "Lahore", "Gujranwala", "Rawalpindi", 
        "Sialkot", "Khanewal", "Narowal"
    ],
    "Industry": [
        "Faisalabad", "Gujranwala", "Sialkot", "Lahore", "Sheikhupura", 
        "Multan", "Jhang", "Mandi Bahuddin", "Nankana Sahib", "Chiniot"
    ],
    "Agriculture": [
        "Bahawalpur", "Rahim Yar Khan", "Lodhran", "Kasur", "Okara", 
        "Pakpattan", "Vehari", "Sahiwal", "Dera Ghazi Khan", "Muzaffargarh", 
        "Bhakkar", "Chakwal", "Bahawalnagar", "Layyah", "Khushab", 
        "Hafizabad", "Toba Tek Singh"
    ],
    "Construction": [
        "Gujranwala", "Gujrat", "Lahore", "Sialkot", "Rawalpindi", 
        "Faisalabad", "Sargodha", "Sahiwal", "Mianwali", "Jhelum"
    ],
    "Miscellaneous": [
        "Dera Ghazi Khan", "Rahim Yar Khan", "Bahawalpur", "Muzaffargarh", 
        "Rajanpur", "Layyah", "Mianwali", "Swat", "Bhakkar", "Lodhran"
    ]
}

@app.get("/api/pakistan_time")
def get_pakistan_time_endpoint():
    """
    Endpoint to get the current time in Pakistan.
    """
    return {"pakistan_time": get_pakistan_time()}
    

@app.get("/api/districts_aqi_color")
def get_districts_aqi_color(use_api=True):
    """
    Endpoint to get the AQI and color for each district at a specific time.
    """
    try:
        # Filter the DataFrame by the given time
        # convert the time to date time format
        if use_api==False:
            time = get_pakistan_time()
            filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['Date'] == time]
            # reset the index
            filtered_df = filtered_df.reset_index(drop=True)
            # print(filtered_df)
            
            if filtered_df.empty:
                raise HTTPException(status_code=404, detail="No data found for the specified time.")
            
            # sort in ascending order
            filtered_df = filtered_df.sort_values(by='Final_aqi')
            
            # Ensure unique districts
            unique_districts_df = filtered_df.drop_duplicates(subset=['District'])
        
            # Assign colors based on AQI and prepare the response
            response = []
            for index, row in unique_districts_df.iterrows():
                color_name, color_code = get_AQI_color(row["Final_aqi"])
                response.append({
                    "district": row["District"],
                    "aqi": row["Final_aqi"],
                    "aqi_name": color_name,  # Assuming color_name is the AQI name
                    "color_code": color_code
                })
            
            return {"districts_aqi_color": response}
        else: 
            current = current_main()
            df = pd.DataFrame(current)
            # Assign colors based on AQI and prepare the response
            response = []
            for index, row in df.iterrows():
                color_name, color_code = get_AQI_color(row["aqi"])
                response.append({
                    "district": row["districts"],
                    "aqi": row["aqi"],
                    "aqi_name": color_name,  # Assuming color_name is the AQI name
                    "color_code": color_code
                })
            
            return {"districts_aqi_color": response}
            
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aqi_status")
def get_aqi_status(use_api=True):
    """
    Endpoint to get the AQI status including best and worst district, highest pollutant, and cause of pollutant.
    """
    try:
        if use_api==False:
            time = get_pakistan_time()
            # Filter the DataFrame by the given time
            filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['Date'] == time]
            
            if filtered_df.empty:
                raise HTTPException(status_code=404, detail="No data found for the specified time.")
            
            # sort in ascending order
            filtered_df = filtered_df.sort_values(by='Final_aqi')
            
            # ensure unique districts
            filtered_df = filtered_df.drop_duplicates(subset=['District'])
            
            # Find the district with the lowest (best) AQI
            best_district_row = filtered_df.loc[filtered_df['Final_aqi'].idxmin()]
            best_district = {"district": best_district_row["District"], "aqi": best_district_row["Final_aqi"]}
            
            # Find the district with the highest (worst) AQI
            worst_district_row = filtered_df.loc[filtered_df['Final_aqi'].idxmax()]
            worst_district = {"district": worst_district_row["District"], "aqi": worst_district_row["Final_aqi"]}
            
            # Set highest pollutant and cause (as per provided logic)
            highest_pollutant = "Carbon Monoxide"
            cause_of_pollutant = "Vehicle and Industry"
            
            # Prepare the response
            response = {
                "best_district": best_district,
                "worst_district": worst_district,
                "highest_pollutant": highest_pollutant,
                "cause_of_pollutant": cause_of_pollutant
            }
            
            return response
        else: 
            current = current_main()
            df = pd.DataFrame(current)
            # Find the district with the lowest (best) AQI
            best_district_row = df.loc[df['aqi'].idxmin()]
            best_district = {"district": best_district_row["districts"], "aqi": best_district_row["aqi"]}
            
            # Find the district with the highest (worst) AQI
            worst_district_row = df.loc[df['aqi'].idxmax()]
            worst_district = {"district": worst_district_row["districts"], "aqi": worst_district_row["aqi"]}
            
            # Set highest pollutant and cause (as per provided logic)
            highest_pollutant = "Carbon Monoxide"
            cause_of_pollutant = "Vehicle and Industry"
            
            # Prepare the response
            response = {
                "best_district": best_district,
                "worst_district": worst_district,
                "highest_pollutant": highest_pollutant,
                "cause_of_pollutant": cause_of_pollutant
            }
            
            return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/map_ranking")
def get_map_ranking(use_api=True):
    """
    Endpoint to get the AQI ranking of districts and assign colors based on the provided color palette.
    """
    try:
        if use_api == False:
            time = get_pakistan_time()
            # Filter the DataFrame by the given time
            filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['Date'] == time]
            
            if filtered_df.empty:
                raise HTTPException(status_code=404, detail="No data found for the specified time.")
            
            # sort in ascending order
            filtered_df = filtered_df.sort_values(by='Final_aqi')
            
            # Ensure unique districts and sort by AQI in ascending order
            sorted_df = filtered_df.drop_duplicates(subset=['District']).sort_values(by='Final_aqi')
        
            # selecting the needed columns
            sorted_df = sorted_df[['District', 'Final_aqi']].reset_index(drop=True)
            # Assign colors based on the sorted order
            response = []
            for index, row in sorted_df.iterrows():
                # preparing the response
                response.append({
                    "district": row["District"],
                    "aqi": row["Final_aqi"],
                    "color": color_palette[index]
                })
            
            return {"map_ranking": response}
        else: 
            current = current_main()
            df = pd.DataFrame(current)
            # sort in ascending order
            df = df.sort_values(by='aqi')
            # Ensure unique districts
            unique_districts_df = df.drop_duplicates(subset=['districts']).sort_values(by='aqi')
            
            # selecting the needed columns
            sorted_df = unique_districts_df[['districts', 'aqi']].reset_index(drop=True)
            # Assign colors based on the sorted order
            response = []
            for index, row in sorted_df.iterrows():
                # preparing the response
                response.append({
                    "district": row["districts"],
                    "aqi": row["aqi"],
                    "color": color_palette[index]
                })
            
            return {"map_ranking": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/historical_data")
def get_historical_data(
    district: str = Query(..., description="District name")
):
    """
    Endpoint to get historical AQI data for a given district for the last 2 months,
    including recent historical forecasts from 7-day and 14-day lag data using last year's data.
    """
    time = get_pakistan_time()
    time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').date()

    # Set duration to 2 months
    start_date = time_dt - timedelta(days=60)
    
    # Rename 'Final_AQI' to 'Final_aqi' in last_year_data
    last_year_data_renamed = last_year_data.rename(columns={'Final_AQI': 'Final_aqi'})
    
    # Combine pollutant data and last year data for historical data
    historical_data = pd.concat([daily_forecast, last_year_data_renamed])
    
    # Ensure 'Date' column exists and is in the correct format
    if 'Date' not in historical_data.columns:
        raise ValueError("'Date' column not found in the data")
    
    # Convert 'Date' to datetime, handling different formats
    historical_data['Date'] = pd.to_datetime(historical_data['Date'])

    # Filter historical data
    filtered_df = historical_data[
        (historical_data['Districts'] == district) &
        (historical_data['Date'].dt.date >= start_date) &
        (historical_data['Date'].dt.date <= time_dt)
    ]
    
    # Calculate the corresponding dates for last year
    last_year_date = time_dt.replace(year=time_dt.year - 1)
    last_year_7d_start = last_year_date - timedelta(days=7)
    last_year_14d_start = last_year_date - timedelta(days=14)

    # Get last 7 days of last year's data
    forecast_7d = last_year_data_renamed[
        (last_year_data_renamed['Districts'] == district) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date > last_year_7d_start) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date <= last_year_date)
    ]

    # Get last 14 days of last year's data
    forecast_14d = last_year_data_renamed[
        (last_year_data_renamed['Districts'] == district) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date > last_year_14d_start) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date <= last_year_date)
    ]

    if filtered_df.empty and forecast_7d.empty and forecast_14d.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
    
    # Prepare response data
    historical_dates = filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    historical_aqi = pd.Series(filtered_df['Final_aqi']).replace([np.inf, -np.inf], np.nan).interpolate().fillna(method='bfill').tolist()
    
    forecast_7d_dates = pd.to_datetime(forecast_7d['Date']).dt.strftime('%Y-%m-%d').tolist()
    forecast_7d_aqi = pd.Series(forecast_7d['Final_aqi']).replace([np.inf, -np.inf], np.nan).interpolate().fillna(method='bfill').tolist()
    
    forecast_14d_dates = pd.to_datetime(forecast_14d['Date']).dt.strftime('%Y-%m-%d').tolist()
    forecast_14d_aqi = pd.Series(forecast_14d['Final_aqi']).replace([np.inf, -np.inf], np.nan).interpolate().fillna(method='bfill').tolist()

    # Return the data as a JSON response
    return {
        "historical": {"date": historical_dates, "aqi": historical_aqi},
        "forecast_7d": {"date": forecast_7d_dates, "aqi": forecast_7d_aqi},
        "forecast_14d": {"date": forecast_14d_dates, "aqi": forecast_14d_aqi}
    }

@app.get("/api/last_year")
def get_last_year_data(
    district: str = Query(..., description="District name")
):
    """
    Endpoint to get last year's AQI data for a given district for the last 2 months
    and the next 2 months from the corresponding date last year.
    """
    # Get current date
    current_date = datetime.now(timezone('Asia/Karachi')).date()
    
    # Calculate the corresponding date last year
    last_year_date = current_date.replace(year=current_date.year - 1)
    
    # Calculate date range
    two_months_ago = last_year_date - timedelta(days=60)
    two_months_ahead = last_year_date + timedelta(days=60)
    
    # Ensure the 'Date' column in last_year_data is in datetime format
    last_year_data['Date'] = pd.to_datetime(last_year_data['Date'])
    
    # Filter last year's data
    filtered_df = last_year_data[
        (last_year_data['Districts'] == district) &
        (last_year_data['Date'].dt.date >= two_months_ago) &
        (last_year_data['Date'].dt.date <= two_months_ahead)
    ]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
    
    # Prepare response data
    past_two_months = filtered_df[filtered_df['Date'].dt.date < last_year_date].sort_values('Date')
    next_two_months = filtered_df[filtered_df['Date'].dt.date >= last_year_date].sort_values('Date')

    past_dates = past_two_months['Date'].dt.strftime('%Y-%m-%d').tolist()
    past_aqi_values = past_two_months['Final_aqi'].tolist()
    
    next_dates = next_two_months['Date'].dt.strftime('%Y-%m-%d').tolist()
    next_aqi_values = next_two_months['Final_aqi'].tolist()

    # Return the data as a JSON response
    return {
        "last_year_data": {
            "past_two_months": {
                "date": past_dates,
                "aqi": past_aqi_values
            },
            "next_two_months": {
                "date": next_dates,
                "aqi": next_aqi_values
            }
        }
    }

@app.get("/api/forecast_data")
def get_forecast_data(
    district: str = Query(..., description="District name"),
    duration: str = "2 months"
):
    """
    Endpoint to get AQI forecast data for a given district and time period.
    """
    time = get_pakistan_time()
    # Convert time to datetime
    time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    # Calculate end date based on duration
    end_date = time_dt + timedelta(days=60)
    
    # Convert the Date column in daily_forecast to datetime format
    latest_daily_forecast_df['Date'] = pd.to_datetime(latest_daily_forecast_df['Date'], format='mixed')
    
    # Filter the DataFrame by district and date range
    filtered_df = latest_daily_forecast_df[
        (latest_daily_forecast_df['Districts'] == district) &
        (latest_daily_forecast_df['Date'] >= time_dt) &
        (latest_daily_forecast_df['Date'] <= end_date)
    ]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No forecast data found for the specified parameters.")

    # Prepare response data
    date_array = filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    aqi_array = filtered_df['Final_aqi'].tolist()
    
    # Get 7 days forecast lag
    seven_days_lag = filtered_df[filtered_df['Date'] <= (time_dt + timedelta(days=7))]
    aqi_array_7_days_lag = seven_days_lag['Final_aqi'].tolist()
    
    # Get 14 days forecast lag
    fourteen_days_lag = filtered_df[filtered_df['Date'] <= (time_dt + timedelta(days=14))]
    aqi_array_14_days_lag = fourteen_days_lag['Final_aqi'].tolist()

    # Return the filtered data as a JSON response
    return {
        "date": date_array, 
        "aqi": aqi_array, 
        "aqi_7_days_lag": aqi_array_7_days_lag, 
        "aqi_14_days_lag": aqi_array_14_days_lag
    }

@app.get("/api/pollutant_districts")
def get_districts_by_pollutant(pollutant_name: str):
    """
    Endpoint to get the districts for a given pollutant or all districts if 'All' is requested.
    """
    if pollutant_name == "All":
        # Return all unique districts from the pollutant_districts dictionary
        all_districts = set()
        for districts in pollutant_districts.values():
            all_districts.update(districts)
        return {"districts": list(all_districts)}
    
    if pollutant_name not in pollutant_districts:
        raise HTTPException(status_code=404, detail="Pollutant not found.")
    
    districts = pollutant_districts[pollutant_name]
    # removing the duplicate districts
    districts = list(set(districts))
    return {"districts": districts}

@app.get("/api/current_pollutants")
def get_current_pollutants(
    district: str = Query(..., description="District name")
):
    """
    Endpoint to get current pollutant values for a given district.
    """
    # Get current time
    current_time = get_pakistan_time()
    
    # Filter the DataFrame by district and current time
    filtered_df = forecasted_pollutants[
        (forecasted_pollutants['District'] == district) &
        (forecasted_pollutants['Date'] == current_time)
    ]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified district and current time.")

    # List of pollutants to return
    pollutants = [
        'Carbon_monoxide', 'Dust', 'Nitrogen_dioxide', 
        'Ozone', 'Pm_10', 'Pm_25', 'Sulphur_dioxide'
    ]

    # Prepare response data
    pollutant_values = {}
    for pollutant in pollutants:
        if pollutant in filtered_df.columns:
            pollutant_values[pollutant] = filtered_df[pollutant].iloc[0]
        else:
            pollutant_values[pollutant] = None  # or some default value

    # Return the pollutant values as a JSON response
    return {
        "district": district,
        "time": current_time,
        "pollutants": pollutant_values
    }

@app.get("/api/this_year")
def get_this_year_data(
    district: str = Query(..., description="District name")
):
    """
    Endpoint to get this year's AQI data for a given district for the last 2 months
    and the next 2 months from the current date.
    """
    # Get current date
    current_date = datetime.now(timezone('Asia/Karachi')).date()
    
    # Calculate date range
    two_months_ago = current_date - timedelta(days=60)
    two_months_ahead = current_date + timedelta(days=60)
    
    # Prepare historical data (last 2 months)
    historical_df = last_year_data[
        (last_year_data['Districts'] == district) &
        (pd.to_datetime(last_year_data['Date']).dt.date >= two_months_ago) &
        (pd.to_datetime(last_year_data['Date']).dt.date < current_date)
    ].copy()
    
    # Rename 'Final_AQI' to 'Final_aqi' in historical data
    # historical_df = historical_df.rename(columns={'Final_aqi': 'Final_aqi'})
    
    # Prepare forecast data (next 2 months)
    forecast_df = latest_daily_forecast_df[
        (latest_daily_forecast_df['Districts'] == district) &
        (pd.to_datetime(latest_daily_forecast_df['Date']).dt.date >= current_date) &
        (pd.to_datetime(latest_daily_forecast_df['Date']).dt.date <= two_months_ahead)
    ]

    if historical_df.empty and forecast_df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
    
    # Prepare response data
    historical_dates = pd.to_datetime(historical_df['Date']).dt.strftime('%Y-%m-%d').tolist()
    historical_aqi_values = historical_df['Final_aqi'].tolist()
    
    forecast_dates = pd.to_datetime(forecast_df['Date']).dt.strftime('%Y-%m-%d').tolist()
    forecast_aqi_values = forecast_df['Final_aqi'].tolist()

    # Return the data as a JSON response
    # Interpolate NaN and infinity values in historical and forecast AQI values
    historical_aqi_values = pd.Series(historical_aqi_values).replace([np.inf, -np.inf], np.nan).interpolate().fillna(method='bfill').tolist()
    forecast_aqi_values = pd.Series(forecast_aqi_values).replace([np.inf, -np.inf], np.nan).interpolate().fillna(method='bfill').tolist()

    return {
        "this_year_data": {
            "past_two_months": {
                "date": historical_dates,
                "aqi": historical_aqi_values
            },
            "next_two_months": {
                "date": forecast_dates,
                "aqi": forecast_aqi_values
            }
        }
    }
    

@app.get("/api/october_sources")
def load_and_group_by_district(input_date, input_district):
    
    result_dict = load_db_and_group_by_district(input_date, input_district)
    
    return result_dict

@app.get("/api/update_october_sources")
def update_october():
    
    result = process_air_quality_data()
    return result
    
    
@app.get("/api/weather_data/")
def wweather_data():
    data = get_average_weather()
    'District', 'Time', 'Temperature_2m', 'Wind_speed_10m'
    result = {
        'District': data['District'].values.tolist(),
        "Temperature": data['Temperature_2m'].values.tolist(),
        "Wind_speed": data['Wind_speed_10m'].values.tolist()
    }
    return result

@app.get("/api/miscellaneous_pts/")
def miscellaneous_data(Type:str):
    filter_data = miscellaneous[miscellaneous['TYPE'] == str(Type)]
    data_long = filter_data['Longitude'].values.tolist()
    data_lat = filter_data["Latitude"].values.tolist()
    
    result = {
        "Longitude": data_long, 
        "Latitude": data_lat
    }
    return result

@app.get("/api/min_max_last_year/")
def get_last_year_minmax(district: str): 
    """
    Get min and max AQI values for a district from last year, 
    returning arrays of dates, min values, and max values for two 2-month periods.
    """
    try:
        # Getting today's date
        current_date = datetime.strptime(get_pakistan_time(), '%Y-%m-%d %H:%M:%S').date()
        
        # Calculate the corresponding date last year
        last_year_date = current_date.replace(year=current_date.year - 1)
        
        # Calculate date ranges
        two_months_before = last_year_date - timedelta(days=60)
        two_months_after = last_year_date + timedelta(days=60)
        
        # Convert dates in the dataframe to datetime
        daily_aqi_min_max['Date'] = pd.to_datetime(daily_aqi_min_max['Date'])
        
        # Filter data for the specified district
        district_data = daily_aqi_min_max[daily_aqi_min_max['District'] == district]
        
        # Split into before and after periods
        before_period = district_data[
            (district_data['Date'].dt.date >= two_months_before) &
            (district_data['Date'].dt.date < last_year_date)
        ].sort_values('Date')
        
        after_period = district_data[
            (district_data['Date'].dt.date >= last_year_date) &
            (district_data['Date'].dt.date <= two_months_after)
        ].sort_values('Date')
        
        if before_period.empty and after_period.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for district {district} in the specified date range"
            )
            
        # Prepare the response with separate arrays
        response = {
            "district": district,
            "before_period": {
                "date": before_period['Date'].dt.strftime('%Y-%m-%d').tolist(),
                "min": before_period['Min'].astype(float).tolist(),
                "max": before_period['Max'].astype(float).tolist()
            },
            "after_period": {
                "date": after_period['Date'].dt.strftime('%Y-%m-%d').tolist(),
                "min": after_period['Min'].astype(float).tolist(),
                "max": after_period['Max'].astype(float).tolist()
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/min_max_this_year/")
def get_this_year_minmax(district: str): 
    """
    Get min and max AQI values for a district from current year, 
    returning arrays of dates, min values, and max values for two 2-month periods.
    """
    try:
        # Getting today's date
        current_date = datetime.strptime(get_pakistan_time(), '%Y-%m-%d %H:%M:%S').date()
        
        # Calculate date ranges
        two_months_before = current_date - timedelta(days=60)
        two_months_after = current_date + timedelta(days=60)
        
        # Convert dates in the dataframe to datetime
        daily_aqi_min_max['Date'] = pd.to_datetime(daily_aqi_min_max['Date'])
        
        # Filter data for the specified district
        district_data = daily_aqi_min_max[daily_aqi_min_max['District'] == district]
        
        # Split into before and after periods
        before_period = district_data[
            (district_data['Date'].dt.date >= two_months_before) &
            (district_data['Date'].dt.date < current_date)
        ].sort_values('Date')
        
        after_period = district_data[
            (district_data['Date'].dt.date >= current_date) &
            (district_data['Date'].dt.date <= two_months_after)
        ].sort_values('Date')
        
        if before_period.empty and after_period.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for district {district} in the specified date range"
            )
            
        # Prepare the response with separate arrays
        response = {
            "district": district,
            "before_period": {
                "date": before_period['Date'].dt.strftime('%Y-%m-%d').tolist(),
                "min": before_period['Min'].astype(float).tolist(),
                "max": before_period['Max'].astype(float).tolist()
            },
            "after_period": {
                "date": after_period['Date'].dt.strftime('%Y-%m-%d').tolist(),
                "min": after_period['Min'].astype(float).tolist(),
                "max": after_period['Max'].astype(float).tolist()
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collect_district_data")
async def collect_district_data(
    background_tasks: BackgroundTasks,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    import datetime
    
    """
    Endpoint to collect air quality data for all districts.
    Uses concurrent processing for faster data collection.
    """
    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.max_cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Load location data
        try:
            location_data = pd.read_csv("location_smog1.csv")
        except FileNotFoundError:
            location_data = pd.read_csv("fastapi-server/location_smog1.csv")

        # Set default dates if not provided
        if not start_date or not end_date:
            current_date = datetime.date.today()
            start_date = current_date.strftime("%Y-%m-%d")
            end_date = (current_date + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

        # Create output directory
        output_dir = "Pollutant"
        os.makedirs(output_dir, exist_ok=True)

        async def process_district(row):
            latitude = row['Latitude']
            longitude = row['Longitude']
            district = row['District']

            # Make API requests for air quality
            air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
            air_quality_params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
                "start_date": start_date,
                "end_date": end_date
            }

            try:
                # Fetch air quality data
                air_quality_response = openmeteo.weather_api(air_quality_url, params=air_quality_params)[0]
                
                # Process air quality data
                air_quality_hourly = air_quality_response.Hourly()
                hourly_data = {
                    "PM10": air_quality_hourly.Variables(0).ValuesAsNumpy(),
                    "PM2.5": air_quality_hourly.Variables(1).ValuesAsNumpy(),
                    "Carbon Monoxide": air_quality_hourly.Variables(2).ValuesAsNumpy(),
                    "Nitrogen Dioxide": air_quality_hourly.Variables(3).ValuesAsNumpy(),
                    "Sulphur Dioxide": air_quality_hourly.Variables(4).ValuesAsNumpy(),
                    "Ozone": air_quality_hourly.Variables(5).ValuesAsNumpy(),
                    "Dust": air_quality_hourly.Variables(6).ValuesAsNumpy(),
                }

                # Create time index
                time_index = pd.date_range(
                    start=pd.to_datetime(air_quality_hourly.Time(), unit="s"),
                    end=pd.to_datetime(air_quality_hourly.TimeEnd(), unit="s"),
                    freq=pd.Timedelta(seconds=air_quality_hourly.Interval()),
                    inclusive="left"
                )

                # Format date and hour
                hourly_data.update({
                    "date": time_index.strftime('%m/%d/%Y'),
                    "hour": time_index.strftime('%H:%M'),
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "District": district
                })

                # Create DataFrame
                hourly_dataframe = pd.DataFrame(data=hourly_data)

                # Calculate AQI
                hourly_dataframe["AQI"] = (
                    (hourly_dataframe["PM10"] * 0.25) +
                    (hourly_dataframe["PM2.5"] * 0.25) +
                    (hourly_dataframe["Carbon Monoxide"] * 0.1) +
                    (hourly_dataframe["Nitrogen Dioxide"] * 0.15) +
                    (hourly_dataframe["Sulphur Dioxide"] * 0.1) +
                    (hourly_dataframe["Ozone"] * 0.1) +
                    (hourly_dataframe["Dust"] * 0.05)
                )

                # Save individual district data
                csv_filename = f"{output_dir}/hourly_data_{latitude}_{longitude}.csv"
                hourly_dataframe.to_csv(csv_filename, index=False)
                
                return hourly_dataframe

            except Exception as e:
                print(f"Error processing district {district}: {str(e)}")
                return None

        # Process districts concurrently
        async def process_all_districts():
            tasks = []
            for _, row in location_data.iterrows():
                tasks.append(asyncio.create_task(process_district(row)))
            
            results = await asyncio.gather(*tasks)
            return [df for df in results if df is not None]

        # Run the processing
        dataframes = await process_all_districts()

        # Combine all DataFrames
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            combined_csv_path = "combined_hourly_data.csv"
            combined_df.to_csv(combined_csv_path, index=False)
            
            return {
                "status": "success",
                "message": "Data collection completed",
                "districts_processed": len(dataframes),
                "combined_file": combined_csv_path
            }
        else:
            raise HTTPException(status_code=500, detail="No data was collected")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hourly_aqi/{district}")
async def get_hourly_aqi(
    district: str,
    date: str = Query(..., description="Date in MM/DD/YYYY format")
):
    """
    API endpoint to get hourly AQI data for a specific district and date.
    
    Args:
        district: Name of the district
        date: Date in MM/DD/YYYY format
    
    Returns:
        JSON response containing formatted hours and AQI values.
    """
    try:
        # Fetch data from the database
        hours, aqi_values = fetch_hourly_aqi_from_db(district, date)

        # If no data is found, raise a 404 error
        if hours is None or aqi_values is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for district {district} on date {date}"
            )

        # Prepare the response
        response = {
            "district": district,
            "date": date,
            "data": {
                "hours": hours,
                "aqi": aqi_values
            }
        }
        
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/last_24hrs")
async def get_last_24hrs_data():
    """
    Get AQI and pollutant data for all districts over the last 24 hours
    """
    try:
        from last_24_hrs_data import get_24hr_data
        
        data = get_24hr_data()
        return {
            "status": "success",
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/district_24hrs/{district}")
async def get_district_24hrs(district: str, use_api: bool = True):
    """
    Get the last 24 hours of AQI data for a specific district.
    Uses live API data if use_api=True, falls back to cached CSV data if False or if API fails.
    
    Args:
        district: Name of the district
        use_api: Whether to fetch fresh data from API (default: True)
    
    Returns:
        Dictionary containing time series and AQI values for the last 24 hours
    """
    try:
        if use_api:
            try:
                # Import and use the get_24hr_data function
                from last_24_hrs_data import get_24hr_data
                
                # Get fresh data
                df = get_24hr_data()
                
                # Filter for the specified district
                district_data = df[df['District'] == district]
                
                if not district_data.empty:
                    # Sort by time
                    district_data = district_data.sort_values('Time')
                    
                    # Prepare response with fresh data
                    response = {
                        "district": district,
                        "data": {
                            "time": district_data['Time'].tolist(),
                            "aqi": district_data['AQI'].tolist(),
                        },
                        "source": "live_api"
                    }
                    
                    return response
                
            except Exception as e:
                print(f"API fetch failed, falling back to cached data: {str(e)}")
                # If API fails, fall back to cached data
                use_api = False
        
        # Use cached CSV data if use_api is False or if API fetch failed
        try:
            df = pd.read_csv("last_24hrs_results.csv")
        except FileNotFoundError:
            df = pd.read_csv("fastapi-server/last_24hrs_results.csv")
        
        # Filter for the specified district
        district_data = df[df['District'] == district]
        
        if district_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for district {district}"
            )
        
        # Sort by time
        district_data = district_data.sort_values('Time')
        
        # Prepare response with cached data
        response = {
            "district": district,
            "data": {
                "time": district_data['Time'].tolist(),
                "aqi": district_data['AQI'].tolist(),
            },
            "source": "cached_csv"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a background task endpoint to update the CSV periodically
@app.get("/api/update_24hrs_data")
async def update_24hrs_data(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger an update of the 24-hour data CSV file.
    """
    try:
        from last_24_hrs_data import get_24hr_data
        
        # Add the update task to background tasks
        background_tasks.add_task(get_24hr_data)
        
        return {
            "status": "success",
            "message": "Update of 24-hour data initiated in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/last_month")
async def get_last_two_months_aqi(district_name):
    dataframe=LastMonth
    # Get current time in Pakistan
    current_time = get_pakistan_time()
    # Format the current time to match the CSV date format ('m/d/yyyy')
    current_date = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    two_months_ago = current_date - timedelta(days=60)
    
    # Convert the formatted dates to match the CSV format
    formatted_current_date = current_date.strftime('%m/%d/%Y')
    formatted_two_months_ago = two_months_ago.strftime('%m/%d/%Y')

    # Filter the DataFrame for the specified district and the last 2 months
    filtered_df = dataframe[
        (dataframe['Districts'] == district_name) &
        (pd.to_datetime(dataframe['Date'], format='%m/%d/%Y') >= two_months_ago) &
        (pd.to_datetime(dataframe['Date'], format='%m/%d/%Y') <= current_date)
    ]
    
    # Convert the filtered DataFrame to a dictionary with lists for Date and AQI
    result_dict = {
        "Date": filtered_df['Date'].tolist(),
        "AQI": filtered_df['AQI'].tolist()
    }
    
    return result_dict

# Example of how to run the FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
