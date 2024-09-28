import streamlit as st
from loguru import logger
from model_forecast import forecast_all_pollutants

# Set up logging with a file size limit of 50MB
logger.add("logs/aqi_forecast.log", rotation="50 MB", level="INFO")

def forecast_page():
    st.title("Air Quality Forecasting")
    st.write("""
        Welcome to the air quality forecasting page. This tool allows you to forecast various pollutants 
        (PM 2.5, PM 10, Carbon Monoxide, etc.) over a four-month period with different lags (0 days, 7 days, 14 days).
    """)

    # Input for number of days to predict (default: 120 days)
    days_to_predict = st.number_input("Enter the number of days to predict (default: 120)", min_value=1, value=120, step=1)

    # Start forecasting when the button is clicked
    if st.button("Start Forecasting"):
        with st.spinner("Forecasting... Please wait."):
            try:
                forecast_all_pollutants(days_to_predict, lookback=300)
                st.success("Forecasting completed successfully!")
            except Exception as e:
                st.error(f"An error occurred during forecasting: {e}")
                logger.error(f"Error during forecasting: {e}")