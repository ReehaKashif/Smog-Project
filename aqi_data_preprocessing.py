import streamlit as st
from data_processing import data_loader, preprocess_data
from loguru import logger
import pandas as pd

# Configure logger
logger.add("logs/data_preprocessing_streamlit.log", rotation="50 MB")

def data_preprocessing_page():
    st.title("Data Preprocessing for Model Fine-tuning")

    st.write("""
        This page allows you to load the collected data, merge it with location information, 
        and prepare it for fine-tuning a deep learning model. 
    """)

    if st.button("Load Downloaded Data"):
        with st.spinner("Loading data..."):
            try:
                data = data_loader("./data_store")
                st.success("Data successfully loaded!")
                st.write("Top 10 rows of the data:")
                st.write(data.head(10))
                logger.info("Data successfully loaded and displayed.")
            except Exception as e:
                st.error("An error occurred while loading the data.")
                logger.exception(f"Error loading data: {e}")

    if st.button("Prepare Data for Fine-tuning"):
        with st.spinner("Processing data..."):
            try:
                data = data_loader("./data_store")  # Reload data if needed
                status = preprocess_data(data)
                if status == "Completed":
                    st.balloons()
                    st.success("Data successfully processed for fine-tuning!")
                    logger.info("Data preprocessing completed successfully.")
                    st.write("You may now proceed to the next phase: **Model Fine-tuning**.")
                else:
                    st.error("Data preprocessing failed.")
            except Exception as e:
                st.error("An error occurred during data preprocessing.")
                logger.exception(f"Error in data preprocessing: {e}")

# Call this function in your Streamlit app
# data_preprocessing_page()
