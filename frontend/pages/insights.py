# pages/insights.py
import streamlit as st
import requests

# Flask backend endpoint for insights
INSIGHTS_URL = "http://127.0.0.1:5000/api/insights"

st.set_page_config(page_title="Insights", layout="wide")

# Styling
st.markdown(
    """
    <style>
    /* Apply rounded corners to all images */
    img {
        border-radius: 40px;   /* Adjust radius here */
        border: 4px solid white;   /* Border thickness and color */
    }
    div[data-testid="stMarkdownContainer"] {
        font-size: 20px !important;
        line-height: 1.6 !important;
    }
    /* Sidebar background pattern */
    [data-testid="stSidebar"] {background-color: #491778;
    opacity: 0.8;
    background-image: radial-gradient( ellipse farthest-corner at 10px 10px , #a52828, #a52828 50%, #491778 50%);
    background-size: 10px 10px;
    }

    """,
    unsafe_allow_html=True
)

st.title("💡 Health Insights")

# Sidebar filter
st.sidebar.header("Filters")
date_filter = st.sidebar.text_input("Enter date (YYYY-MM-DD)")
year_filter = st.sidebar.text_input("Enter year (YYYY)")

# Fetch insights from backend
def get_insights(date=None, year=None):
    try:
        payload = {}
        if date:
            payload["date"] = date
        elif year:
            payload["year"] = year
        else:
            return {"insight": "Awaiting date selection..."}  # default message

        response = requests.post(INSIGHTS_URL, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"insight": "Error fetching insights from backend."}
    except Exception as e:
        return {"insight": f"Error: {e}"}

# Main content: center column
col1, col2, col3 = st.columns([1, 2, 1])  # middle column wider
with col2:
    if not date_filter and not year_filter:
        st.info("Please select a date or year to get insights.")
    else:
        insights_data = get_insights(date_filter, year_filter)
        st.markdown("### Your AI Insights")
        st.markdown(insights_data.get("insight", "No insights available."), unsafe_allow_html=True)

# Images below (full width)
st.markdown("---")
st.subheader("💪 Fitness Goals")

# Replace these with your own URLs
image_urls = [
    "https://images.unsplash.com/photo-1692369608021-c722c4fc7088?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8d29ya291dCUyMGd5bXxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1554284126-aa88f22d8b74?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Z3ltJTIwZ3JvdXB8ZW58MHx8MHx8fDA%3D",
    "https://plus.unsplash.com/premium_photo-1663134230160-42cb7a37efb6?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8Y291cGxlJTIwZ3ltfGVufDB8fDB8fHww"
]

cols = st.columns(len(image_urls))
for i, url in enumerate(image_urls):
    cols[i].image(url, use_container_width=True, caption=f"Goal {i+1}")


st.write(
    """
    AI can help... A LOT
    """
)

