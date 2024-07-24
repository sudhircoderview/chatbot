import streamlit as st
import requests
import json

API_URL = "http://flask-container:5000/llama3"  # Use container name

st.title("Llama3 Text Generation")

prompt = st.text_area("Enter your prompt:")
max_length = st.number_input("Max length:", min_value=10, max_value=100, value=50)

if st.button("Generate"):
    payload = {
        "prompt": prompt,
        "max_length": max_length
    }
    
    response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        st.success("Generated Text:")
        st.write(result.get('text', 'No response text'))
    else:
        st.error(f"Error: {response.status_code}")
        st.write(response.json())
