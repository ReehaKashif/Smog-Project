from fastapi import FastAPI, Query ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta

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
color_palette = [
    "#00FF00", "#19F719", "#32EF32", "#4BE74B", "#64DF64", "#7DD77D",
    "#96CF96", "#AFC7AF", "#C8BFC8", "#E1B7E1", "#FF9FFF", "#FF99E5",
    "#FF92CC", "#FF8CB2", "#FF8699", "#FF7F80", "#FF7966", "#FF734D",
    "#FF6C33", "#FF662A", "#FF6020", "#FF5917", "#FF5313", "#FF4C0F",
    "#FF460B", "#FF4007", "#FF3A03", "#FF3300", "#FF2D00", "#FF2600",
    "#FF2000", "#FF1A00", "#FF1400", "#FF0D00", "#FF0700", "#FF0000"
]

# Define the pollutant to districts mapping
pollutant_districts = {
    "Vehicle": [
        "Bahawalpur", "Rahim Yar Khan", "Gujranwala", "Gujrat", "Hafizabad", "Mandi Bahuddin",
        "Narowal", "Sialkot", "Dera Ghazi Khan", "Layyah", "Muzaffargarh", "Rajanpur", "Lahore",
        "Kasur", "Nankana Sahib", "Sheikhupura", "Faisalabad", "Chiniot", "Toba Tek Singh", "Jhang",
        "Multan", "Lodhran", "Khanewal", "Vehari"
    ],
    "Industry": [
        "Bahawalpur", "Bahawalnagar", "Rahim Yar Khan", "Gujranwala", "Gujrat", "Hafizabad",
        "Mandi Bahuddin", "Narowal", "Sialkot", "Dera Ghazi Khan", "Layyah", "Muzaffargarh",
        "Rajanpur", "Lahore", "Kasur", "Nankana Sahib", "Sheikhupura", "Faisalabad", "Chiniot",
        "Toba Tek Singh", "Jhang", "Multan", "Lodhran", "Khanewal", "Vehari"
    ],
    "Agriculture": [
        "Bahawalpur", "Bahawalnagar", "Rahim Yar Khan", "Dera Ghazi Khan", "Layyah", "Muzaffargarh",
        "Rajanpur", "Kasur", "Nankana Sahib", "Sheikhupura", "Faisalabad", "Chiniot", "Toba Tek Singh",
        "Jhang", "Multan", "Lodhran", "Khanewal", "Vehari"
    ],
    "Construction": [
        "Bahawalpur", "Bahawalnagar", "Rahim Yar Khan", "Gujranwala", "Gujrat", "Hafizabad",
        "Mandi Bahuddin", "Narowal", "Sialkot", "Dera Ghazi Khan", "Layyah", "Muzaffargarh",
        "Rajanpur", "Lahore", "Kasur", "Nankana Sahib", "Sheikhupura", "Faisalabad", "Chiniot",
        "Toba Tek Singh", "Jhang", "Multan", "Lodhran", "Khanewal", "Vehari"
    ],
    "General Wasting": [
        "Bahawalpur", "Bahawalnagar", "Rahim Yar Khan", "Gujranwala", "Gujrat", "Hafizabad",
        "Mandi Bahuddin", "Narowal", "Sialkot", "Dera Ghazi Khan", "Layyah", "Muzaffargarh",
        "Rajanpur", "Lahore", "Kasur", "Nankana Sahib", "Sheikhupura", "Faisalabad", "Chiniot",
        "Toba Tek Singh", "Jhang", "Multan", "Lodhran", "Khanewal", "Vehari"
    ]
}

@app.get("/api/pakistan_time")
def get_pakistan_time_endpoint():
    """
    Endpoint to get the current time in Pakistan.
    """
    return {"pakistan_time": get_pakistan_time()}

# @app.get("/api/aggregate_pollutants/last_year")
# def last_year_aggregate_pollutants(initial_time: str, district: str):
#     forecasted_df = last_year_pollutant_df.copy()
    
#     # Rename and process columns
#     # remove the unnamed column
#     forecasted_df = forecasted_df.drop(columns=['Unnamed: 0'])
#     forecasted_df = forecasted_df.set_index('Date')
#     forecasted_df.index = pd.to_datetime(forecasted_df.index)
#     # print(forecasted_df)
    
#     # Convert initial time to last year
#     initial_time = pd.to_datetime(initial_time)
#     initial_time = initial_time - pd.Timedelta(days=366)
#     final_time = initial_time + pd.Timedelta(days=60)

#     # Filter DataFrame
#     filtered_df = forecasted_df[(forecasted_df.index >= initial_time) & 
#                                 (forecasted_df.index <= final_time) & 
#                                 (forecasted_df['District'] == district)]
#     # print(filtered_df)
#     # Aggregate pollutants
#     numeric_columns = filtered_df.select_dtypes(include=['float64', 'int64']).columns
#     aggregated_df = filtered_df[numeric_columns].resample('h').mean()
    
#     return aggregated_df.to_dict(orient="index")


# @app.get("/api/aggregate_pollutants/daily")
# def daily_aggregate_pollutants(initial_time: str, district: str):
#     forecasted_df = forecasted_pollutant_df.copy()
#     # counting the unique districts
#     print(forecasted_df['District'].nunique())
    
#     # Rename and process columns
#     # forecasted_df = forecasted_df.drop(columns=['Unnamed: 0'])
#     forecasted_df = forecasted_df.set_index('date')
#     forecasted_df.index = pd.to_datetime(forecasted_df.index)
    
#     # Process initial time
#     initial_time = pd.to_datetime(initial_time)
#     final_time = initial_time + pd.Timedelta(days=14)

#     # Filter DataFrame
#     filtered_df = forecasted_df[(forecasted_df.index >= initial_time) & 
#                                 (forecasted_df.index <= final_time) & 
#                                 (forecasted_df['District'] == district)]
    
#     # Aggregate pollutants
#     numeric_columns = filtered_df.select_dtypes(include=['float64', 'int64']).columns
#     aggregated_df = filtered_df[numeric_columns].resample('D').mean()
    
#     return aggregated_df.to_dict(orient="index")


# @app.get("/api/forecast_aqi")
# def forecast_aqi(district_name: str, date: str, forecast_period: Optional[str] = "60 days"):
#     district_data = aqi_forecast_df[aqi_forecast_df['district'] == district_name].copy()
#     # removing the unnamed column
#     district_data = district_data.drop(columns=['Unnamed: 0'])
#     district_data['date'] = pd.to_datetime(district_data['date'])
    
#     if forecast_period == "7 days":
#         start_date = pd.to_datetime(date).normalize()
#         end_date = start_date + pd.Timedelta(days=7)
#     elif forecast_period == "14 days":
#         start_date = pd.to_datetime(date).normalize()
#         end_date = start_date + pd.Timedelta(days=14)
#     else:
#         start_date = pd.to_datetime(date).normalize()
#         end_date = start_date + pd.Timedelta(days=60)
    
#     # Filter the data
#     forecast_data = district_data[(district_data['date'] >= start_date) & 
#                                   (district_data['date'] <= end_date)]
    
#     return forecast_data.to_dict(orient="index")


# @app.get("/api/best_districts_aqi")
# def get_best_districts_aqi():
#     """
#     Endpoint to get the four districts with the best (lowest) AQI at a specific time.
#     """
#     try:
#         time = get_pakistan_time()
#         # Filter the DataFrame by the given time
#         filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
#         if filtered_df.empty:
#             raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
#         # Sort by AQI in ascending order and get the top 4
#         sorted_df = filtered_df.sort_values(by='Aqi')
#         # getting the unique top 4 districts
#         sorted_df = sorted_df.drop_duplicates(subset=['District']).head(4)
        
#         # Prepare the response
#         response = [{"district": row["District"], "aqi": row["Aqi"]} for index, row in sorted_df.iterrows()]
        
#         return {"best_districts": response}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
    


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
        aqi_array_7_days_lag = filtered_df_7_days_lag['Aqi'].tolist()
        aqi_array_14_days_lag = filtered_df_14_days_lag['Aqi'].tolist()

        # Return the filtered data as a JSON response
        return {"date": date_array, "aqi": aqi_array, "aqi_7_days_lag": aqi_array_7_days_lag, "aqi_14_days_lag": aqi_array_14_days_lag}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pollutant_districts")
def get_districts_by_pollutant(pollutant_name: str):
    """
    Endpoint to get the districts for a given pollutant.
    """
    try:
        if pollutant_name not in pollutant_districts:
            raise HTTPException(status_code=404, detail="Pollutant not found.")
        districts = pollutant_districts[pollutant_name]
        # removing the duplicate districts
        districts = list(set(districts))
        # print(districts)
        return {"districts": districts}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Example of how to run the FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


