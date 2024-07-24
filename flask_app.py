from flask import Flask, request, jsonify
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os
import logging

app = Flask("Llama3 server")
logging.basicConfig(level=logging.INFO)

model = None
tokenizer = None

@app.route('/llama3', methods=['POST'])
def generate_response():
    global model, tokenizer
    try:
        data = request.get_json()
        app.logger.info(f"Received request data: {data}")

        if model is None or tokenizer is None:
            model_dir = "/app/Meta-Llama-3-8B"
            if not os.path.exists(model_dir):
                return jsonify({"error": "Model directory does not exist"}), 500

            files = os.listdir(model_dir)
            app.logger.info(f"Files in model directory: {files}")

            tokenizer = AutoTokenizer.from_pretrained(model_dir)
            model = AutoModelForCausalLM.from_pretrained(model_dir)
            app.logger.info("Model and tokenizer loaded successfully")

        if 'prompt' in data and 'max_length' in data:
            prompt = data['prompt']
            max_length = int(data['max_length'])

            text_gen = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                torch_dtype=torch.float16,
                device_map="auto",
            )

            sequences = text_gen(
                prompt,
                do_sample=True,
                top_k=10,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id,
                max_length=max_length,
            )

            response = [seq['generated_text'] for seq in sequences]
            app.logger.info(f"Generated response: {response}")
            return jsonify(response)

        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"Error": str(e)}), 500 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
