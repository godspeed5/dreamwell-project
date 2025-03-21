import streamlit as st
import os
import json
import re
from openai import OpenAI

# Configure the chat page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AI Chat Assistant")
st.markdown(
    "Ask your questions about the influencer. For example, try: *what should this influencer do to improve retention?* "
    "or *is he a good fit to sell my product?*"
)

# Function to create a more detailed context from the Instagram data
def create_detailed_context(profile_data):
    # Extract essential profile info
    profile = profile_data.get("data", {})
    
    # Format follower count
    followers = profile.get("usersCount", 0)
    if followers >= 1_000_000:
        followers_formatted = f"{followers/1_000_000:.1f}M"
    elif followers >= 1_000:
        followers_formatted = f"{followers/1_000:.1f}K"
    else:
        followers_formatted = str(followers)
    
    # Get engagement metrics
    avg_likes = profile.get("avgLikes", 0)
    avg_comments = profile.get("avgComments", 0)
    avg_er = profile.get("avgER", 0)
    
    # Calculate engagement rate if not available
    if avg_er == 0 and followers > 0:
        avg_er = (avg_likes + avg_comments) / followers
    
    # Extract top countries and cities
    countries = profile.get("membersCountries", [])
    top_countries = [f"{country.get('name', 'Unknown')}: {country.get('value', 0)*100:.1f}%" 
                    for country in countries[:5] if "name" in country]
    
    cities = profile.get("membersCities", [])
    top_cities = [f"{city.get('name', 'Unknown')}: {city.get('value', 0)*100:.1f}%" 
                 for city in cities[:5] if "name" in city]
    
    # Extract recent posts for content analysis
    recent_posts = [post.get("text", "") for post in profile.get("lastPosts", [])[:3]]
    recent_posts_formatted = "\n\n".join([f"- \"{post}\"" for post in recent_posts if post])
    
    # Build detailed context
    context = f"""
INSTAGRAM PROFILE ANALYSIS:

Basic Information:
- Name: {profile.get('name', 'N/A')}
- Username: @{profile.get('screenName', 'N/A')}
- Followers: {followers_formatted} ({followers} total)
- Description: "{profile.get('description', 'N/A')}"
- Verified: {"Yes" if profile.get('verified', False) else "No"}

Content Categories:
- {', '.join(profile.get('categories', ['N/A']))}

Profile Tags:
- {', '.join(profile.get('tags', ['N/A']))}

Audience Demographics:
- Top Countries: {', '.join(top_countries) if top_countries else 'N/A'}
- Top Cities: {', '.join(top_cities) if top_cities else 'N/A'}
- Gender Split: {"Male-dominated" if profile.get('gender') == 'm' else "Female-dominated" if profile.get('gender') == 'f' else "Mixed"}
- Age Group: {profile.get('age', 'N/A').replace('_', '-')}

Engagement Metrics:
- Average Likes: {avg_likes:,}
- Average Comments: {avg_comments:,}
- Engagement Rate: {avg_er*100:.2f}%
- Fake Followers Percentage: {profile.get('pctFakeFollowers', 0)*100:.1f}%

Recent Content Examples:
{recent_posts_formatted}
"""
    return context

# API Key handling - keeping original implementation
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if not api_key:
    st.sidebar.warning("Please enter your OpenAI API key to use the chat functionality.")
    st.sidebar.info("You can get an API key from [OpenAI's platform](https://platform.openai.com/api-keys).")
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    #### Why do I need to enter an API key?
    This app uses OpenAI's API to generate responses, which requires an API key for authentication.
    Your key is used only for this session and is not stored.
    """)
    # Stop execution if no API key is provided
    st.stop()

# Initialize chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize the OpenAI client with the provided API key
client = OpenAI(api_key=api_key)

# Load Instagram data from file if not in session state
if "detailed_profile_context" not in st.session_state:
    try:
        with open("data/instagram_data.txt", "r") as f:
            content = f.read()
            
            # Extract JSON data
            match = re.search(r"Raw JSON Data:\n(.*?)(\n\n|$)", content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                data = json.loads(json_str)
                
                # Create detailed context
                st.session_state.detailed_profile_context = create_detailed_context(data)
                st.session_state.instagram_data = data
            else:
                st.error("JSON data not found in file.")
                st.session_state.detailed_profile_context = "Error loading Instagram data."
    except Exception as e:
        st.error(f"Error loading Instagram data: {str(e)}")
        st.session_state.detailed_profile_context = "Error loading Instagram data."

# Get profile data - either from session state or from directly loaded file
profile_context = st.session_state.get("detailed_profile_context", "No profile data available.")

# Display profile summary
if "instagram_data" in st.session_state:
    with st.expander("👤 Profile Summary", expanded=False):
        profile = st.session_state.instagram_data.get("data", {})
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if profile.get("image"):
                st.image(profile.get("image"), width=150)
        
        with col2:
            st.subheader(f"{profile.get('name', 'N/A')} (@{profile.get('screenName', 'N/A')})")
            st.write(profile.get("description", ""))
            
            metrics_cols = st.columns(3)
            metrics_cols[0].metric("Followers", f"{profile.get('usersCount', 0):,}")
            metrics_cols[1].metric("Avg. Likes", f"{profile.get('avgLikes', 0):,}")
            metrics_cols[2].metric("Avg. Comments", f"{profile.get('avgComments', 0):,}")

# Function to generate a response using OpenAI's Chat API
def generate_response(question):
    # System prompt to guide the model's behavior
    system_prompt = """
    You are an expert marketing and influencer consultant with deep knowledge of social media analytics.
    Provide thoughtful advice and actionable insights based on the Instagram profile data provided.
    Include specific recommendations tied to the profile's audience demographics, content style, and engagement metrics.
    Support your analysis with data from the profile when relevant.
    Be concise but comprehensive in your answers.
    """
    
    # Prepare the conversation messages with context
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": profile_context},
        {"role": "user", "content": question},
    ]
    
    try:
        # Call the OpenAI ChatCompletion API using the client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Chat interface with a clear visual distinction
st.markdown("### Chat")

# Chat input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("Your question", height=100, 
                             placeholder="e.g., What type of brands would be a good fit for collaboration with this influencer?")
    col1, col2 = st.columns([1, 5])
    with col1:
        submitted = st.form_submit_button("Send", use_container_width=True)
    
    if submitted and user_input:
        # Add user message to chat history
        st.session_state.chat_history.append(("You", user_input))
        
        # Show a spinner while generating the response
        with st.spinner("Thinking..."):
            # Generate and store the agent's response
            answer = generate_response(user_input)
            st.session_state.chat_history.append(("Agent", answer))

# Display the conversation history with better styling
for i, (speaker, message) in enumerate(st.session_state.chat_history):
    if speaker == "You":
        st.markdown(f"<div style='background-color:#F0F2F6; padding:10px; border-radius:5px; margin-bottom:10px;'><b>You:</b> {message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#E1F5FE; padding:10px; border-radius:5px; margin-bottom:10px;'><b>AI Assistant:</b> {message}</div>", unsafe_allow_html=True)

# Add a clear button to reset the conversation
if st.session_state.chat_history:
    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.experimental_rerun()