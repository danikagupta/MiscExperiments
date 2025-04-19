# streamlit_app.py
# Copyright 2024 Jahangir Iqbal

import os
import json
import PyPDF2
import random
import streamlit as st
from src.graph import salesCompAgent
from src.google_firestore_integration import get_all_prompts
from google.oauth2 import service_account
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from datetime import datetime

# Set environment variables for Langchain and SendGrid
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="SalesCompAgent"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

DEBUGGING=0

def apply_cl3vr_styling():
    st.markdown("""
    <style>
        /* Base styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        .cl3vr-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background-color: white;
            border-bottom: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .cl3vr-logo-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .cl3vr-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            background-color: #2563eb;
            color: white;
            border-radius: 9999px;
            font-size: 1.25rem;
        }
        
        .cl3vr-logo-text {
            font-weight: 700;
            font-size: 1.25rem;
            color: #111827;
        }
        
        .cl3vr-header-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .cl3vr-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.5rem 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .cl3vr-button-outline {
            border: 1px solid #e5e7eb;
            background-color: white;
            color: #111827;
        }
        
        .cl3vr-button-outline:hover {
            background-color: #f9fafb;
        }
        
        /* Welcome section */
        .cl3vr-welcome {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 50vh;
            padding: 2rem 1rem;
        }
        
        .cl3vr-welcome-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 5rem;
            height: 5rem;
            background-color: #2563eb;
            color: white;
            border-radius: 9999px;
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
        }
        
        .cl3vr-welcome-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 1rem;
        }
        
        .cl3vr-welcome-subtitle {
            font-size: 1.25rem;
            color: #4b5563;
            margin-bottom: 1rem;
        }
        
        .cl3vr-welcome-description {
            font-size: 1rem;
            color: #6b7280;
            max-width: 36rem;
            margin: 0 auto;
        }
        
        /* Chat messages */
        .cl3vr-message-container {
            display: flex;
            margin-bottom: 0.75rem;
        }
        
        .cl3vr-message {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            display: flex;
            gap: 0.75rem;
        }
        
        .cl3vr-user-message {
            background-color: #2563eb;
            color: white;
            margin-left: auto;
        }
        
        .cl3vr-assistant-message {
            background-color: white;
            color: #111827;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        
        .cl3vr-avatar {
            width: 2rem;
            height: 2rem;
            border-radius: 9999px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .cl3vr-user-avatar {
            background-color: #3b82f6;
            color: white;
        }
        
        .cl3vr-assistant-avatar {
            background-color: #f3f4f6;
            color: #2563eb;
        }
        
        .cl3vr-message-content {
            flex: 1;
        }
        
        .cl3vr-message-sender {
            font-weight: 500;
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
        }
        
        .cl3vr-message-text {
            font-size: 0.875rem;
        }
        
        /* Loading dots */
        .cl3vr-loading-dots {
            display: flex;
            gap: 0.375rem;
        }
        
        .cl3vr-dot {
            width: 0.5rem;
            height: 0.5rem;
            background-color: #6b7280;
            border-radius: 9999px;
            opacity: 0.75;
        }
        
        @keyframes blink {
            0%, 100% {
                opacity: 0.2;
            }
            50% {
                opacity: 1;
            }
        }
        
        .cl3vr-dot-1 {
            animation: blink 1.4s infinite 0s;
        }
        
        .cl3vr-dot-2 {
            animation: blink 1.4s infinite 0.2s;
        }
        
        .cl3vr-dot-3 {
            animation: blink 1.4s infinite 0.4s;
        }
        
        /* File attachment */
        .cl3vr-file-attachment {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background-color: white;
            padding: 0.5rem;
            border-radius: 0.375rem;
            border: 1px solid #e5e7eb;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        
        .cl3vr-file-name {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .cl3vr-file-size {
            font-size: 0.75rem;
            color: #6b7280;
        }
        
        /* Footer */
        .cl3vr-footer {
            text-align: center;
            padding: 1rem;
            background-color: white;
            border-top: 1px solid #e5e7eb;
            font-size: 0.75rem;
            color: #6b7280;
            margin: 1rem -1rem -1rem -1rem;
        }
        
        /* Streamlit customizations */
        .stTextInput > div > div > input {
            border-radius: 0.375rem;
            border: 1px solid #e5e7eb;
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
        }
        
        .stButton > button {
            border-radius: 0.375rem;
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Container styling */
        .cl3vr-container {
            display: flex;
            flex-direction: column;
            min-height: calc(100vh - 2rem);
            margin: -1rem;
            padding: 1rem;
        }
        
        .cl3vr-main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .cl3vr-chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem 0;
        }
        
        .cl3vr-input-container {
            margin-top: auto;
            padding: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Call this at the beginning of your app
#apply_cl3vr_styling()

def render_cl3vr_header():
    """Render the cl3vr header with logo and buttons"""
    st.markdown("""
    <div class="cl3vr-header">
        <div class="cl3vr-logo-container">
            <div class="cl3vr-logo">🤖</div>
            <div class="cl3vr-logo-text">cl3vr</div>
        </div>
        <div class="cl3vr-header-buttons">
            <button class="cl3vr-button cl3vr-button-outline" onclick="openEnterpriseForm()">
                <span>🏢</span>
                <span>Enterprise</span>
            </button>
            <button class="cl3vr-button cl3vr-button-outline" onclick="openLoginForm()">
                <span>👤</span>
                <span>Log in</span>
            </button>
        </div>
    </div>
    
    <script>
        function openEnterpriseForm() {
            // You can replace this with your own logic
            const event = new CustomEvent('openEnterpriseForm');
            window.dispatchEvent(event);
        }
        
        function openLoginForm() {
            // You can replace this with your own logic
            const event = new CustomEvent('openLoginForm');
            window.dispatchEvent(event);
        }
    </script>
    """, unsafe_allow_html=True)

def render_cl3vr_welcome():
    """Render the welcome section for first-time visitors"""
    st.markdown("""
    <div class="cl3vr-welcome">
        <div class="cl3vr-welcome-logo">🤖</div>
        <h1 class="cl3vr-welcome-title">Meet cl3vr</h1>
        <p class="cl3vr-welcome-subtitle">Your AI assistant for Sales Compensation</p>
        <p class="cl3vr-welcome-description">
            Get instant answers to your sales compensation questions, analyze data, and streamline your compensation
            workflows with AI-powered assistance.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_cl3vr_message(content, role="assistant", attachment=None):
    """Render a chat message in the cl3vr style
    
    Args:
        content (str): The message content
        role (str): Either "assistant" or "user"
        attachment (dict, optional): File attachment info with keys: name, size
    """
    if role == "user":
        avatar = "👤"
        message_class = "cl3vr-user-message"
        avatar_class = "cl3vr-user-avatar"
        sender = "You"
    else:
        avatar = "🤖"
        message_class = "cl3vr-assistant-message"
        avatar_class = "cl3vr-assistant-avatar"
        sender = "cl3vr"
    
    attachment_html = ""
    if attachment:
        attachment_html = f"""
        <div class="cl3vr-file-attachment" style="background-color: {'#3b82f6' if role == 'user' else '#f3f4f6'}; color: {'white' if role == 'user' else 'inherit'};">
            📎 <span class="cl3vr-file-name">{attachment['name']}</span>
            <span class="cl3vr-file-size">({attachment['size']} KB)</span>
        </div>
        """
    
    st.markdown(f"""
    <div class="cl3vr-message-container">
        <div class="cl3vr-message {message_class}">
            <div class="cl3vr-avatar {avatar_class}">{avatar}</div>
            <div class="cl3vr-message-content">
                <div class="cl3vr-message-sender">{sender}</div>
                <div class="cl3vr-message-text">{content}</div>
                {attachment_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_cl3vr_loading():
    """Render the loading indicator with blinking dots"""
    st.markdown("""
    <div class="cl3vr-message-container">
        <div class="cl3vr-message cl3vr-assistant-message">
            <div class="cl3vr-avatar cl3vr-assistant-avatar">🤖</div>
            <div class="cl3vr-message-content">
                <div class="cl3vr-message-sender">cl3vr</div>
                <div class="cl3vr-loading-dots">
                    <div class="cl3vr-dot cl3vr-dot-1"></div>
                    <div class="cl3vr-dot cl3vr-dot-2"></div>
                    <div class="cl3vr-dot cl3vr-dot-3"></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_cl3vr_footer():
    """Render the footer with copyright information"""
    current_year = datetime.now().year
    st.markdown(f"""
    <div class="cl3vr-footer">
        © {current_year} cl3vr AI. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

def render_cl3vr_file_preview(file_name, file_size):
    """Render a preview of an uploaded file
    
    Args:
        file_name (str): Name of the uploaded file
        file_size (int): Size of the file in KB
    """
    st.markdown(f"""
    <div class="cl3vr-file-attachment">
        📎 <span class="cl3vr-file-name">{file_name}</span>
        <span class="cl3vr-file-size">({file_size} KB)</span>
        <button onclick="removeFile()" style="background: none; border: none; cursor: pointer; font-size: 0.875rem;">❌</button>
    </div>
    """+"""
    <script>
        function removeFile() {
            const event = new CustomEvent('removeFile');
            window.dispatchEvent(event);
        }
    </script>
    """, unsafe_allow_html=True)

def get_google_cloud_credentials():
    """
    Gets and sets up Google Cloud credentials for authentication.
    This function:
    1. Retrieves the Google service account key from Streamlit secrets
    2. Converts the JSON string to a Python dictionary
    3. Creates a credentials object that can be used to authenticate with Google services
    
    Returns:
        service_account.Credentials: Google Cloud credentials object
    """
    # Get Google Cloud credentials from Streamlit secrets
    js1 = st.secrets["GOOGLE_KEY"]
    #print(" A-plus Google credentials JS: ", js1)
    credentials_dict=json.loads(js1)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)   
    st.session_state.credentials = credentials
    return credentials

def initialize_prompts():
    """
    Initializes the application by setting up Google credentials and loading prompts.
    This function:
    1. Checks if credentials exist in the session state, if not gets new credentials
    2. Checks if prompts exist in the session state, if not fetches them from Firestore
    3. Stores both credentials and prompts in Streamlit's session state for later use
    """
    if "credentials" not in st.session_state:
        st.session_state.credentials = get_google_cloud_credentials()
    if "prompts" not in st.session_state:
        prompts = get_all_prompts(st.session_state.credentials)
        st.session_state.prompts = prompts

# Add custom CSS to change the font to Inter
def set_custom_font():
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def process_file(upload_file):
    #st.sidebar.image(upload_file)
    #return
    #PDF=application/pdf
    #CSV=text/csv
    with st.sidebar.expander("File contents"):
        st.write("file type:", upload_file.type)
    filetype = upload_file.type
    if filetype == 'application/pdf':

        pdfReader = PyPDF2.PdfReader(upload_file)
        count = len(pdfReader.pages)
        text=""
        for i in range(count):
            page = pdfReader.pages[i]
            text=text+page.extract_text()

        with st.sidebar.expander("File contents"):
            st.write("file type:", upload_file.type)
            st.write(text)
        return text, "pdf"

    elif filetype == 'text/csv':
        print("got a cvs file")
        file_contents = upload_file.read()
        return file_contents, "csv"
    else:
        st.sidebar.write('unknown file type', filetype)

def start_chat(container=st):
    """
    Sets up and manages the main chat interface for the Sales Comp Agent application.
    
    This function:
    1. Creates the UI elements (title, welcome message)
    2. Manages chat history using Streamlit's session state
    3. Maintains conversation threading with unique thread IDs
    4. Handles message display for both user and assistant
    5. Processes user input and generates AI responses using salesCompAgent in graph.py
    6. Handles message escaping for special characters
    7. Manages debugging output when DEBUGGING flag is enabled
    
    The function runs in a continuous loop as part of the Streamlit app, waiting for 
    and responding to user input in real-time.
    """
    # Setup a simple landing page with title and avatars
    container.title('Meet cl3vr')
    st.markdown("#### Your AI assistant for Sales Compensation")
    avatars={"system":"💻🧠", "user":"🧑‍💼", "assistant":"🌀"} 
    
    # Keeping context of conversations, checks if there is anything in messages array
    # If not, it creates an empty list where all messages will be saved
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Ensuring a unique thread-id is maintained for every conversation
    if "thread-id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 9999)
    thread_id = st.session_state.thread_id

    # Display previous messages in the chat history by keeping track of the messages array
    # in the session state. 
    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar=avatars[message["role"]]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"]) 

    # Handle new user input. Note: walrus operator serves two functions, it checks if
    # the user entered any input. If yes, it returns that value and assigns to 'prompt'. Note that escaped_prompt was
    # used for formatting purposes.
    if prompt := st.chat_input("Ask me anything related to sales comp..", accept_file=True, file_type=["pdf", "md", "doc", "csv"]):
        if prompt and prompt["files"]:
            uploaded_file=prompt["files"][0]
            
            file_contents, filetype = process_file(uploaded_file)
            if filetype != 'csv':
                prompt.text = prompt.text + f"\n Here are the file contents: {file_contents}"
        
        escaped_prompt = prompt.text.replace("$", "\\$")
        st.session_state.messages.append({"role": "user", "content": escaped_prompt})
        with st.chat_message("user", avatar=avatars["user"]):
            st.write(escaped_prompt)
        message_history = []
        
        msgs = st.session_state.messages
    
    # Iterate through chat history, and based on the role (user or assistant) tag it as HumanMessage or AIMessage
        for m in msgs:
            if m["role"] == "user":
                # Add user messages as HumanMessage
                message_history.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                # Add assistant messages as AIMessage
                message_history.append(AIMessage(content=m["content"]))
        
        # Initialize salesCompAgent in graph.py 
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        parameters = {'initialMessage': prompt.text, 'sessionState': st.session_state, 
                        'sessionHistory': st.session_state.messages, 
                        'message_history': message_history}
        if 'csv_data' in st.session_state:
            parameters['csv_data'] = st.session_state['csv_data']
        if prompt['files'] and filetype == 'csv':
            parameters['csv_data'] = file_contents
            st.session_state['csv_data'] = file_contents
        # Stream responses from the instance of salesCompAgent which is called "app"
        for s in app.graph.stream(parameters, thread):
    
            if DEBUGGING:
                print(f"GRAPH RUN: {s}")
                st.write(s)
            for k,v in s.items():
                if DEBUGGING:
                    print(f"Key: {k}, Value: {v}")
            if resp := v.get("responseToUser"):
                with st.chat_message("assistant", avatar=avatars["assistant"]):
                    st.write(resp) 
                st.session_state.messages.append({"role": "assistant", "content": resp})

# Enterprise Inquiry Form
def show_enterprise_form():
    with st.form("enterprise_inquiry"):
        st.markdown("### Enterprise Inquiry")
        st.markdown("Interested in an enterprise solution? Fill out the form below and our team will contact you to schedule a follow-up meeting.")
        
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        company = st.text_input("Company Name")
        
        submitted = st.form_submit_button("Request Follow-up")
        
        if submitted:
            if not name or not email or not company:
                st.error("Please fill out all fields")
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
            else:
                # Process the form (integrate with your existing logic)
                st.success("Thank you! Your inquiry has been received. A member of the cl3vr team will contact you shortly.")
                return True
    return False

# Login Form
def show_login_form():
    st.markdown("### Log in to cl3vr")
    st.markdown("Sign in to save your conversations and access them across devices.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Continue with Google", key="google_login"):
            # Integrate with your existing authentication
            st.session_state.logged_in = True
            st.session_state.username = "User_123"
            return True
    
    with col2:
        if st.button("Continue with Apple", key="apple_login"):
            # Integrate with your existing authentication
            st.session_state.logged_in = True
            st.session_state.username = "User_456"
            return True
    
    st.markdown("By continuing, you agree to our Terms of Service and Privacy Policy.")
    return False

#if __name__ == '__main__':
    #initialize_prompts()
    #set_custom_font()
    #start_chat()

# This is the main section

import streamlit as st
from datetime import datetime
import time



# Set page config
st.set_page_config(
    page_title="cl3vr - Sales Compensation Assistant",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="auto", # Added for completeness, adjust as needed
    #theme="light" # Explicitly set the theme to light
)

# Apply the cl3vr styling
apply_cl3vr_styling()

# Initialize session state for your app
if 'messages' not in st.session_state:
    # Initialize with a default welcome message from the assistant
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! How can I help you with sales compensation today?"}
    ]
if 'has_interacted' not in st.session_state:
    # Start with has_interacted as True if you want the chat visible immediately
    st.session_state.has_interacted = True # Changed to True
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = None
if 'uploaded_file_type' not in st.session_state:
    st.session_state.uploaded_file_type = None
# Ensure thread_id for Langchain agent state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"cl3vr-thread-{random.randint(1000, 9999)}"

# Initialize prompts and credentials if not already done
# You might want to move this near the top if needed earlier
if "credentials" not in st.session_state:
    st.session_state.credentials = get_google_cloud_credentials()
# if "prompts" not in st.session_state: # Assuming prompts are not needed for this flow yet
#     prompts = get_all_prompts(st.session_state.credentials)
#     st.session_state.prompts = prompts

# Render the cl3vr header
render_cl3vr_header()

# Main container
st.markdown('<div class="cl3vr-container">', unsafe_allow_html=True)
st.markdown('<div class="cl3vr-main">', unsafe_allow_html=True)

# Welcome section or chat messages
# Removed the welcome section logic as has_interacted is now True by default
# if not st.session_state.has_interacted:
render_cl3vr_welcome()
# else:

# Always render the chat container now
st.markdown('<div class="cl3vr-chat-container" id="chat-container">', unsafe_allow_html=True)

# Display all messages using the custom renderer
for message in st.session_state.messages:
    render_cl3vr_message(
        content=message['content'],
        role=message['role'],
        attachment=message.get('attachment')
    )

# Placeholder for the loading indicator
loading_placeholder = st.empty()

st.markdown('</div>', unsafe_allow_html=True)


# Input area
st.markdown('<div class="cl3vr-input-container">', unsafe_allow_html=True)

# File upload handling
uploaded_file = st.file_uploader(
    "Upload a file",
    type=["pdf", "csv", "txt"], # Adjusted types based on process_file
    label_visibility="collapsed",
    key="file_uploader" # Added a key for better state management
)

# Process and store file content when a new file is uploaded
if uploaded_file and uploaded_file != st.session_state.get('uploaded_file_instance'):
    st.session_state.uploaded_file_instance = uploaded_file # Store the instance for comparison
    st.session_state.uploaded_file = {
        "name": uploaded_file.name,
        "size": round(uploaded_file.size / 1024)
    }
    # Process the file immediately and store its content
    # Use a copy of the file object for processing if needed multiple times
    file_content, file_type = process_file(uploaded_file)
    st.session_state.uploaded_file_content = file_content
    st.session_state.uploaded_file_type = file_type
    # Display file preview right after upload
    render_cl3vr_file_preview(st.session_state.uploaded_file["name"], st.session_state.uploaded_file["size"])
    # Rerun to show the preview immediately and clear the uploader state visually
    # st.rerun() # Optional: uncomment if preview doesn't show instantly

# Display file preview if a file exists in session state but hasn't been processed by send button yet
elif st.session_state.uploaded_file and not uploaded_file:
     render_cl3vr_file_preview(st.session_state.uploaded_file["name"], st.session_state.uploaded_file["size"])


# Input form using columns
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Ask me anything related to sales compensation...",
        label_visibility="collapsed",
        key="user_text_input" # Added key
    )

with col2:
    send_button = st.button("Send", key="send_button") # Added key

# Process input when the send button is clicked
if send_button and (user_input.strip() or st.session_state.uploaded_file):
    st.session_state.has_interacted = True # Ensure interaction flag is set

    # --- Prepare User Message ---
    user_message_content = user_input.strip()
    user_message = {
        "role": "user",
        "content": user_message_content,
        "attachment": None # Initialize attachment as None
    }

    # Add file info to the message and potentially content to the prompt text
    if st.session_state.uploaded_file:
        user_message["attachment"] = st.session_state.uploaded_file

        # Append non-CSV file content directly to the user's text query
        if st.session_state.uploaded_file_type != 'csv' and st.session_state.uploaded_file_content:
             user_message_content += f"\n\n--- Attached File ({st.session_state.uploaded_file['name']}) Content ---\n{st.session_state.uploaded_file_content}"
             user_message["content"] = user_message_content # Update message content

    # Add user message to chat history
    st.session_state.messages.append(user_message)

    # --- Display User Message ---
    # Rerender the whole chat history including the new user message
    # This replaces the previous loop and clears the loading placeholder
    st.markdown('<div class="cl3vr-chat-container" id="chat-container-rerender">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        render_cl3vr_message(
            content=message['content'],
            role=message['role'],
            attachment=message.get('attachment')
        )
    st.markdown('</div>', unsafe_allow_html=True)


    # --- Show Loading Indicator ---
    with loading_placeholder.container():
         render_cl3vr_loading()

    # --- Prepare for AI Call ---
    message_history = []
    for m in st.session_state.messages:
        if m["role"] == "user":
            message_history.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            message_history.append(AIMessage(content=m["content"]))

    # Prepare parameters for the agent
    thread_id = st.session_state.thread_id
    thread = {"configurable": {"thread_id": thread_id}}
    parameters = {
        'initialMessage': user_message_content, # Use the potentially modified content
        'sessionState': st.session_state,
        'sessionHistory': st.session_state.messages, # Pass the raw history too if needed
        'message_history': message_history # Pass Langchain formatted history
    }

    # Add CSV data if it exists and is the relevant type
    if st.session_state.uploaded_file_type == 'csv' and st.session_state.uploaded_file_content:
        parameters['csv_data'] = st.session_state.uploaded_file_content
        # Optionally keep it in session state if needed across turns without re-upload
        # st.session_state['csv_data'] = st.session_state.uploaded_file_content

    # --- Call AI Agent ---
    app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
    ai_response_content = ""
    try:
        # Stream responses from the agent
        for s in app.graph.stream(parameters, thread):
            if DEBUGGING:
                print(f"GRAPH RUN: {s}")
                # st.write(s) # Avoid writing debug directly to main UI if possible
            for k, v in s.items():
                if DEBUGGING:
                    print(f"Key: {k}, Value: {v}")
                if resp := v.get("responseToUser"):
                    ai_response_content += resp # Accumulate response parts if streamed

        # If no response was extracted, provide a default
        if not ai_response_content:
             ai_response_content = "Sorry, I couldn't process that request."

    except Exception as e:
        ai_response_content = f"An error occurred: {e}"
        print(f"Error during agent execution: {e}") # Log the error

    # --- Process AI Response ---
    ai_response = {
        "role": "assistant",
        "content": ai_response_content
    }
    st.session_state.messages.append(ai_response)

    # --- Clear Inputs and File State ---
    # Reset file state after processing
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_type = None
    st.session_state.uploaded_file_instance = None # Reset instance too

    # Clear the text input - This requires JavaScript or a rerun
    # Using st.rerun() is the simplest way in Streamlit to clear input fields
    # after submission and display the final AI response.

    # --- Clear Loading and Rerun ---
    loading_placeholder.empty()
    st.rerun() # Rerun to display the AI message and clear the input box


# --- JavaScript for Button Clicks (Enterprise/Login) ---
# This part needs careful integration. Streamlit doesn't directly support
# onclick JS triggering Python functions easily.
# A common workaround is using session state flags toggled by buttons,
# which you seem to be doing later in the code. Let's keep that pattern.

# Add this to your main app logic
if 'show_enterprise_form' not in st.session_state:
    st.session_state.show_enterprise_form = False
if 'show_login_form' not in st.session_state:
    st.session_state.show_login_form = False

# --- Modal Logic (using flags set by JS or sidebar buttons) ---
# These forms will appear *outside* the main chat flow if triggered.
# Consider using st.dialog for a modal experience if desired.

if st.session_state.show_enterprise_form:
    # Using st.dialog for a modal popup
    with st.dialog("Enterprise Inquiry"):
        if show_enterprise_form(): # Your existing form function
            st.session_state.show_enterprise_form = False
            st.rerun()
        # Add a close button if the form submission doesn't close it
        if st.button("Close", key="close_enterprise_dialog"):
             st.session_state.show_enterprise_form = False
             st.rerun()


if st.session_state.show_login_form:
     # Using st.dialog for a modal popup
    with st.dialog("Log In"):
        if show_login_form(): # Your existing form function
            st.session_state.show_login_form = False
            st.rerun()
        # Add a close button
        if st.button("Close", key="close_login_dialog"):
             st.session_state.show_login_form = False
             st.rerun()


# --- Sidebar Buttons to Trigger Modals ---
# These buttons provide an alternative way to open the forms
with st.sidebar:
    st.markdown("---") # Separator
    if st.button("🏢 Enterprise Inquiry", key="sidebar_enterprise_button"):
        st.session_state.show_enterprise_form = True
        # Clear other form flag if necessary
        st.session_state.show_login_form = False
        st.rerun()

    if st.button("👤 Log In / Sign Up", key="sidebar_login_button"):
        st.session_state.show_login_form = True
        # Clear other form flag if necessary
        st.session_state.show_enterprise_form = False
        st.rerun()

# --- Footer ---
st.markdown('</div>', unsafe_allow_html=True) # Close cl3vr-input-container
st.markdown('</div>', unsafe_allow_html=True) # Close cl3vr-main

render_cl3vr_footer()
st.markdown('</div>', unsafe_allow_html=True) # Close cl3vr-container


# --- JavaScript Injection for Header Buttons ---
# This uses streamlit-js-eval or similar techniques to bridge JS clicks to Python state changes.
# It's more complex than sidebar buttons. Let's stick to sidebar buttons for now
# unless you specifically need the header buttons to work. The HTML/JS for the header
# buttons currently doesn't have a mechanism to trigger Streamlit state changes.

# --- Remove Old/Unused Code ---
# Comment out or remove the old start_chat function and its call if it's fully replaced.
# def start_chat(container=st):
#    ... (old function) ...

# if __name__ == '__main__':
    #initialize_prompts() # Called earlier now
    #set_custom_font() # Called by apply_cl3vr_styling
    #start_chat() # Replaced by the main script logic
