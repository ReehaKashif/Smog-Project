import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import joblib
from datetime import timedelta

class PM10_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(PM10_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, 300, 300)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, 300, 300) for CNN
        x = self.conv1(x)  # Output shape: (batch_size, 64, 300)
        x = self.relu(x)
        x = self.pool(x)  # Output shape: (batch_size, 64, 150)
        
        x = self.conv2(x)  # Output shape: (batch_size, 128, 150)
        x = self.relu(x)
        x = self.pool(x)  # Output shape: (batch_size, 128, 75)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, 75, 128) for LSTM
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Output shape: (batch_size, 75, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction, shape: (batch_size, hidden_size)
        out = self.relu(out)
        out = self.fc2(out)  # Final output shape: (batch_size, output_size) = (batch_size, 300)
        return out

    
class PM25_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(PM25_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = self.dropout(x)
        
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
class carbon_monoxide_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(carbon_monoxide_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
class nitrogen_dioxide_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(nitrogen_dioxide_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
class sulphur_dioxide_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(sulphur_dioxide_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
    
    
class ozone_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(ozone_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
class dust_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(dust_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out



class aqi_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(aqi_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
    
class aqi_last_14_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(aqi_last_14_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out
    
class aqi_last_7_CNN_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(aqi_last_7_CNN_LSTM, self).__init__()
        
        # CNN layers
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.5)
        
        # LSTM layers
        self.lstm = nn.LSTM(128, hidden_size, num_layers, batch_first=True)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, output_size)
    
    def forward(self, x):
        # Initial input shape: (batch_size, lookback, num_features)
        x = x.permute(0, 2, 1)  # Change shape to (batch_size, num_features, lookback)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 64, lookback//2)
        
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)  # Shape: (batch_size, 128, lookback//4)
        x = x.permute(0, 2, 1)  # Change shape back to (batch_size, lookback//4, 128)
        x = self.dropout(x)
        
        # LSTM forward
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))  # Shape: (batch_size, lookback//4, hidden_size)
        
        # Fully connected layers
        out = self.fc1(out[:, -1, :])  # Use the last time step's output for prediction
        out = self.relu(out)
        out = self.fc2(out)  # Shape: (batch_size, output_size)
        return out