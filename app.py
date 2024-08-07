import streamlit as st
import time
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from PyPDF2 import PdfReader

# Initialize cache
cache = {}

# Load models in advance
models = {
    'LLaMA 2': CTransformers(model='models/llama-2-7b-chat.ggmlv3.q8_0.bin', model_type='llama', config={'max_new_tokens': 256, 'temperature': 0.01}),
    'Mistral': CTransformers(model='models/mistral-7b-instruct-v0.1.Q2_K.gguf', model_type='mistral', config={'max_new_tokens': 256, 'temperature': 0.01}),
}

# Function to read PDF
def read_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

# Function to get response from LLaMA 2 model
def get_response(input_text, no_words, model_choice, pdf_text=None):
    key = (input_text, no_words, model_choice, pdf_text)
    
    if key in cache:
        return cache[key]
    
    llm = models[model_choice]

    # Prompt Template
    template = """
        Write a blog for a topic {input_text} within {no_words} words.
        {pdf_text}
    """
    prompt = PromptTemplate(
        input_variables=["input_text", 'no_words', 'pdf_text'],
        template=template
    )

    formatted_prompt = prompt.format(input_text=input_text, no_words=no_words, pdf_text=pdf_text or "")
    start_time = time.time()
    response = llm.invoke(formatted_prompt)
    end_time = time.time()

    cache[key] = response
    return response, end_time - start_time

# Streamlit app setup
st.set_page_config(page_title="Generate Blogs", page_icon='🤖', layout='wide', initial_sidebar_state='expanded')

st.sidebar.header("Chat History")

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Input fields and file upload
model_choice = st.sidebar.selectbox('Select Model', list(models.keys()))
input_text = st.text_input("Enter the Blog Topic")
pdf_file = st.file_uploader("Upload PDF Document", type=["pdf"])
no_words = st.text_input('No of Words')
submit = st.button("Generate")

# Display chat history
for i, entry in enumerate(st.session_state['history']):
    st.sidebar.write(f"Question: {entry['question']}")
    st.sidebar.write(f"Response Time: {entry['response_time']:.6f} seconds")
    st.sidebar.write(f"Timestamp: {entry['timestamp']}")
    st.sidebar.write("")

# Final response
if submit:
    if pdf_file:
        pdf_text = read_pdf(pdf_file)
    else:
        pdf_text = None
    
    response, response_time = get_response(input_text, no_words, model_choice, pdf_text)
    st.write(response)

    # Add to history
    st.session_state['history'].append({
        'question': input_text,
        'response_time': response_time,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
