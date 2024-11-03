import requests_cache
import pandas as pd
from retry_requests import retry
import openmeteo_requests  # Assuming you have the openmeteo_requests module
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_air_quality_data(csv_path):
    # Load longitude and latitude values from CSV
    location_data = pd.read_csv(csv_path)

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Set start and end dates based on the current date
    current_date = datetime.now()
    start_date = current_date - timedelta(days=30)  # 30 days before
    end_date = current_date + timedelta(days=2)     # 2 days ahead

    # Function to fetch and process data for a single location
    def fetch_air_quality_data(latitude, longitude):
        # Make API requests for air quality
        air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        air_quality_params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        # Fetch air quality data
        air_quality_response = openmeteo.weather_api(air_quality_url, params=air_quality_params)[0]
        print(f"Air Quality Data for {latitude}°N, {longitude}°E")

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
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(air_quality_hourly.Time(), unit="s"),
                end=pd.to_datetime(air_quality_hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=air_quality_hourly.Interval()),
                inclusive="left"
            ),
            "PM10": hourly_pm10,
            "PM2.5": hourly_pm2_5,
            "Carbon Monoxide": hourly_carbon_monoxide,
            "Nitrogen Dioxide": hourly_nitrogen_dioxide,
            "Sulphur Dioxide": hourly_sulphur_dioxide,
            "Ozone": hourly_ozone,
            "Dust": hourly_dust,
            "Latitude": latitude,
            "Longitude": longitude
        }

        # Return the DataFrame
        return pd.DataFrame(data=hourly_data)

    # Create an empty list to store all dataframes for each location
    all_dataframes = []

    # Use ThreadPoolExecutor to fetch data concurrently
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = [executor.submit(fetch_air_quality_data, row['latitude'], row['longitude']) for _, row in location_data.iterrows()]

        # Collect results as they complete
        for future in as_completed(futures):
            all_dataframes.append(future.result())

    # Combine all individual DataFrames into one
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    return combined_df


def calculate_contributions(merged_data):
    # Perform Vehicle calculations
    merged_data['Veh_CO'] = merged_data['Carbon Monoxide'] * merged_data['Veh_CO_Formula']
    merged_data['Veh_Dust'] = merged_data['Dust'] * merged_data['Veh_Dust_Formula']
    merged_data['Veh_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Veh_NO2_Formula']
    merged_data['Veh_O3'] = merged_data['Ozone'] * merged_data['Veh_O3_Formula']
    merged_data['Veh_PM10'] = merged_data['PM10'] * merged_data['Veh_PM10_Formula']
    merged_data['Veh_PM25'] = merged_data['PM2.5'] * merged_data['Veh_PM2.5_Formula']
    merged_data['Veh_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Veh_SO2_Formula']
    merged_data['Vehicle'] = (merged_data[['Veh_CO', 'Veh_Dust', 'Veh_NO2', 'Veh_O3',
                                           'Veh_PM10', 'Veh_PM25', 'Veh_SO2']].sum(axis=1))

    # Perform Industry calculations
    merged_data['Ind_CO'] = merged_data['Carbon Monoxide'] * merged_data['Ind_CO_Formula']
    merged_data['Ind_Dust'] = merged_data['Dust'] * merged_data['Ind_Dust_Formula']
    merged_data['Ind_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Ind_NO2_Formula']
    merged_data['Ind_O3'] = merged_data['Ozone'] * merged_data['Ind_O3_Formula']
    merged_data['Ind_PM10'] = merged_data['PM10'] * merged_data['Ind_PM10_Formula']
    merged_data['Ind_PM25'] = merged_data['PM2.5'] * merged_data['Ind_PM2.5_Formula']
    merged_data['Ind_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Ind_SO2_Formula']
    merged_data['Indrusty'] = (merged_data[['Ind_CO', 'Ind_Dust', 'Ind_NO2', 'Ind_O3',
                                            'Ind_PM10', 'Ind_PM25', 'Ind_SO2']].sum(axis=1))

    # Perform Residential calculations
    merged_data['Res_CO'] = merged_data['Carbon Monoxide'] * merged_data['Res_CO_Formula']
    merged_data['Res_Dust'] = merged_data['Dust'] * merged_data['Res_Dust_Formula']
    merged_data['Res_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Res_NO2_Formula']
    merged_data['Res_O3'] = merged_data['Ozone'] * merged_data['Res_O3_Formula']
    merged_data['Res_PM10'] = merged_data['PM10'] * merged_data['Res_PM10_Formula']
    merged_data['Res_PM25'] = merged_data['PM2.5'] * merged_data['Res_PM2.5_Formula']
    merged_data['Res_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Res_SO2_Formula']
    merged_data['Residential'] = (merged_data[['Res_CO', 'Res_Dust', 'Res_NO2', 'Res_O3',
                                               'Res_PM10', 'Res_PM25', 'Res_SO2']].sum(axis=1))

    # Perform Misc calculations
    merged_data['Misc_CO'] = merged_data['Carbon Monoxide'] * merged_data['Misc_CO_Formula']
    merged_data['Misc_Dust'] = merged_data['Dust'] * merged_data['Misc_Dust_Formula']
    merged_data['Misc_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Misc_NO2_Formula']
    merged_data['Misc_O3'] = merged_data['Ozone'] * merged_data['Misc_O3_Formula']
    merged_data['Misc_PM10'] = merged_data['PM10'] * merged_data['Misc_PM10_Formula']
    merged_data['Misc_PM25'] = merged_data['PM2.5'] * merged_data['Misc_PM2.5_Formula']
    merged_data['Misc_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Misc_SO2_Formula']
    merged_data['Misc'] = (merged_data[['Misc_CO', 'Misc_Dust', 'Misc_NO2', 'Misc_O3',
                                        'Misc_PM10', 'Misc_PM25', 'Misc_SO2']].sum(axis=1))

    # Perform Construction calculations
    merged_data['Cons_CO'] = merged_data['Carbon Monoxide'] * merged_data['Cons_CO_Formula']
    merged_data['Cons_Dust'] = merged_data['Dust'] * merged_data['Cons_Dust_Formula']
    merged_data['Cons_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Cons_NO2_Formula']
    merged_data['Cons_O3'] = merged_data['Ozone'] * merged_data['Cons_O3_Formula']
    merged_data['Cons_PM10'] = merged_data['PM10'] * merged_data['Cons_PM10_Formula']
    merged_data['Cons_PM25'] = merged_data['PM2.5'] * merged_data['Cons_PM2.5_Formula']
    merged_data['Cons_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Cons_SO2_Formula']
    merged_data['Construction'] = (merged_data[['Cons_CO', 'Cons_Dust', 'Cons_NO2', 'Cons_O3',
                                                'Cons_PM10', 'Cons_PM25', 'Cons_SO2']].sum(axis=1))

    # Perform Agriculture calculations
    merged_data['Agr_CO'] = merged_data['Carbon Monoxide'] * merged_data['Agr_CO_Formula']
    merged_data['Agr_Dust'] = merged_data['Dust'] * merged_data['Agr_Dust_Formula']
    merged_data['Agr_NO2'] = merged_data['Nitrogen Dioxide'] * merged_data['Agr_NO2_Formula']
    merged_data['Agr_O3'] = merged_data['Ozone'] * merged_data['Agr_O3_Formula']
    merged_data['Agr_PM10'] = merged_data['PM10'] * merged_data['Agr_PM10_Formula']
    merged_data['Agr_PM25'] = merged_data['PM2.5'] * merged_data['Agr_PM2.5_Formula']
    merged_data['Agr_SO2'] = merged_data['Sulphur Dioxide'] * merged_data['Agr_SO2_Formula']
    merged_data['Agriculture'] = (merged_data[['Agr_CO', 'Agr_Dust', 'Agr_NO2', 'Agr_O3',
                                               'Agr_PM10', 'Agr_PM25', 'Agr_SO2']].sum(axis=1))

    # Calculate sum_sum and contributions
    merged_data['sum_sum'] = merged_data[['Vehicle', 'Indrusty', 'Residential', 'Misc', 'Construction', 'Agriculture']].sum(axis=1)

    # Contribution calculations
    merged_data['Vehicle%'] = (merged_data['Vehicle'] / merged_data['sum_sum']) * 100
    merged_data['Industry%'] = (merged_data['Indrusty'] / merged_data['sum_sum']) * 100
    merged_data['Residential%'] = (merged_data['Residential'] / merged_data['sum_sum']) * 100
    merged_data['Misc%'] = (merged_data['Misc'] / merged_data['sum_sum']) * 100
    merged_data['Construction%'] = (merged_data['Construction'] / merged_data['sum_sum']) * 100
    merged_data['Agriculture%'] = (merged_data['Agriculture'] / merged_data['sum_sum']) * 100

    # Select the final output columns
    result = merged_data[['id', 'district_id',  'District','date', 'Vehicle', 'Indrusty', 'Residential',
                          'Misc', 'Construction', 'Agriculture', 'sum_sum', 'Vehicle%',
                          'Industry%', 'Residential%', 'Misc%',
                          'Construction%', 'Agriculture%']]

    return result


def process_openmeteo_data(location_csv_path="location_smog1.csv", formula_sheet_path="FormulaSheet.csv", output_csv_path='contribution_results.csv'):
    """
    This function processes the Open-Meteo data by merging it with location data and a formula sheet,
    calculates contributions from different pollution sources, and saves the final result to a CSV.
    
    Parameters:
    - combined_df (DataFrame): The initial data collected from Open-Meteo.
    - location_csv_path (str): Path to the CSV file containing location data for matching IDs and Districts.
    - formula_sheet_path (str): Path to the formula sheet CSV file for calculating contributions.
    - output_csv_path (str): Path where the final CSV file will be saved.
    
    Returns:
    - result (DataFrame): The final processed DataFrame with contribution percentages.
    """
    
    combined_df = get_air_quality_data("location_smog.csv")
    
    # Load location data for matching IDs and Districts
    location_df = pd.read_csv(location_csv_path)

    # Merge combined_df with location_df to add district information
    combined_lat_col = 'Latitude'
    combined_lon_col = 'Longitude'
    loc_lat_col = 'Latitude'
    loc_lon_col = 'Longitude'

    data = pd.merge(
        combined_df,
        location_df[[loc_lat_col, loc_lon_col, 'district_id', 'District']],
        left_on=[combined_lat_col, combined_lon_col],
        right_on=[loc_lat_col, loc_lon_col],
        how='left'
    )
    
    print(data.columns)

    # Drop the extra latitude and longitude columns from location_smog1.csv
    data.drop(columns=[loc_lat_col, loc_lon_col], inplace=True)

    # Add an 'id' column with a sequence starting from 1
    data['id'] = range(1, len(data) + 1)

    # Reorder columns to the specified format
    desired_order = [
        'id', 'district_id', 'District', 'date', 'Carbon Monoxide', 'Dust',
        'Nitrogen Dioxide', 'Ozone', 'PM10', 'PM2.5', 'Sulphur Dioxide'
    ]
    data = data[desired_order]

    # Load the formula sheet containing contribution formulas
    data_matrix = pd.read_csv(formula_sheet_path)

    # Merge the data with the formula sheet based on the 'District' column
    merged_data = pd.merge(data, data_matrix, left_on='District', right_on='Districts', how='left')

    # Calculate contributions using the calculate_contributions function
    result = calculate_contributions(merged_data)

    # Save the final result to a CSV file
    result.to_csv(output_csv_path, index=False)
    
    print(f"Data has been successfully processed and saved to {output_csv_path}")
    return result

# Example usage:
# Assuming `combined_df` is the DataFrame from the Open-Meteo API data collection step
# final_result = process_openmeteo_data('fastapi-server/location_smog1.csv', 'fastapi-server/FormulaSheet.csv')
# print(final_result.head())
