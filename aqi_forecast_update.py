import streamlit as st
from forecast_update import run_all_forecast_updates  # Assuming the functions are in forecast_update_functions.py
from loguru import logger

# Set up logging for Streamlit
logger.add("logs/streamlit_forecast_update.log", rotation="50 MB", level="INFO")

# Streamlit app layout
def forecast_update_app():
    st.title("Forecast Data Update Application")
    st.write("""
        This application is used to update the forecast data, process lagged data, and update historical data. 
        Click the button below to start the process.
    """)

    # Button to start the forecast update process
    if st.button("Start Forecast Data Update"):
        st.write("Updating forecast data...")

        # Call the function to run all forecast update tasks
        update_success = run_all_forecast_updates()

        if update_success:
            st.success("Forecast data updated successfully!")
            st.balloons()  # Show balloons for successful completion
        else:
            st.error("An error occurred during the forecast data update process.")

