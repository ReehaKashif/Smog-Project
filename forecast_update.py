import pandas as pd
from loguru import logger

# Set up logging
logger.add("logs/forecast_update.log", rotation="50 MB", level="INFO")

# Task 1: Update forecast data by merging with district info and saving the result
def update_forecast_data(forecast_file, output_file):
    try:
        logger.info(f"Processing forecast data from {forecast_file}...")

        # Load forecast data and district data
        forecasted_df = pd.read_csv(forecast_file)
        logger.info(f"Columns: {forecasted_df.columns}")
        logger.info(f"Sole loc id: {forecasted_df['location_id'][:10]}")
        
        district = pd.read_csv('Join.csv')[['id', 'district']]
        # renaming id as location_id in district
        district.rename(columns={'id':'location_id'}, inplace=True)
        logger.info(f"district tops : {district.head()}")

        # Convert 'location_id' to float for merging
        forecasted_df['location_id'] = forecasted_df['location_id'].astype(float)
        district['location_id'] = district['location_id'].astype(float)

        # Merge forecast data with district data
        forecasted_df = forecasted_df.merge(district, on='location_id', how='left')

        # Reorder columns alphabetically and capitalize column names
        forecasted_df = forecasted_df.reindex(sorted(forecasted_df.columns), axis=1)
        forecasted_df.columns = forecasted_df.columns.str.capitalize()

        # Save the processed forecast data to the output file
        forecasted_df.to_csv(output_file, index=False)
        logger.success(f"Saved updated forecast data to {output_file}")
    except Exception as e:
        logger.error(f"Error processing forecast data from {forecast_file}: {e}")

# Task 2: Calculate daily maximum AQI values
def calculate_daily_max_aqi(forecast_file, output_file):
    try:
        logger.info(f"Calculating daily max AQI values from {forecast_file}...")

        # Load forecast data
        forecasted_data = pd.read_csv(forecast_file)

        # renaming unnamed: 0 as date
        forecasted_data.rename(columns={'Unnamed: 0':'date'}, inplace=True)
        
        # Convert 'date' column to datetime
        forecasted_data['date'] = pd.to_datetime(forecasted_data['date'])

        # Group by 'district' and 'date', then calculate the daily max AQI for each district
        daily_max_forecast = forecasted_data.groupby(['District', forecasted_data['date'].dt.date])['Aqi'].max().reset_index()

        # Rename columns
        daily_max_forecast.columns = ['District', 'date', 'Aqi']

        # Save the daily maximum AQI data
        daily_max_forecast.to_csv(output_file, index=False)
        logger.success(f"Saved daily max AQI data to {output_file}")
    except Exception as e:
        logger.error(f"Error calculating daily max AQI from {forecast_file}: {e}")

# Task 3: Update historical data with new forecast data
def update_historical_data(historical_file, new_data_file, output_file):
    try:
        logger.info(f"Updating historical data with {new_data_file}...")

        # Load historical and new forecast data
        historical_data = pd.read_csv(historical_file)
        newest_data = pd.read_csv(new_data_file)

        # Convert 'date' columns to datetime
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        newest_data['date'] = pd.to_datetime(newest_data['date'])

        # Combine both datasets, giving priority to the new data in case of duplicates
        combined_data = pd.concat([newest_data, historical_data]).drop_duplicates(subset=['District', 'date'], keep='first')

        # Sort by district and date
        combined_data.sort_values(by=['District', 'date'], inplace=True)

        # Save the updated historical data
        combined_data.to_csv(output_file, index=False)
        logger.success(f"Updated historical data saved to {output_file}")
    except Exception as e:
        logger.error(f"Error updating historical data: {e}")

# Task 4 & 5: Process lagged data (7-day lag and 14-day lag)
def process_lagged_forecast(forecast_file, lag_days, output_file):
    try:
        logger.info(f"Processing {lag_days}-day lag forecast from {forecast_file}...")

        # Load forecast data
        forecast_lag = pd.read_csv(forecast_file)
        district = pd.read_csv('Join.csv')[['id', 'district']]
        # renaming id as location_id in district
        district.rename(columns={'id':'location_id'}, inplace=True)

        # Convert 'location_id' to float for merging
        forecast_lag['location_id'] = forecast_lag['location_id'].astype(float)
        district['location_id'] = district['location_id'].astype(float)

        # Merge with district data
        forecast_lag = forecast_lag.merge(district, on='location_id', how='left')
        
        # setting the index as the date column
        forecast_lag['date'] = forecast_lag.index
        
        # Convert 'date' column to datetime
        forecast_lag['date'] = pd.to_datetime(forecast_lag['date'])

        # Calculate daily maximum AQI for each district
        daily_max_lag = forecast_lag.groupby(['district', forecast_lag['date'].dt.date])['Aqi'].max().reset_index()

        # Rename columns
        daily_max_lag.columns = ['District', 'date', 'Aqi']

        # Save the lagged daily AQI data to output file
        daily_max_lag.to_csv(output_file, index=False)
        logger.success(f"Saved {lag_days}-day lag forecast data to {output_file}")
    except Exception as e:
        logger.error(f"Error processing {lag_days}-day lag forecast: {e}")

# Function to run all tasks sequentially
def run_all_forecast_updates():
    try:
        logger.info("Starting forecast update process...")

        # Task 1: Update the 0-day lag forecast
        update_forecast_data('data_forecast/forecast_0_day_lag.csv', 'fastapi-server/forecasted_pollutant.csv')

        # Task 2: Calculate daily maximum AQI values
        calculate_daily_max_aqi('fastapi-server/forecasted_pollutant.csv', 'fastapi-server/daily_forecasted_data.csv')

        # Task 3: Update historical data with new forecast
        update_historical_data('fastapi-server/daily_historical_data.csv', 'new_data.csv', 'fastapi-server/daily_historical_data.csv')

        # Task 4: Process the 7-day lag forecast
        process_lagged_forecast('data_forecast/forecast_7_day_lag.csv', 7, 'fastapi-server/daily_7_days_lag_data.csv')

        # Task 5: Process the 14-day lag forecast
        process_lagged_forecast('data_forecast/forecast_14_day_lag.csv', 14, 'fastapi-server/daily_14_days_lag_data.csv')

        logger.success("All forecast update tasks completed successfully!")
        return True  # Indicate successful completion
    except Exception as e:
        logger.error(f"An error occurred during forecast update process: {e}")
        return False  # Indicate failure
