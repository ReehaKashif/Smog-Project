# app_finetune.py

import streamlit as st
from model_finetune import fine_tune_all_pollutants
from loguru import logger

# Configure logger
logger.add("logs/streamlit_finetune.log", rotation="50 MB")

def fine_tune_app():
    # Introduction
    st.title("Model Fine-tuning Page")
    st.write("""
        Welcome to the **Model Fine-tuning** page. This page allows you to fine-tune your models for various pollutants, including:
        - Carbon Monoxide
        - Dust
        - Nitrogen Dioxide
        - Ozone
        - PM 10
        - PM 2.5
        - Sulphur Dioxide

        Click the "Fine-tune Models" button below to start the fine-tuning process. Once completed, you'll receive confirmation.
    """)

    # Button to start fine-tuning
    if st.button("Fine-tune Models"):
        with st.spinner("Fine-tuning models... Please wait."):
            try:
                logger.info("User initiated fine-tuning process.")
                fine_tune_all_pollutants(lookback=300, epochs=3)
                logger.info("Fine-tuning process completed successfully.")
                
                # Feedback after fine-tuning
                st.success("Fine-tuning process completed successfully!")
                st.balloons()
            except Exception as e:
                logger.error(f"An error occurred during fine-tuning: {e}")
                st.error("An error occurred during fine-tuning. Please check the logs for more information.")

    st.write("---")
    st.write("**Next Step**: Proceed to the **Model Prediction** phase to generate forecasts using the fine-tuned models.")

# Run the app
# if __name__ == "__main__":
#     fine_tune_app()
