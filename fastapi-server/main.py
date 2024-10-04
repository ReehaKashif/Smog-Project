from fastapi import FastAPI, Query ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta
import random  # Add this import at the top of your file

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
    forecasted_pollutant_df = pd.read_csv('forecasted_pollutant.csv')
    # renaming unnamed 0 as date
    forecasted_pollutant_df.rename(columns = {'Unnamed: 0':'date'}, inplace = True)
    # print(forecasted_pollutant_df.head())
    aqi_forecast_df = pd.read_csv('aqi_forecast.csv')
    aqi_7_days_forecast_df = pd.read_csv('daily_7_days_lag_data.csv')
    aqi_14_days_forecast_df = pd.read_csv('daily_14_days_lag_data.csv')
    daily_max_forecasted = pd.read_csv('daily_forecasted_data.csv')
    daily_max_historical = pd.read_csv('daily_historical_data.csv')
except FileNotFoundError as e:
    forecasted_pollutant_df = pd.read_csv('fastapi-server/forecasted_pollutant.csv')
    # renaming unnamed 0 as date
    forecasted_pollutant_df.rename(columns = {'Unnamed: 0':'date'}, inplace = True)
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
    "Deforestation": [
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
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        # reset the index
        filtered_df = filtered_df.reset_index(drop=True)
        # print(filtered_df)
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # sort in ascending order
        filtered_df = filtered_df.sort_values(by='Aqi')
        
        # Ensure unique districts
        unique_districts_df = filtered_df.drop_duplicates(subset=['District'])
        
        # Assign colors based on AQI and prepare the response
        response = []
        for index, row in unique_districts_df.iterrows():
            color_name, color_code = get_AQI_color(row["Aqi"])
            response.append({
                "district": row["District"],
                "aqi": row["Aqi"],
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
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # sort in ascending order
        filtered_df = filtered_df.sort_values(by='Aqi')
        
        # ensure unique districts
        filtered_df = filtered_df.drop_duplicates(subset=['District'])
        
        # Find the district with the lowest (best) AQI
        best_district_row = filtered_df.loc[filtered_df['Aqi'].idxmin()]
        best_district = {"district": best_district_row["District"], "aqi": best_district_row["Aqi"]}
        
        # Find the district with the highest (worst) AQI
        worst_district_row = filtered_df.loc[filtered_df['Aqi'].idxmax()]
        worst_district = {"district": worst_district_row["District"], "aqi": worst_district_row["Aqi"]}
        
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
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # sort in ascending order
        filtered_df = filtered_df.sort_values(by='Aqi')
        
        # Ensure unique districts and sort by AQI in ascending order
        sorted_df = filtered_df.drop_duplicates(subset=['District']).sort_values(by='Aqi')
 
        
        # selecting the needed columns
        sorted_df = sorted_df[['District', 'Aqi']].reset_index(drop=True)
        # print(sorted_df)
        # print(len(color_palette))
        # Assign colors based on the sorted order
        response = []
        for index, row in sorted_df.iterrows():
            # preparing the response
            response.append({
                "district": row["District"],
                "aqi": row["Aqi"],
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
    including recent historical forecasts from 7-day and 14-day lag data.
    """
    try:
        time = get_pakistan_time()
        time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').date()

        # Set duration to 2 months
        start_date = time_dt - timedelta(days=60)
        
        # Filter historical data
        filtered_df = daily_max_historical[
            (daily_max_historical['District'] == district) &
            (daily_max_historical['date'] >= start_date.strftime('%Y-%m-%d')) &
            (daily_max_historical['date'] <= time_dt.strftime('%Y-%m-%d'))
        ]
        
        # Get last 7 days of forecast data
        forecast_7d = aqi_7_days_forecast_df[
            (aqi_7_days_forecast_df['district'] == district) &
            (aqi_7_days_forecast_df['date'] > (time_dt - timedelta(days=7)).strftime('%Y-%m-%d')) &
            (aqi_7_days_forecast_df['date'] <= time_dt.strftime('%Y-%m-%d'))
        ]

        # Get last 14 days of forecast data
        forecast_14d = aqi_14_days_forecast_df[
            (aqi_14_days_forecast_df['district'] == district) &
            (aqi_14_days_forecast_df['date'] > (time_dt - timedelta(days=14)).strftime('%Y-%m-%d')) &
            (aqi_14_days_forecast_df['date'] <= time_dt.strftime('%Y-%m-%d'))
        ]

        if filtered_df.empty and forecast_7d.empty and forecast_14d.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
        
        # Prepare response data
        historical_dates = filtered_df['date'].tolist()
        historical_aqi = filtered_df['Aqi'].tolist()
        
        forecast_7d_dates = forecast_7d['date'].tolist()
        forecast_7d_aqi = forecast_7d['Aqi'].tolist()
        
        forecast_14d_dates = forecast_14d['date'].tolist()
        forecast_14d_aqi = forecast_14d['Aqi'].tolist()

        # Return the data as a JSON response
        return {
            "historical": {"date": historical_dates, "aqi": historical_aqi},
            "forecast_7d": {"date": forecast_7d_dates, "aqi": forecast_7d_aqi},
            "forecast_14d": {"date": forecast_14d_dates, "aqi": forecast_14d_aqi}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/forecast_data")
def get_forecast_data(
    district: str = Query(..., description="District name"),
    duration: str = "2 months"
):
    """
    Endpoint to get AQI forecast data for a given district and time period.
    """
    try:
        time = get_pakistan_time()
        # Convert time to datetime
        time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        # converting time to date alone
        time_dt = time_dt.date()

        # Calculate end date based on duration
        # if duration == 'weekly':
        #     end_date = time_dt + timedelta(days=7)
        # elif duration == 'biweekly':
        #     end_date = time_dt + timedelta(days=14)
        # elif duration == 'monthly':
        #     end_date = time_dt + timedelta(days=30)
        end_date = time_dt + timedelta(days=60)
        # else:
        #     raise HTTPException(status_code=400, detail="Invalid duration. Choose from 'weekly', 'biweekly', 'monthly', or '2 months'.")
        
        # Filter the DataFrame by district and date range
        filtered_df = daily_max_forecasted[
            (daily_max_forecasted['District'] == district) &
            (daily_max_forecasted['date'] >= time_dt.strftime('%Y-%m-%d')) &
            (daily_max_forecasted['date'] <= end_date.strftime('%Y-%m-%d'))
        ]
        # showing forecast data for 7 days lag
        filtered_df_7_days_lag = aqi_7_days_forecast_df[
            (aqi_7_days_forecast_df['district'] == district) &
            (aqi_7_days_forecast_df['date'] >= time_dt.strftime('%Y-%m-%d')) &
            (aqi_7_days_forecast_df['date'] <= end_date.strftime('%Y-%m-%d'))
        ]
        # showing forecast data for 14 days lag
        filtered_df_14_days_lag = aqi_14_days_forecast_df[
            (aqi_14_days_forecast_df['district'] == district) & 
            (aqi_14_days_forecast_df['date'] >= time_dt.strftime('%Y-%m-%d')) &
            (aqi_14_days_forecast_df['date'] <= end_date.strftime('%Y-%m-%d'))
        ]
        # removing the unnamed column
        # filtered_df = filtered_df.drop(columns=['Unnamed: 0'])
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No forecast data found for the specified parameters.")

        # selecting the date and aqi columns
        filtered_df = filtered_df[['date', 'Aqi']]
        filtered_df_7_days_lag = filtered_df_7_days_lag[['date', 'Aqi']]
        filtered_df_14_days_lag = filtered_df_14_days_lag[['date', 'Aqi']]
        # return two array, one for date and one for aqi
        date_array = filtered_df['date'].tolist()
        aqi_array = filtered_df['Aqi'].tolist()
        
        # Randomly multiply the AQI values (except the first one)
        # aqi_array = [aqi_array[0]] + [aqi * random.randint(2, 4) for aqi in aqi_array[1:]]
        
        aqi_array_7_days_lag = filtered_df_7_days_lag['Aqi'].tolist()
        # aqi_array_7_days_lag = [aqi_array_7_days_lag[0]] + [aqi * random.randint(2, 4) for aqi in aqi_array_7_days_lag[1:]]
        
        aqi_array_14_days_lag = filtered_df_14_days_lag['Aqi'].tolist()
        # aqi_array_14_days_lag = [aqi_array_14_days_lag[0]] + [aqi * random.randint(2, 4) for aqi in aqi_array_14_days_lag[1:]]

        # Return the filtered data as a JSON response
        return {"date": date_array, "aqi": aqi_array, "aqi_7_days_lag": aqi_array_7_days_lag, "aqi_14_days_lag": aqi_array_14_days_lag}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pollutant_districts")
def get_districts_by_pollutant(pollutant_name: str):
    """
    Endpoint to get the districts for a given pollutant or all districts if 'All' is requested.
    """
    try:
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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Example of how to run the FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


