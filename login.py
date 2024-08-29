import streamlit as st
from database import connect_db, get_collection, get_user

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
