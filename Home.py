import streamlit as st
import json
import pandas as pd
import re

# Configure the page
st.set_page_config(
    page_title="Instagram Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and extract JSON data from the text file.
def load_data(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    # Extract the JSON data portion that follows "Raw JSON Data:"
    match = re.search(r"Raw JSON Data:\n(.*?)(\n\n|$)", content, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            data = json.loads(json_str)
            return data
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")
            return None
    else:
        st.error("JSON data not found in file.")
        return None

# Function to format numbers with K, M, B suffixes
def format_number(num):
    if not isinstance(num, (int, float)):
        return num
    
    abs_num = abs(num)
    sign = -1 if num < 0 else 1
    
    if abs_num >= 1_000_000_000:
        return f"{sign * abs_num / 1_000_000_000:.1f}B"
    elif abs_num >= 1_000_000:
        return f"{sign * abs_num / 1_000_000:.1f}M"
    elif abs_num >= 1_000:
        return f"{sign * abs_num / 1_000:.1f}K"
    else:
        return str(num)

# Load the data and store in session state so it can be accessed by other pages
@st.cache_data
def load_cached_data():
    return load_data("data/instagram_data.txt")

data = load_cached_data()
if data is None:
    st.stop()

# Store data in session state for other pages to access
if "instagram_data" not in st.session_state:
    st.session_state.instagram_data = data

# Extract the main profile info from the data
profile = data.get("data", {})

# Dashboard title and profile header
st.title("Instagram Analytics Dashboard")
st.header(f"{profile.get('name', 'N/A')} (@{profile.get('screenName', 'N/A')})")

# Display profile in a more structured layout
col1, col2 = st.columns([1, 3])

with col1:
    if profile.get("image"):
        st.image(profile.get("image"), width=200)

with col2:
    st.markdown(profile.get("description", ""))
    
    # --- Key Statistics ---
    st.subheader("Key Statistics")
    # Some community metrics might be available in a nested 'community' key.
    community = data.get("community", {})
    
    stats_cols = st.columns(4)
    stats_cols[0].metric("Followers", format_number(profile.get("usersCount", "N/A")))
    
    # Add a guide for navigation
    st.markdown("---")
    st.markdown("""
    ## Navigate the Dashboard
    
    Use the sidebar to explore different sections of the dashboard:
    
    - **Home** - Profile overview and key statistics
    - **Audience Demographics** - Analyze follower demographics by country and city
    - **Tags Analysis** - Explore profile tags, suggested tags and rating tags
    - **About** - Information about this dashboard
    """)