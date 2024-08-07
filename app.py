import streamlit as st
import time
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain_community.cache import InMemoryCache
import diskcache as dc
from PyPDF2 import PdfReader

class LLMCache:
    def __init__(self, model, cache_type='in_memory', cache_dir=None):
        self.llm = model
        
        if cache_type == 'in_memory':
            self.cache = {}
        elif cache_type == 'disk':
            if cache_dir is None:
                raise ValueError("cache_dir must be specified for DiskCache")
            self.cache = dc.Cache(cache_dir)
        else:
            raise ValueError("Unsupported cache_type. Use 'in_memory' or 'disk'")
    
    def get_response(self, prompt):
        # Check cache
        if prompt in self.cache:
            return self.cache[prompt]
        
        # Generate response
        response = self.llm.invoke(prompt)
        
        # Store in cache
        self.cache[prompt] = response
        
        return response

# Initialize models
models = {
    'LLaMA 2': CTransformers(model='models/llama-2-7b-chat.ggmlv3.q8_0.bin', model_type='llama', config={'max_new_tokens': 256, 'temperature': 0.01}),
    'Mistral': CTransformers(model='models/mistral-7b-instruct-v0.1.Q2_K.gguf', model_type='mistral', config={'max_new_tokens': 256, 'temperature': 0.01}),
}

# Initialize caches
llm_caches = {
    'LLaMA 2': LLMCache(models['LLaMA 2'], cache_type='in_memory'),
    'Mistral': LLMCache(models['Mistral'], cache_type='disk', cache_dir='path_to_cache_directory'),
}

# Function to read PDF
def read_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

# Function to get response
def get_response(input_text, no_words, model_choice, pdf_text=None):
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
    response = llm_caches[model_choice].get_response(formatted_prompt)
    end_time = time.time()

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
