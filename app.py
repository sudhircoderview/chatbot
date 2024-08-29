import streamlit as st
import os
from hashlib import sha256
from astrapy import DataAPIClient
from langflow.load import run_flow_from_json

# Initialize the client
client = DataAPIClient("AstraCS:hFwYSGTLbLXpqZhDsdedICSZ:c623d882a54bf24f1e7f51c32089cfb62afd50fee8bf6627670741cadf501146")

# Define TWEAKS for both flows
TWEAKS_FLOW_1 = {
    "ChatInput-SNgYM": {},
    "AstraVectorStoreComponent-vUYys": {},
    "ParseData-qAjdA": {},
    "Prompt-s8ACt": {},
    "ChatOutput-JJYyu": {},
    "AmazonBedrockModel-REYcl": {},
    "AmazonBedrockEmbeddings-PekiE": {}
}

TWEAKS_FLOW_2 = {
    "File-hFef6": {
        "path": "",  # This will be set dynamically based on the uploaded file
        "silent_errors": False
    },
    "SplitText-lSgJr": {
        "chunk_overlap": 200,
        "chunk_size": 1000,
        "separator": "\n"
    },
    "AmazonBedrockEmbeddings-vFt6k": {
        "aws_access_key": "AKIAR6FT4PPU6VG25JSW",
        "aws_secret_key": "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",
        "credentials_profile_name": "",
        "endpoint_url": "",
        "model_id": "amazon.titan-embed-text-v1",
        "region_name": "us-east-1"
    },
    "AstraDB-fkeZ8": {
        "api_endpoint": "https://7e4a4842-8b12-4eb1-9daf-bf45036ab49e-us-east-2.apps.astra.datastax.com",
        "collection_name": "test21",
        "token": "AstraCS:tOOPKUWArDwyUCBoynvHCSgf:5ce4e178c2e3df99e695f3520583d0d1b3dbc345a00c0362e0e69fe85cbcf8af"
    }
}

def run_flow(flow_file: str, input_value: str, tweaks: dict):
    result = run_flow_from_json(
        flow=flow_file,
        input_value=input_value,
        fallback_to_env_vars=True,
        tweaks=tweaks
    )
    return result

def extract_ai_response(result):
    try:
        if isinstance(result, list) and len(result) > 0:
            run_output = result[0]
            if hasattr(run_output, 'outputs') and len(run_output.outputs) > 0:
                result_data = run_output.outputs[0]
                if hasattr(result_data, 'results'):
                    message_data = result_data.results.get('message', {})
                    if hasattr(message_data, 'text'):
                        return message_data.text
                    return 'No text attribute found in message'
        return 'No valid response format'
    except Exception as e:
        return f"Error extracting response: {e}"

# Streamlit App
st.set_page_config(page_title="Flow Runner with User Authentication")

def connect_db():
    try:
        db = client.get_database_by_api_endpoint(
            "https://7e4a4842-8b12-4eb1-9daf-bf45036ab49e-us-east-2.apps.astra.datastax.com"
        )
        return db, True
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None, False

def get_collection(db, collection_name):
    try:
        collection = db.get_collection(collection_name)
        return collection
    except Exception as e:
        st.error(f"Error accessing collection '{collection_name}': {e}")
        return None

def create_user(collection, username, password, email):
    if collection:
        user_data = {"username": username, "password": sha256(password.encode()).hexdigest(), "email": email}
        collection.insert_one(user_data)

def get_user(collection, username, password):
    if collection:
        filter = {"username": username, "password": sha256(password.encode()).hexdigest()}
        return collection.find_one(filter)
    return None

# Login and Registration Logic
def login_page():
    st.header("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        db, connected = connect_db()
        if db:
            collection = get_collection(db, "user_data")
            if collection:
                user = get_user(collection, username, password)
                if user:
                    st.session_state['username'] = username
                    st.session_state['logged_in'] = True
                    st.session_state.page = "Main"
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Could not access 'user_data' collection.")
        else:
            st.error("Could not connect to the database.")

def registration_page():
    st.header("Register")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")
    
    if st.button("Register"):
        if len(username) < 5:
            st.error("Username must be at least 5 characters long.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not email.endswith("gmail.com"):
            st.error("Email must end with 'gmail.com'.")
        else:
            db, connected = connect_db()
            if db:
                collection = get_collection(db, "user_data")
                if collection:
                    create_user(collection, username, password, email)
                    st.success("User registered successfully!")
                    st.session_state.page = "Login"  # Redirect to login page
                else:
                    st.error("Could not access 'user_data' collection.")
            else:
                st.error("Could not connect to the database.")

def main_page():
    st.title("Choose Your Action")
    option = st.selectbox("What would you like to do?", ["Upload File to Vector Store", "Chat with AI"])

    if option == "Upload File to Vector Store":
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
        if uploaded_file is not None:
            # Create a temp folder to store the uploaded file
            temp_dir = "temp_files"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save the file to the temp folder
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Ensure the key exists in TWEAKS_FLOW_2
            if "File-hFef6" in TWEAKS_FLOW_2:
                # Update TWEAKS with the file path
                absolute_path = os.path.abspath(temp_file_path)
                TWEAKS_FLOW_2["File-hFef6"]["path"] = absolute_path
                st.write(f"File '{uploaded_file.name}' uploaded successfully.")
                
                # Run the flow with the uploaded file
                try:
                    result_flow_2 = run_flow("vector_db.json", "message", TWEAKS_FLOW_2)
                    if isinstance(result_flow_2, list) and len(result_flow_2) > 0:
                        st.write("File processed successfully.")
                        st.session_state.flow_redirect = "Chat with AI"  # Set redirection flag
                    else:
                        st.error("No valid response from Flow 2.")
                except ValueError as e:
                    st.error(f"Error running Flow 2: {str(e)}")
            else:
                st.error("Key 'File-hFef6' not found in TWEAKS_FLOW_2.")
    
    elif option == "Chat with AI" or st.session_state.get("flow_redirect", "") == "Chat with AI":
        st.session_state.flow_redirect = ""  # Clear redirection flag
        user_input = st.text_input("Enter your question:")
        if user_input:
            try:
                result_flow_1 = run_flow("Vector_Store_RAG.json", user_input, TWEAKS_FLOW_1)
                ai_response_flow_1 = extract_ai_response(result_flow_1)
                st.write("AI Response from Flow 1:")
                st.markdown(ai_response_flow_1)
            except ValueError as e:
                st.error(f"Error running Flow 1: {str(e)}")

# Page Navigation Selector
def page_selector():
    db, connected = connect_db()
    status_color = "green" if connected else "red"
    st.sidebar.markdown(f'<div style="text-align: right;"><span style="color: {status_color}; font-weight: bold;">Database Connection: {"Connected" if connected else "Disconnected"}</span></div>', unsafe_allow_html=True)

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.sidebar.button("Logout", on_click=logout)
        main_page()
    else:
        page = st.sidebar.selectbox("Select Page", ["Login", "Register"])
        if page == "Login":
            login_page()
        elif page == "Register":
            registration_page()

def logout():
    st.session_state['logged_in'] = False
    st.session_state.page = "Login"

if 'page' not in st.session_state:
    st.session_state.page = "Login"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

page_selector()





