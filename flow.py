# flow.py

from langflow.load import run_flow_from_json

def run_flow(json_file, input_data, tweaks):
    return run_flow_from_json(json_file, input_data, tweaks)

def extract_ai_response(flow_result):
    try:
        # Assuming the output message is located in a nested dictionary structure
        message_data = flow_result[0].outputs[0].results['message'].data['text']
        return message_data
    except (KeyError, IndexError, TypeError) as e:
        return "Error extracting AI response."
