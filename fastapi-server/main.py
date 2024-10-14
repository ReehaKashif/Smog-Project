from fastapi import FastAPI, Query ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta
import random  # Add this import at the top of your file
from collect_weather_data import get_average_weather

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
    forecasted_pollutant_df = pd.read_csv('combined_forecast.csv')
    latest_forecast_df = pd.read_csv("latest_forecasts.csv")
    latest_daily_forecast_df = pd.read_csv("latest_daily_forecasts.csv")
    daily_forecast =  pd.read_csv('daily_forecast.csv')
    last_year_data = pd.read_csv('last_year_daily_data.csv')
    # renaming unnamed 0 as date
    # print(forecasted_pollutant_df.head())
    aqi_forecast_df = pd.read_csv('aqi_forecast.csv')
    aqi_7_days_forecast_df = pd.read_csv('daily_7_days_lag_data.csv')
    aqi_14_days_forecast_df = pd.read_csv('daily_14_days_lag_data.csv')
    daily_max_forecasted = pd.read_csv('daily_forecasted_data.csv')
    daily_max_historical = pd.read_csv('daily_historical_data.csv')
except FileNotFoundError as e:
    forecasted_pollutant_df = pd.read_csv('fastapi-server/combined_forecast.csv')
    latest_forecast_df = pd.read_csv("fastapi-server/latest_forecasts.csv")
    latest_daily_forecast_df = pd.read_csv("fastapi-server/latest_daily_forecasts.csv")
    daily_forecast =  pd.read_csv('fastapi-server/daily_forecast.csv')
    last_year_data = pd.read_csv('fastapi-server/last_year_daily_data.csv')
    # renaming unnamed 0 as date
    aqi_forecast_df = pd.read_csv('fastapi-server/aqi_forecast.csv')
    aqi_7_days_forecast_df = pd.read_csv('fastapi-server/daily_7_days_lag_data.csv')
    aqi_14_days_forecast_df = pd.read_csv('fastapi-server/daily_14_days_lag_data.csv')
    daily_max_forecasted = pd.read_csv('fastapi-server/daily_forecasted_data.csv')
    daily_max_historical = pd.read_csv('fastapi-server/daily_historical_data.csv')
    # raise HTTPException(status_code=404, detail=str(e))

def get_pakistan_time():
    # Example of getting the current date and time in Pakistan
    now = datetime.now(timezone('Asia/Karachi'))
    # now = "2024-07-01 23:00:00"
    # converting to time format
    # now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
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


# Assuming the color palette provided corresponds to these hex codes
# color_palette =[
#   ["#00FF00", "#24FF00", "#48FF00", "#6CFF00", "#90FF00", "#B4FF00"],
#   ["#D8FF00", "#FCFF00", "#FFF500", "#FFEB00", "#FFE100", "#FFD700"],
#   ["#FFCC00", "#FFC200", "#FFB800", "#FFAD00", "#FFA300", "#FF9900"],
#   ["#FF8E00", "#FF8400", "#FF7A00", "#FF6F00", "#FF6500", "#FF5B00"],
#   ["#FF5100", "#FF4600", "#FF3C00", "#FF3200", "#FF2800", "#FF1D00"],
#   ["#FF1300", "#FF0900", "#FF0000", "#F50000", "#EB0000", "#E10000"],
# ]

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
def get_districts_aqi_color():
    """
    Endpoint to get the AQI and color for each district at a specific time.
    """
    try:
        # Filter the DataFrame by the given time
        # convert the time to date time format
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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aqi_status")
def get_aqi_status():
    """
    Endpoint to get the AQI status including best and worst district, highest pollutant, and cause of pollutant.
    """
    try:
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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/map_ranking")
def get_map_ranking():
    """
    Endpoint to get the AQI ranking of districts and assign colors based on the provided color palette.
    """
    try:
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
        # print(sorted_df)
        # print(len(color_palette))
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
        (historical_data['District'] == district) &
        (historical_data['Date'].dt.date >= start_date) &
        (historical_data['Date'].dt.date <= time_dt)
    ]
    
    # Calculate the corresponding dates for last year
    last_year_date = time_dt.replace(year=time_dt.year - 1)
    last_year_7d_start = last_year_date - timedelta(days=7)
    last_year_14d_start = last_year_date - timedelta(days=14)

    # Get last 7 days of last year's data
    forecast_7d = last_year_data_renamed[
        (last_year_data_renamed['District'] == district) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date > last_year_7d_start) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date <= last_year_date)
    ]

    # Get last 14 days of last year's data
    forecast_14d = last_year_data_renamed[
        (last_year_data_renamed['District'] == district) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date > last_year_14d_start) &
        (pd.to_datetime(last_year_data_renamed['Date']).dt.date <= last_year_date)
    ]

    if filtered_df.empty and forecast_7d.empty and forecast_14d.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
    
    # Prepare response data
    historical_dates = filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    historical_aqi = filtered_df['Final_aqi'].tolist()
    
    forecast_7d_dates = pd.to_datetime(forecast_7d['Date']).dt.strftime('%Y-%m-%d').tolist()
    forecast_7d_aqi = forecast_7d['Final_aqi'].tolist()
    
    forecast_14d_dates = pd.to_datetime(forecast_14d['Date']).dt.strftime('%Y-%m-%d').tolist()
    forecast_14d_aqi = forecast_14d['Final_aqi'].tolist()

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
        (last_year_data['District'] == district) &
        (last_year_data['Date'].dt.date >= two_months_ago) &
        (last_year_data['Date'].dt.date <= two_months_ahead)
    ]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
    
    # Prepare response data
    past_two_months = filtered_df[filtered_df['Date'].dt.date < last_year_date].sort_values('Date')
    next_two_months = filtered_df[filtered_df['Date'].dt.date >= last_year_date].sort_values('Date')

    past_dates = past_two_months['Date'].dt.strftime('%Y-%m-%d').tolist()
    past_aqi_values = past_two_months['Final_AQI'].tolist()
    
    next_dates = next_two_months['Date'].dt.strftime('%Y-%m-%d').tolist()
    next_aqi_values = next_two_months['Final_AQI'].tolist()

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
        (latest_daily_forecast_df['District'] == district) &
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
    filtered_df = forecasted_pollutant_df[
        (forecasted_pollutant_df['District'] == district) &
        (forecasted_pollutant_df['Date'] == current_time)
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
        (last_year_data['District'] == district) &
        (pd.to_datetime(last_year_data['Date']).dt.date >= two_months_ago) &
        (pd.to_datetime(last_year_data['Date']).dt.date < current_date)
    ].copy()
    
    # Rename 'Final_AQI' to 'Final_aqi' in historical data
    historical_df = historical_df.rename(columns={'Final_AQI': 'Final_aqi'})
    
    # Prepare forecast data (next 2 months)
    forecast_df = latest_daily_forecast_df[
        (latest_daily_forecast_df['District'] == district) &
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

# Example of how to run the FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)