import streamlit as st
from hashlib import sha256
from astrapy import DataAPIClient
import config

# Initialize the client
client = DataAPIClient(config.ASTRA_API_TOKEN)

def connect_db():
    try:
        db = client.get_database_by_api_endpoint(config.ASTRA_API_ENDPOINT)
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
