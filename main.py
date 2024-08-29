# main.py

import streamlit as st
from login import login_page
from register import registration_page
from flow import run_flow, extract_ai_response
from database import connect_db
import os
import config

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
        "aws_access_key": config.AWS_ACCESS_KEY,
        "aws_secret_key": config.AWS_SECRET_KEY,
        "credentials_profile_name": "",
        "endpoint_url": "",
        "model_id": config.AWS_MODEL_ID,
        "region_name": config.AWS_REGION_NAME
    },
    "AstraDB-fkeZ8": {
        "api_endpoint": config.ASTRA_API_ENDPOINT,
        "collection_name": "test21",
        "token": config.ASTRA_DB_TOKEN
    }
}

def main_page():
    st.title("Choose Your Action")

    # Navigation buttons
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Click to Upload File"):
            st.session_state.page = "Upload"
            st.session_state.previous_page = "Main"  # Track previous page
            st.session_state.updated = True  # Mark as updated

    with col2:
        if st.button("Chat with AI"):
            st.session_state.page = "Chat"
            st.session_state.previous_page = "Main"  # Track previous page
            st.session_state.updated = True  # Mark as updated

def upload_page():
    st.title("Upload File to Vector Store")

    # Return button to go back to the previous page
    if 'previous_page' in st.session_state:
        st.button("Return to Previous Page", on_click=lambda: go_to_page(st.session_state.previous_page))

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

    if uploaded_file is not None:
        temp_dir = config.TEMP_FILES_DIR
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if "File-hFef6" in TWEAKS_FLOW_2:
            absolute_path = os.path.abspath(temp_file_path)
            TWEAKS_FLOW_2["File-hFef6"]["path"] = absolute_path
            st.write(f"File '{uploaded_file.name}' uploaded successfully.")
            
            try:
                result_flow_2 = run_flow(config.VECTOR_DB_FLOW_FILE, "message", TWEAKS_FLOW_2)
                if isinstance(result_flow_2, list) and len(result_flow_2) > 0:
                    st.write("File processed successfully.")
                    st.session_state.file_uploaded = True  # Set state to indicate file upload success
                else:
                    st.error("No valid response from Flow 2.")
            except ValueError as e:
                st.error(f"Error running Flow 2: {str(e)}")
        else:
            st.error("Key 'File-hFef6' not found in TWEAKS_FLOW_2.")

    # Chat input field for upload page (only visible after successful upload)
    if st.session_state.get('file_uploaded', False):
        st.write("Chat with AI after file upload:")
        user_input = st.text_input("Enter your question:")
        if user_input:
            try:
                result_flow_1 = run_flow(config.CHAT_FLOW_FILE, user_input, TWEAKS_FLOW_1)
                ai_response_flow_1 = extract_ai_response(result_flow_1)
                st.write("AI Response from Flow 1:")
                st.markdown(ai_response_flow_1)
            except ValueError as e:
                st.error(f"Error running Flow 1: {str(e)}")

def chat_page():
    st.title("Chat with AI")

    # Return button to go back to the previous page
    if 'previous_page' in st.session_state:
        st.button("Return to Previous Page", on_click=lambda: go_to_page(st.session_state.previous_page))

    user_input = st.text_input("Enter your question:")
    if user_input:
        try:
            result_flow_1 = run_flow(config.CHAT_FLOW_FILE, user_input, TWEAKS_FLOW_1)
            ai_response_flow_1 = extract_ai_response(result_flow_1)
            st.write("AI Response from Flow 1:")
            st.markdown(ai_response_flow_1)
        except ValueError as e:
            st.error(f"Error running Flow 1: {str(e)}")

def go_to_page(page_name):
    st.session_state.page = page_name
    st.session_state.updated = True

def page_selector():
    db, connected = connect_db()
    status_color = "green" if connected else "red"
    st.sidebar.markdown(f'<div style="text-align: right;"><span style="color: {status_color}; font-weight: bold;">Database Connection: {"Connected" if connected else "Disconnected"}</span></div>', unsafe_allow_html=True)

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.sidebar.button("Logout", on_click=logout)

        if 'page' not in st.session_state:
            st.session_state.page = "Main"

        if st.session_state.page == "Upload":
            upload_page()
        elif st.session_state.page == "Chat":
            chat_page()
        else:
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
    st.session_state.previous_page = None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'updated' not in st.session_state:
    st.session_state.updated = False

page_selector()

