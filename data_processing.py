import pandas as pd
import numpy as np
import os
from loguru import logger

# Configure logging
logger.add("logs/data_preprocessing.log", rotation="50 MB")

# reading files in the data_store folder
data_folder = "./data_store"
data_files = os.listdir(data_folder)

# data_loading function
def data_loader(data_folder):
    logger.info(f"Starting data loading from the folder: {data_folder}")
    data = []
    
    for file in data_files:
        file_path = os.path.join(data_folder, file)
        logger.info(f"Reading file: {file}")
        df = pd.read_csv(file_path)
        data.append(df)
    
    logger.info("Merging data into a single dataframe.")
    final_data = pd.concat(data, axis=0)

    logger.info("Merging the data with location data.")
    location_data = pd.read_csv("locations.csv")
    final_data_1 = pd.merge(final_data, location_data, on=["latitude", "longitude"], how="left")
    final_data_1["id"] = final_data_1["id"].astype(float)

    logger.info("Dropping latitude and longitude columns.")
    final_data_2 = final_data_1.drop(["latitude", "longitude"], axis=1)

    logger.info("Renaming 'id' to 'location_id'.")
    final_data_2.rename(columns={"id": "location_id"}, inplace=True)

    logger.info("Converting 'date' column to datetime and setting as the index.")
    final_data_2["date"] = pd.to_datetime(final_data_2["date"])
    final_data_3 = final_data_2.set_index("date")

    logger.info("Loading district dataset and merging with forecasted data.")
    district = pd.read_csv('Join.csv')
    district = district.rename(columns={'id': 'location_id'})
    district = district[['location_id', 'district']]

    index = final_data_3.index
    logger.debug(f"Data index: {index}")

    logger.info("Converting 'location_id' to float and merging with district data.")
    final_data_3['location_id'] = final_data_3['location_id'].astype(float)
    district['location_id'] = district['location_id'].astype(float)
    final_data_3 = final_data_3.merge(district, on='location_id', how='left') 

    logger.info("Calculating AQI.")
    final_data_3['Aqi'] = (final_data_3['pm2_5'] * 0.25 + final_data_3['pm10'] * 0.25 +
                           final_data_3['nitrogen_dioxide'] * 0.15 + final_data_3['sulphur_dioxide'] * 0.1 +
                           final_data_3['carbon_monoxide'] * 0.1 + final_data_3['ozone'] * 0.1 +
                           final_data_3['dust'] * 0.05)

    logger.info("Rewriting column names in alphabetical order and capitalizing pollutant names.")
    final_data_3 = final_data_3.reindex(sorted(final_data_3.columns), axis=1)
    final_data_3.columns = final_data_3.columns.str.capitalize()

    final_data_3['date'] = index
    final_data_3['date_only'] = final_data_3['date'].dt.date

    # logger.info("Calculating daily maximum AQI for each district.")
    # daily_max_aqi = final_data_3.groupby(['date_only', 'District'])['Aqi'].max().reset_index()

    # daily_max_aqi.columns = ['Date', 'District', 'Max_Aqi']
    # logger.info("Data loading and AQI calculation completed successfully.")
    
    # saving date as the index
    # final_data_3.index = index
    
    # saving the data
    final_data_3.to_csv('new_data.csv', index=False)
    
    return final_data_3

def preprocess_data(data):
    logger.info("Starting data preprocessing for fine-tuning.")
    pollutants = ['Pm10', 'Pm2_5', 'Carbon_monoxide', 'Nitrogen_dioxide', 'Sulphur_dioxide', 'Ozone', 'Dust']
    for pollutant in pollutants:
        logger.info(f"Processing data for {pollutant}.")
        pivot_df = data.pivot_table(index='date', columns='Location_id', values=pollutant.capitalize())
        pivot_df = pivot_df.sort_index(axis=1)
        file_path = f'pol_data/{pollutant.lower()}_data.csv'
        pivot_df.to_csv(file_path, index=True)
        logger.info(f"Saved {pollutant} data to {file_path}.")
    
    logger.info("Data preprocessing completed.")
    return "Completed"
