import streamlit as st
from database import connect_db, get_collection, create_user

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
