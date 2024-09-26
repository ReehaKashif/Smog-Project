import streamlit as st

def home():
    st.title("SMOG Prediction and Model Update Application")

    st.write("""
    Welcome to the **SMOG Prediction and Model Update** app! This application is designed to streamline the process of making accurate forecasts based on deep learning models.
    
    ### Features:
    1. **Get Recent Data**: Fetch the latest data from the specified API.
    2. **Data Processing**: Automatically process the collected data for fine-tuning the model.
    3. **Model Fine-tuning**: Update the existing deep learning model with new data to improve accuracy.
    4. **New Forecasts**: Generate new predictions using the fine-tuned model.
    5. **Database Updates**: Save the new forecasts back into the database.

    This app is designed to facilitate efficient, real-time model updates and accurate predictions.
    """)

    st.write("Navigate through the app using the sidebar to begin the process.")
