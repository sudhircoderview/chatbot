import streamlit as st
from langflow.load import run_flow_from_json

# Define the tweaks if needed
# Define the tweaks if needed
TWEAKS = {
    "ChatInput-QWzsY": {},
    "Prompt-PpkOq": {},
    "ChatOutput-PBoyv": {},
    "TextInput-nqi5V": {},
    "AmazonBedrockModel-0TjIg": {},
    "AstraDB-8Tm07": {},
    "AmazonBedrockEmbeddings-COipt": {},
    "File-JayRh": {},
    "SplitText-2Pcoy": {},
    "ParseData-bv5Hm": {},
    "Memory-NwqCc": {},
    "GoogleGenerativeAIModel-m5Vjz": {}
}

def run_flow(input_value: str):
    """
    Run the flow with the given input value and return the result.
    """
    result = run_flow_from_json(
        flow="RAG_demo.json",
        input_value=input_value,
        fallback_to_env_vars=True,  # Set to True or False based on your needs
        tweaks=TWEAKS
    )
    return result

def extract_ai_response(result):
    """
    Extract the AI response text from the result.
    """
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

# Set up the Streamlit app
st.set_page_config(page_title="Simple Flow Runner")
st.title("Simple Flow Runner")

# Get user input
user_input = st.text_input("Enter your message:", "")

if user_input:
    # Run the flow with user input
    result = run_flow(user_input)
    
    # Extract and display the AI response
    ai_response = extract_ai_response(result)
    st.write("Response from AI:")
    st.markdown(ai_response)
