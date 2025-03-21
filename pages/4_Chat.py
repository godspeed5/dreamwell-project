import streamlit as st
import os
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

# API Key handling
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

# Get the Instagram profile data from session state
if "instagram_data" in st.session_state:
    data = st.session_state.instagram_data
    profile = data.get("data", {})
    
    # Create a context about the profile
    profile_context = f"""
    Instagram Profile Information:
    - Name: {profile.get('name', 'N/A')}
    - Username: @{profile.get('screenName', 'N/A')}
    - Followers: {profile.get('usersCount', 'N/A')}
    - Description: {profile.get('description', 'N/A')}
    - Tags: {', '.join(profile.get('tags', ['N/A']))}
    """
else:
    profile_context = "No profile data available. Please start from the Home page to load the data."

# Function to generate a response using OpenAI's Chat API
def generate_response(question):
    # System prompt to guide the model's behavior
    system_prompt = (
        "You are an expert marketing and influencer consultant. "
        "Answer questions with thoughtful advice and actionable insights. "
        "Use the provided profile information to make your advice specific and relevant."
    )
    
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
    user_input = st.text_area("Your question", height=100)
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