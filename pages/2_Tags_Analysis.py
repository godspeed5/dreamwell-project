import streamlit as st
import streamlit.components.v1 as components  # Import the components module
import pandas as pd
import time
from pytrends.request import TrendReq

# Configure the page
st.set_page_config(
    page_title="Tags Analysis - Instagram Analytics",
    page_icon="🏷️",
    layout="wide"
)

# Initialize pytrends
@st.cache_resource
def get_pytrends():
    return TrendReq(hl='en-US', tz=360)

pytrends = get_pytrends()

# Function to get Google Trends link for a keyword
def get_trends_link(keyword):
    encoded_keyword = keyword.replace(" ", "+")
    return f"https://trends.google.com/trends/explore?q={encoded_keyword}"

# Function to get interest over time data for a keyword
@st.cache_data(ttl=3600)
def get_interest_data(keyword):
    try:
        pytrends.build_payload([keyword], timeframe='today 12-m')
        interest_over_time_df = pytrends.interest_over_time()
        if not interest_over_time_df.empty:
            last_month = interest_over_time_df[-4:][keyword].mean()
            return round(last_month, 1)
        return "N/A"
    except Exception as e:
        st.error(f"Error fetching trends data: {str(e)}")
        return "N/A"

# Check if data is in session state
if "instagram_data" not in st.session_state:
    st.error("Please start from the Home page to load the data.")
    st.stop()

data = st.session_state.instagram_data
profile = data.get("data", {})

st.title("Tags Analysis")
st.write("Explore the tags associated with this Instagram profile.")

# Display profile and suggested tags
col1, col2 = st.columns(2)
with col1:
    st.subheader("Profile Tags")
    tags = profile.get("tags", [])
    if tags:
        tag_html = "".join([f'<span style="background-color:#6c5ce7; color:white; padding:2px 8px; border-radius:10px; margin:2px; display:inline-block;">{tag}</span>' for tag in tags])
        st.markdown(tag_html, unsafe_allow_html=True)
    else:
        st.info("No profile tags available.")
with col2:
    st.subheader("Suggested Tags")
    suggested = profile.get("suggestedTags", [])
    if suggested:
        tag_html = "".join([f'<span style="background-color:#00b894; color:white; padding:2px 8px; border-radius:10px; margin:2px; display:inline-block;">{tag}</span>' for tag in suggested])
        st.markdown(tag_html, unsafe_allow_html=True)
    else:
        st.info("No suggested tags available.")

# Rating tags section with Google Trends data
st.subheader("Rating Tags with Trend Analysis")
rating_tags = profile.get("ratingTags", [])
if rating_tags:
    rating_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, tag in enumerate(rating_tags):
        tag_name = tag.get("name", "")
        status_text.text(f"Fetching trends data for '{tag_name}'...")
        trends_link = get_trends_link(tag_name)
        interest = get_interest_data(tag_name)
        rating_data.append({
            "Tag": tag_name,
            "Trend Score (0-100)": interest,
            "Link": trends_link
        })
        progress_bar.progress((i + 1) / len(rating_tags))
        time.sleep(0.5)  # Delay to avoid rate limiting

    progress_bar.empty()
    status_text.empty()

    # Sort rating_data by "Trend Score (0-100)" in descending order.
    # For "N/A" entries, we treat them as -1 so they appear at the bottom.
    rating_data.sort(key=lambda x: x["Trend Score (0-100)"] if isinstance(x["Trend Score (0-100)"], (int, float)) else -1, reverse=True)
    
    # Create custom HTML table with sorted data
    html_table = """
    <table style="width:100%; border-collapse: collapse;">
      <thead>
        <tr style="background-color: #f0f2f6;">
          <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Tag</th>
          <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Trend Score (0-100)</th>
        </tr>
      </thead>
      <tbody>
    """
    
    for item in rating_data:
        tag = item["Tag"]
        trend_score = item["Trend Score (0-100)"]
        link = item["Link"]
        if trend_score != "N/A":
            trend_display = f'<a href="{link}" target="_blank">{trend_score}</a>'
        else:
            trend_display = f'<a href="{link}" target="_blank">N/A</a>'
        html_table += f"""
        <tr>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">{tag}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">{trend_display}</td>
        </tr>
        """
    
    html_table += """
      </tbody>
    </table>
    """
    
    components.html(html_table, height=300)
    st.info("Click on the trend score to see detailed Google Trends data for each tag.")
else:
    st.info("No rating tags available.")

st.markdown("""
---
### About Google Trends Data

The Trend Score represents the average search interest for each tag over the past month on a scale of 0-100:
* **100**: Peak popularity for the term.
* **50**: Half as popular as the peak.
* **0**: Insufficient data for the term.
""")

st.caption("""
Note: Google Trends data may be limited due to API restrictions. If you see "N/A", the tag may be too specific or the API request might have been rate-limited.
""")
