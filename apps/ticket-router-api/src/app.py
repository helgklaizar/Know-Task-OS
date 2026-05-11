import streamlit as st
import requests

st.set_page_config(page_title="Support Routing AI", page_icon="🎧", layout="centered")

st.title("🎧 Intelligent Support Router")
st.markdown("This ML system automatically determines the target department based on the ticket text.")

# API URL (FastAPI)
API_URL = "http://127.0.0.1:8000/predict"

ticket_text = st.text_area("Enter the customer ticket text:", height=150, placeholder="Example: I want a refund right now, the service is terrible!")

if st.button("Route Ticket 🚀"):
    if ticket_text.strip():
        with st.spinner("The model is analyzing the text..."):
            try:
                response = requests.post(API_URL, json={"text": ticket_text})
                if response.status_code == 200:
                    data = response.json()
                    department = data["department"]
                    confidence = data["confidence"]
                    
                    st.success(f"**Target Department:** {department}")
                    st.info(f"**Network Confidence:** {confidence * 100:.1f}%")
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to the API. Is the FastAPI server running?\n{e}")
    else:
        st.warning("Please enter the ticket text.")
