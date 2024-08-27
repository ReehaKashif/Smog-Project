from fastapi import FastAPI, Query ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
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
    last_year_pollutant_df = pd.read_csv('last_year_pollutant.csv')
    aqi_forecast_df = pd.read_csv('aqi_forecast.csv')
    historical_df = pd.read_csv('ready_historical.csv')
except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))



def get_pakistan_time():
    # Example of getting the current date and time in Pakistan
    # now = datetime.now(timezone('Asia/Karachi'))
    now = "2024-07-01 23:00:00"
    # converting to time format
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    # returning it in this format '2024-07-01 00:00:00'
    formatted_time = now.strftime('%Y-%m-%d %H:00:00')
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
    "#6EC3D0", "#61BF97", "#F5B565", "#EAA29C", "#B0A6C9", "#D282A6",  # Row 1
    "#4699CC", "#0FAA62", "#F18B12", "#DC3D3D", "#4839A0", "#B11277",  # Row 2
    "#4A79B6", "#0D8A5E", "#EB9300", "#CF3434", "#403093", "#A4106F",  # Row 3
    "#4077A3", "#077F4F", "#DAA105", "#BC2C2C", "#362C82", "#8C095E",  # Row 4
    "#6E9CC4", "#3B8C86", "#EDB143", "#DD6861", "#8575AD", "#C66F95",  # Row 5
    "#286CA5", "#0E9253", "#E49806", "#D14A4A", "#5245A6", "#A31377"   # Row 6
]

@app.get("/api/pakistan_time")
def get_pakistan_time_endpoint():
    """
    Endpoint to get the current time in Pakistan.
    """
    return {"pakistan_time": get_pakistan_time()}

@app.get("/api/aggregate_pollutants/last_year")
def last_year_aggregate_pollutants(initial_time: str, district: str):
    forecasted_df = last_year_pollutant_df.copy()
    
    # Rename and process columns
    # remove the unnamed column
    forecasted_df = forecasted_df.drop(columns=['Unnamed: 0'])
    forecasted_df = forecasted_df.set_index('Date')
    forecasted_df.index = pd.to_datetime(forecasted_df.index)
    # print(forecasted_df)
    
    # Convert initial time to last year
    initial_time = pd.to_datetime(initial_time)
    initial_time = initial_time - pd.Timedelta(days=366)
    final_time = initial_time + pd.Timedelta(days=60)

    # Filter DataFrame
    filtered_df = forecasted_df[(forecasted_df.index >= initial_time) & 
                                (forecasted_df.index <= final_time) & 
                                (forecasted_df['District'] == district)]
    # print(filtered_df)
    # Aggregate pollutants
    numeric_columns = filtered_df.select_dtypes(include=['float64', 'int64']).columns
    aggregated_df = filtered_df[numeric_columns].resample('h').mean()
    
    return aggregated_df.to_dict(orient="index")


@app.get("/api/aggregate_pollutants/daily")
def daily_aggregate_pollutants(initial_time: str, district: str):
    forecasted_df = forecasted_pollutant_df.copy()
    # counting the unique districts
    print(forecasted_df['District'].nunique())
    
    # Rename and process columns
    # forecasted_df = forecasted_df.drop(columns=['Unnamed: 0'])
    forecasted_df = forecasted_df.set_index('date')
    forecasted_df.index = pd.to_datetime(forecasted_df.index)
    
    # Process initial time
    initial_time = pd.to_datetime(initial_time)
    final_time = initial_time + pd.Timedelta(days=14)

    # Filter DataFrame
    filtered_df = forecasted_df[(forecasted_df.index >= initial_time) & 
                                (forecasted_df.index <= final_time) & 
                                (forecasted_df['District'] == district)]
    
    # Aggregate pollutants
    numeric_columns = filtered_df.select_dtypes(include=['float64', 'int64']).columns
    aggregated_df = filtered_df[numeric_columns].resample('D').mean()
    
    return aggregated_df.to_dict(orient="index")


@app.get("/api/forecast_aqi")
def forecast_aqi(district_name: str, date: str, forecast_period: Optional[str] = "60 days"):
    district_data = aqi_forecast_df[aqi_forecast_df['District'] == district_name].copy()
    # removing the unnamed column
    district_data = district_data.drop(columns=['Unnamed: 0'])
    district_data['date'] = pd.to_datetime(district_data['date'])
    
    if forecast_period == "7 days":
        start_date = pd.to_datetime(date).normalize()
        end_date = start_date + pd.Timedelta(days=7)
    elif forecast_period == "14 days":
        start_date = pd.to_datetime(date).normalize()
        end_date = start_date + pd.Timedelta(days=14)
    else:
        start_date = pd.to_datetime(date).normalize()
        end_date = start_date + pd.Timedelta(days=60)
    
    # Filter the data
    forecast_data = district_data[(district_data['date'] >= start_date) & 
                                  (district_data['date'] <= end_date)]
    
    return forecast_data.to_dict(orient="index")


@app.get("/api/best_districts_aqi")
def get_best_districts_aqi(time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'")):
    """
    Endpoint to get the four districts with the best (lowest) AQI at a specific time.
    """
    try:
        # Filter the DataFrame by the given time
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # Sort by AQI in ascending order and get the top 4
        sorted_df = filtered_df.sort_values(by='Aqi')
        # getting the unique top 4 districts
        sorted_df = sorted_df.drop_duplicates(subset=['District']).head(4)
        
        # Prepare the response
        response = [{"district": row["District"], "aqi": row["Aqi"]} for index, row in sorted_df.iterrows()]
        
        return {"best_districts": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


@app.get("/api/districts_aqi_color")
def get_districts_aqi_color(time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'")):
    """
    Endpoint to get the AQI and color for each district at a specific time.
    """
    try:
        # Filter the DataFrame by the given time
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # Assign colors based on AQI and prepare the response
        response = []
        for index, row in filtered_df.iterrows():
            color_name, color_code = get_AQI_color(row["Aqi"])
            response.append({"district": row["District"], "aqi": row["Aqi"], "color": color_name, "color_code": color_code})
        
        return {"districts_aqi_color": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aqi_status")
def get_aqi_status(time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'")):
    """
    Endpoint to get the AQI status including best and worst district, highest pollutant, and cause of pollutant.
    """
    try:
        # Filter the DataFrame by the given time
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
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
def get_map_ranking(time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'")):
    """
    Endpoint to get the AQI ranking of districts and assign colors based on the provided color palette.
    """
    try:
        # Filter the DataFrame by the given time
        filtered_df = forecasted_pollutant_df[forecasted_pollutant_df['date'] == time]
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time.")
        
        # Sort districts by AQI in ascending order
        sorted_df = filtered_df.sort_values(by='Aqi')
        # ensure there's no duplicate districts
        sorted_df = sorted_df.drop_duplicates(subset=['District'])
        
        # Assign colors based on the sorted order
        response = []
        for index, row in sorted_df.iterrows():
            color_index = index % len(color_palette)
            response.append({"district": row["District"], "aqi": row["Aqi"], "color": color_palette[color_index]})
        
        return {"map_ranking": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/historical_data")
def get_historical_data(
    time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'"),
    district: str = Query(..., description="District name"),
    duration: str = Query(..., description="Duration can be 'weekly', 'biweekly', 'monthly', or '2 months'")
):
    """
    Endpoint to get historical AQI data for a given district and time period.
    """
    try:
        # Convert time to datetime
        time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

        # Calculate date range based on duration
        if duration == 'weekly':
            start_date = time_dt - timedelta(days=7)
        elif duration == 'biweekly':
            start_date = time_dt - timedelta(days=14)
        elif duration == 'monthly':
            start_date = time_dt - timedelta(days=30)
        elif duration == '2 months':
            start_date = time_dt - timedelta(days=60)
        else:
            raise HTTPException(status_code=400, detail="Invalid duration. Choose from 'weekly', 'biweekly', 'monthly', or '2 months'.")
        
        # Filter the DataFrame by district and date range
        filtered_df = historical_df[
            (historical_df['District'] == district) &
            (historical_df['date'] >= start_date.strftime('%Y-%m-%d')) &
            (historical_df['date'] <= time_dt.strftime('%Y-%m-%d'))
        ]
        # droppig the unnamed column
        filtered_df = filtered_df.drop(columns=['Unnamed: 0'])
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters.")
        
        # selecting the date and aqi columns
        filtered_df = filtered_df[['date', 'Aqi']]

        # Return the filtered data as a JSON response
        return filtered_df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/forecast_data")
def get_forecast_data(
    time: str = Query(..., description="Time in format 'YYYY-MM-DD HH:00:00'"),
    district: str = Query(..., description="District name"),
    duration: str = Query(..., description="Duration can be 'weekly', 'biweekly', 'monthly', or '2 months'")
):
    """
    Endpoint to get AQI forecast data for a given district and time period.
    """
    try:
        # Convert time to datetime
        time_dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

        # Calculate end date based on duration
        if duration == 'weekly':
            end_date = time_dt + timedelta(days=7)
        elif duration == 'biweekly':
            end_date = time_dt + timedelta(days=14)
        elif duration == 'monthly':
            end_date = time_dt + timedelta(days=30)
        elif duration == '2 months':
            end_date = time_dt + timedelta(days=60)
        else:
            raise HTTPException(status_code=400, detail="Invalid duration. Choose from 'weekly', 'biweekly', 'monthly', or '2 months'.")
        
        # Filter the DataFrame by district and date range
        filtered_df = aqi_forecast_df[
            (aqi_forecast_df['District'] == district) &
            (aqi_forecast_df['date'] >= time_dt.strftime('%Y-%m-%d %H:00:00')) &
            (aqi_forecast_df['date'] <= end_date.strftime('%Y-%m-%d %H:00:00'))
        ]
        # removing the unnamed column
        filtered_df = filtered_df.drop(columns=['Unnamed: 0'])
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No forecast data found for the specified parameters.")

        # selecting the date and aqi columns
        filtered_df = filtered_df[['date', 'Aqi']]
        
        # Return the filtered data as a JSON response
        return filtered_df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example of how to run the FastAPI server with Uvicorn
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)


