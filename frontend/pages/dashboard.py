import streamlit as st
import requests
import pandas as pd


st.title("Cumulative Health📊 ")

# Home page content
st.write(
    """
    Home for your metrics of health
    """
)

# Flask backend URL (make sure Flask is running)
BACKEND_URL = "http://127.0.0.1:5000/api/patients"

st.set_page_config(page_title="Dashboard", layout="wide")


# Sidebar filters
st.sidebar.header("Filters")
date_filter = st.sidebar.text_input("Enter date (YYYY-MM-DD)")
year_filter = st.sidebar.text_input("Enter year (YYYY)")

# Function to fetch data from Flask
@st.cache_data
def fetch_data(date=None, year=None):
    try:
        params = {}
        if date:
            params["date"] = date
        if year:
            params["year"] = year
        response = requests.get(BACKEND_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return {}

# Fetch patient + average weight data
data = fetch_data(date_filter, year_filter)

col1, col2 = st.columns(2)

# Column 1 → Patient Table
with col1:
    st.subheader("📋 Your Data")
    if "patients" in data and data["patients"]:
        df_patients = pd.DataFrame(data["patients"])
        st.dataframe(df_patients, use_container_width=True)
    else:
        st.info("No patient data available.")

# Column 2 → Average Weight Line Chart
with col2:
    st.subheader("📈 Average Weight Per Year")
    if "average_weights" in data and data["average_weights"]:
        df_weights = pd.DataFrame(data["average_weights"])
        df_weights["year"] = df_weights["year"].astype(str)
        st.line_chart(df_weights.set_index("year")["avg_weight"])
    else:
        st.info("No average weight data available.")
