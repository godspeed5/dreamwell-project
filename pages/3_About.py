import streamlit as st

# Configure the page
st.set_page_config(
    page_title="About - Instagram Analytics",
    page_icon="ℹ️",
    layout="wide"
)

st.title("About This Dashboard")

st.markdown("""
## Instagram Analytics Dashboard

This dashboard provides insights into an Instagram profile's audience and engagement metrics.

### Features

- **Profile Overview**: Basic profile information and key statistics
- **Audience Demographics**: Geographic distribution of followers by country and city
- **Tags Analysis**: Explore profile tags, suggested tags, and rating tags

### How to Use

1. Start from the Home page to load the profile data
2. Navigate through the different sections using the sidebar
3. Explore the visualizations and insights

### Data Source

The data is loaded from a text file containing Instagram profile analytics in JSON format.

---

Created for Dreamwell Hackathon
""")