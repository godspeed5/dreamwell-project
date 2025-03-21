import streamlit as st
import pandas as pd
import altair as alt

# Configure the page
st.set_page_config(
    page_title="Audience Demographics - Instagram Analytics",
    page_icon="🌎",
    layout="wide"
)

# Check if data is in session state
if "instagram_data" not in st.session_state:
    st.error("Please start from the Home page to load the data.")
    st.stop()

data = st.session_state.instagram_data
profile = data.get("data", {})

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

st.title("Audience Demographics")
st.write("Explore the geographic distribution of your Instagram audience.")

# --- Audience by Country ---
st.header("Top Countries")
countries = profile.get("membersCountries", [])
if countries:
    df_countries = pd.DataFrame(countries)
    # Sort descending by 'value' and pick the top 10
    df_countries = df_countries.sort_values(by="value", ascending=False).head(10)
    df_countries["formatted_value"] = df_countries["value"].apply(format_number)
    
    # Create a more vibrant chart
    chart = alt.Chart(df_countries).mark_bar().encode(
        x=alt.X('value:Q', title='Followers'),
        y=alt.Y('name:N', sort='-x', title='Country'),
        color=alt.Color('value:Q', scale=alt.Scale(scheme='viridis'), legend=None),
        tooltip=['name', 'formatted_value']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No country data available.")

# --- Audience by City ---
st.header("Top Cities")
cities = profile.get("membersCities", [])
if cities:
    df_cities = pd.DataFrame(cities)
    df_cities = df_cities.sort_values(by="value", ascending=False).head(10)
    df_cities["formatted_value"] = df_cities["value"].apply(format_number)
    
    chart = alt.Chart(df_cities).mark_bar().encode(
        x=alt.X('value:Q', title='Followers'),
        y=alt.Y('name:N', sort='-x', title='City'),
        color=alt.Color('value:Q', scale=alt.Scale(scheme='turbo'), legend=None),
        tooltip=['name', 'formatted_value']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No city data available.")