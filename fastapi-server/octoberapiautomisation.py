import requests_cache
import pandas as pd
from retry_requests import retry
import openmeteo_requests
from datetime import datetime, timedelta
from connect_db import save_dataframe_to_db

def process_air_quality_data():
    # File paths
    csv_path = "location_smog.csv"
    formula_sheet_path = "FormulaSheet.csv"
    output_csv_path = "merged_data.csv"
    api_key = "dmjxSgVmXqx5O1Iq"

    # Load location data
    location_data = pd.read_csv(csv_path)

    # Initialize sessions for API calls
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Set dates to one day before the current date
    current_date = datetime.now()
    start_date = current_date - timedelta(days=1)
    end_date = current_date - timedelta(days=1)

    # Prepare to collect data
    all_dataframes = []

    # Process each location
    for index, row in location_data.iterrows():
        latitude = row['latitude']
        longitude = row['longitude']

        # API call
        air_quality_url = "https://customer-air-quality-api.open-meteo.com/v1/air-quality"
        air_quality_params = {
            "apikey": api_key,
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust"],
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
        air_quality_response = openmeteo.weather_api(air_quality_url, params=air_quality_params)[0]

        # Extract and process hourly data
        air_quality_hourly = air_quality_response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(air_quality_hourly.Time(), unit="s"),
                end=pd.to_datetime(air_quality_hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=air_quality_hourly.Interval()),
                inclusive="left"
            ),
            "PM10": air_quality_hourly.Variables(0).ValuesAsNumpy(),
            "PM2.5": air_quality_hourly.Variables(1).ValuesAsNumpy(),
            "Carbon Monoxide": air_quality_hourly.Variables(2).ValuesAsNumpy(),
            "Nitrogen Dioxide": air_quality_hourly.Variables(3).ValuesAsNumpy(),
            "Sulphur Dioxide": air_quality_hourly.Variables(4).ValuesAsNumpy(),
            "Ozone": air_quality_hourly.Variables(5).ValuesAsNumpy(),
            "Dust": air_quality_hourly.Variables(6).ValuesAsNumpy(),
            "Latitude": latitude,
            "Longitude": longitude
        }
        all_dataframes.append(pd.DataFrame(hourly_data))

    # Combine all DataFrames
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    # Merge with location data
    location_df = pd.read_csv(csv_path)
    data = pd.merge(
        combined_df,
        location_df[['latitude', 'longitude', 'id', 'district']],
        left_on=['Latitude', 'Longitude'],
        right_on=['latitude', 'longitude'],
        how='left'
    )
    data.drop(columns=['latitude', 'longitude'], inplace=True)

    # Read the formula sheet
    data_matrix = pd.read_csv(formula_sheet_path)
    merged_data = pd.merge(data, data_matrix, left_on='district', right_on='Districts', how='left')

    # Perform calculations
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
        merged_data['Industry'] = (merged_data[['Ind_CO', 'Ind_Dust', 'Ind_NO2', 'Ind_O3',
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
        merged_data['Sum_of_Sources'] = merged_data[['Vehicle', 'Industry', 'Residential', 'Misc', 'Construction', 'Agriculture']].sum(axis=1)


        merged_data['Vehicle_percentage'] = (merged_data['Vehicle'] / merged_data['Sum_of_Sources']) * 100
        merged_data['Industry_percentage'] = (merged_data['Industry'] / merged_data['Sum_of_Sources']) * 100
        merged_data['Residential_percentage'] = (merged_data['Residential'] / merged_data['Sum_of_Sources']) * 100
        merged_data['Misc_percentage'] = (merged_data['Misc'] / merged_data['Sum_of_Sources']) * 100
        merged_data['Construction_percentage'] = (merged_data['Construction'] / merged_data['Sum_of_Sources']) * 100
        merged_data['Agriculture_percentage'] = (merged_data['Agriculture'] / merged_data['Sum_of_Sources']) * 100

        result = merged_data[['district','date', 'Vehicle', 'Industry', 'Residential',
                          'Misc', 'Construction', 'Agriculture', 'Sum_of_Sources', 'Vehicle_percentage',
                          'Industry_percentage', 'Residential_percentage', 'Misc_percentage',
                          'Construction_percentage', 'Agriculture_percentage']]
        result.rename(columns={'district': 'District'}, inplace=True)
        return result

    # Final results
    result = calculate_contributions(merged_data)

    # Save the result
    result.to_csv(output_csv_path, index=False)
    save_dataframe_to_db(result)

    return result

# Call the function
result = process_air_quality_data()
