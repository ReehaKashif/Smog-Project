import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import joblib
import os
from datetime import timedelta
from smog_models import (
    PM10_CNN_LSTM, PM25_CNN_LSTM, carbon_monoxide_CNN_LSTM, 
    nitrogen_dioxide_CNN_LSTM, sulphur_dioxide_CNN_LSTM, ozone_CNN_LSTM, dust_CNN_LSTM
)
from loguru import logger

# Set up logging with a file size limit of 50MB
logger.add("logs/forecasting.log", rotation="50 MB", level="INFO")
# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Device selected: {device}")

# Create sequences function
def create_sequences(data, lookback):
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i+lookback])
        y.append(data[i+lookback])
    logger.info(f"Created {len(X)} sequences with a lookback period of {lookback}.")
    return np.array(X), np.array(y)

# Dictionary mapping pollutant names to model classes and their parameters
model_mapping = {
    'pm10': {
        'class': PM10_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'pm2_5': {
        'class': PM25_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'carbon_monoxide': {
        'class': carbon_monoxide_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'nitrogen_dioxide': {
        'class': nitrogen_dioxide_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'sulphur_dioxide': {
        'class': sulphur_dioxide_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'ozone': {
        'class': ozone_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
    'dust': {
        'class': dust_CNN_LSTM,
        'params': {'input_size': 300, 'hidden_size': 50, 'num_layers': 2, 'output_size': 300}
    },
}

def load_model_and_scaler(pollutant):
    logger.info(f"Loading model and scaler for {pollutant}")
    try:
        # Get model class and parameters
        model_info = model_mapping.get(pollutant)
        if model_info is None:
            raise ValueError(f"No model found for pollutant: {pollutant}")
        
        model_class = model_info['class']
        params = model_info['params']
        
        # Instantiate the model architecture
        model = model_class(**params)
        model = model.to(device)

        # Load the state dict (weights) into the model, not the entire model object
        state_dict = torch.load(f'pol_models/{pollutant}_model_state.pt', map_location=device)
        model.load_state_dict(state_dict)
        
        # Load the scaler
        scaler = joblib.load(f'pol_scalers/{pollutant}_scaler.pkl')
        
        # Load the data
        data = pd.read_csv(f'pol_data/{pollutant}_data.csv', parse_dates=['date'], index_col='date')
        
        logger.info(f"Successfully loaded model, scaler, and data for {pollutant}")
        return model, scaler, data
    except Exception as e:
        logger.error(f"Error loading model, scaler, or data for {pollutant}: {e}")
        raise

# Forecasting function
def forecast_pollutant(model, scaler, data, lookback, total_days_to_predict):
    forecast_horizon = total_days_to_predict * 24  # Convert days to hours

    # Ensure we have enough historical data for past predictions
    data = data[-720:]  # Use the last 720 rows (e.g., 30 days of data)
    
    scaled_data = scaler.transform(data)
    X, _ = create_sequences(scaled_data, lookback)
    X = torch.tensor(X, dtype=torch.float32).to(device)

    last_sequence = X[-1].unsqueeze(0)  # Start with the last available sequence
    forecasted_values = []

    model.eval()
    with torch.no_grad():
        current_sequence = last_sequence
        for _ in range(forecast_horizon):
            prediction = model(current_sequence)
            forecasted_values.append(prediction.cpu().numpy())
            new_sequence = torch.cat((current_sequence[:, 1:, :], prediction.unsqueeze(1)), dim=1)
            current_sequence = new_sequence

    forecasted_values = np.concatenate(forecasted_values)
    forecasted_values_inverse = scaler.inverse_transform(forecasted_values)
    
    logger.info(f"Completed forecasting for {total_days_to_predict} days.")
    return forecasted_values_inverse

# Forecast with lag logic
def forecast_all_pollutants(days_to_predict, lookback=300):
    pollutants = ['carbon_monoxide', 'dust', 'nitrogen_dioxide', 'ozone', 'pm10', 'pm2_5', 'sulphur_dioxide']
    
    # Iterating through no lag, 7-day lag, and 14-day lag
    for lag_days in [0, 7, 14]:
        logger.info(f"Starting forecast with a {lag_days}-day lag.")
        
        total_days_to_predict = days_to_predict + lag_days  # Extend forecast horizon by lag days

        forecasted_data = []
        date = []
        location_id = []

        for pollutant in pollutants:
            model, scaler, data = load_model_and_scaler(pollutant)
            forecasted_values = forecast_pollutant(model, scaler, data, lookback, total_days_to_predict)

            # Creating a DataFrame for the pollutant
            forecasted_df = pd.DataFrame(forecasted_values, columns=data.columns)
            forecasted_df.index = pd.date_range(start=data.index[-1] - pd.Timedelta(days=lag_days) + pd.Timedelta(hours=1), 
                                                periods=total_days_to_predict * 24, freq='H')

            # Reverse the pivot operation
            reverted_df = forecasted_df.melt(ignore_index=False, var_name='location_id', value_name=pollutant)
            date.append(reverted_df.index)
            location_id.append(reverted_df['location_id'])
            forecasted_data.append(reverted_df[pollutant].values)
        
        # Combining pollutant data into a single DataFrame
        combined_forecast = pd.DataFrame(forecasted_data).T
        combined_forecast.columns = pollutants
        combined_forecast.index = date[0]
        combined_forecast['location_id'] = location_id[0]
        
        # Calculate AQI
        combined_forecast['Aqi'] = (
            combined_forecast['pm2_5'] * 0.25 +
            combined_forecast['pm10'] * 0.25 +
            combined_forecast['nitrogen_dioxide'] * 0.15 +
            combined_forecast['sulphur_dioxide'] * 0.1 +
            combined_forecast['carbon_monoxide'] * 0.1 +
            combined_forecast['ozone'] * 0.1 +
            combined_forecast['dust'] * 0.05
        )
        
        # Save the forecast to a CSV file
        os.makedirs("data_forecast", exist_ok=True)
        csv_filename = f'data_forecast/forecast_{lag_days}_day_lag.csv'
        combined_forecast.to_csv(csv_filename)
        logger.info(f"Saved forecast with a lag of {lag_days} days to {csv_filename}.")

# # Run forecast for the next 4 months (e.g., till December)
# days_to_predict = 120  # Approx. 4 months
# forecast_all_pollutants(days_to_predict, lookback=300)
