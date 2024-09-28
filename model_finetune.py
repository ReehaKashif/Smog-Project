# fine_tune_module.py

import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import numpy as np
import pandas as pd
from smog_models import (
    PM10_CNN_LSTM, PM25_CNN_LSTM, carbon_monoxide_CNN_LSTM, 
    nitrogen_dioxide_CNN_LSTM, sulphur_dioxide_CNN_LSTM, ozone_CNN_LSTM, dust_CNN_LSTM
)
from loguru import logger

# Configure logger
logger.add("logs/model_finetuning.log", rotation="50 MB")

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Device selected: {device}")

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


def create_sequences(data, lookback):
    logger.info(f"Creating sequences with lookback period: {lookback}")
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    logger.info(f"Created {len(X)} sequences")
    return np.array(X), np.array(y)

def fine_tune_pollutant_model(pollutant, lookback=300, epochs=2):
    logger.info(f"Starting fine-tuning for {pollutant}")
    print(f'Fine-tuning {pollutant} model')

    try:
        # Load model, scaler, and new data
        model, scaler, data = load_model_and_scaler(pollutant)
        logger.info(f"Loaded model, scaler, and data for {pollutant}")
    except Exception as e:
        logger.error(f"Failed to load model, scaler, or data for {pollutant}: {e}")
        return

    # Scale the data
    new_scaled_data = scaler.transform(data)
    logger.info(f"Data for {pollutant} scaled using the loaded scaler")

    # Create sequences from new data
    X_new, y_new = create_sequences(new_scaled_data, lookback)
    X_new, y_new = torch.tensor(X_new, dtype=torch.float32), torch.tensor(y_new, dtype=torch.float32)

    # Move to device
    X_new, y_new = X_new.to(device), y_new.to(device)
    model = model.to(device)

    # Define loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    logger.info(f"Model, loss function, and optimizer configured for {pollutant}")

    # Fine-tune the model
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for i in range(len(X_new)):
            inputs = X_new[i:i+1]
            targets = y_new[i:i+1]

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(X_new)
        logger.info(f'Epoch [{epoch + 1}/{epochs}] for {pollutant}, Avg Loss: {avg_loss:.4f}')
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {avg_loss:.4f}')

    # Save the fine-tuned model
    model_save_path = f'pol_models/{pollutant}_model_state.pt'
    torch.save(model.state_dict(), model_save_path)
    logger.info(f"Fine-tuning completed for {pollutant}, model saved at {model_save_path}")

def fine_tune_all_pollutants(lookback=300, epochs=3):
    pollutants = ['carbon_monoxide', 'dust', 'nitrogen_dioxide', 'ozone', 'pm10', 'pm2_5', 'sulphur_dioxide']
    
    for pollutant in pollutants:
        logger.info(f"Starting fine-tuning process for {pollutant}")
        fine_tune_pollutant_model(pollutant, lookback, epochs)
        logger.info(f"Completed fine-tuning for {pollutant}")
