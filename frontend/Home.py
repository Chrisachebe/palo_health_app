import streamlit as st
import requests
def main():
    st.title("Data Access⁉️")

    # Call Flask backend
    try:
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            data = response.json()
            st.success(data["message"])  # Show Flask's message
        else:
            st.error("Failed to connect to backend.")
    except Exception as e:
        st.error(f"Error: {e}")

# Page configuration
st.set_page_config(
    page_title="HyGiah",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    """,
    unsafe_allow_html=True
)


# Home page content
st.title("Welcome to the L2B 💙")

# Make columns
col1, col2 = st.columns([1, 2])  # col1 is twice as wide as col2

col1.write(
    """
    L2B aggregates your health data from Google Fit, MyFitnessPal, and Weight Lifts.
    L2B is an acronym for Listen to Body. The name is unique to draw you in 😁
    
    At its core health is about maintaining equilibrium in the body. By monitoring all of your health data we make it easy
    to know what you really need to know about the data your body outputs. Your body speaks everyday, we are giving you a way to listen.
    At its core this is about information. Information if the power you need for a physical renewal. 
    Everything you need can be hooked up and displayed for all your health and fitness goals. 
    AI insights are included as well so you dont need to search for any symptoms
    Ultimately when alarm arise, your insights will show it.

    Use the sidebar to navigate to:
    - **Insights**: Get AI health insights based on your selected date or year.
    - **Health Metrics**: View raw health metrics in tables or charts.
    
    Stay on top of your health and make informed decisions!
    """
)

# Column for Images
with col2:
    st.image(
        "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bWFuJTIwaW4lMjBneW18ZW58MHx8MHx8fDA%3D",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
