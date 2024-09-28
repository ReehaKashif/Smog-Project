import streamlit as st
import os
from datetime import datetime
from data_update import recent_data_update as get_data
from loguru import logger

# Configure logger
logger.add("logs/data_update.log", rotation="50 MB")  # Log to a file with a size limit for rotation

def check_data_store():
    logger.info("Checking if 'data_store' folder exists.")
    if not os.path.exists('data_store'):
        logger.error("The `data_store` folder does not exist.")
        st.error("The `data_store` folder does not exist.")
        return False
    elif not os.listdir('data_store'):
        logger.warning("The `data_store` folder is empty.")
        st.warning("The `data_store` folder is empty.")
        return False
    else:
        logger.info("The `data_store` folder exists and is not empty.")
        st.success("The `data_store` folder exists and is not empty.")
        return True

def get_data_update():
    logger.info("Rendering the Data Update page.")
    st.title("Data Update")
    st.write("Select a start and end date to retrieve recent data for model fine-tuning.")
    st.write("When selecting the End date, make sure that it's a day before today so you can retrieve available data in the api.")

    # Date inputs for start and end date
    start_date = st.date_input("Start Date", datetime.now())
    end_date = st.date_input("End Date", datetime.now())
    
    st.write("Start Date:", start_date)
    st.write("End Date:", end_date)

    logger.info(f"Start Date: {start_date}, End Date: {end_date}")

    try:
        if start_date > end_date:
            logger.error("End date is before the start date.")
            st.error("End date must be after the start date.")
        else:
            if st.button("Get Data"):
                logger.info("Fetching data.")
                
                # Add spinner during the data collection process
                with st.spinner("Fetching data... Please wait."):
                    status = get_data(start_date, end_date)
                
                logger.info(f"Data fetching status: {status}")
                
                st.success(f"Data successfully fetched and stored from {start_date} to {end_date}!")
                
                if status == "Completed":
                    folder_status = check_data_store()
                    if folder_status:
                        logger.success("Data update completed successfully, `data_store` folder is not empty.")
                        st.success("Data update completed successfully.")
                        # Add a celebration with balloons
                        st.balloons()
                    else:
                        logger.warning("Data update completed but the `data_store` folder is empty.")
                        st.warning("Data update completed but the `data_store` folder is empty.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        st.error("An error occurred. Please try again.")
