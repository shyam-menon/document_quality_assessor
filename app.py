import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError
import logging


USE_GPT4 = False  # Set to True to use GPT-4, False for GPT-4o-mini


# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Load .env file and print result
result = load_dotenv(verbose=True)
print(f"Load dotenv result: {result}")

# Print the actual API key being used
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key from environment: {api_key[:8]}...{api_key[-4:]}")

app = Flask(__name__)

# Initialize client as None
client = None

try:
    # Get API key from environment
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Create OpenAI client and validate key
    client = OpenAI(api_key=api_key)
    # Test the connection by making a simple API call
    client.models.list()
    print("Successfully connected to OpenAI API")
    
except (AuthenticationError, ValueError) as e:
    print(f"ERROR: {str(e)}")
    print("Please ensure your OpenAI API key is correctly set in the .env file")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    if client is None:
        return jsonify({"status": "error", "message": "OpenAI client not initialized"}), 500
    return jsonify({"status": "healthy", "message": "OpenAI client connected"}), 200

@app.route('/assess', methods=['POST'])
def assess_document():
    if not client:
        return jsonify({"error": "OpenAI client not initialized due to missing API key"}), 500

    document_content = request.form['document_content']
    prompt = request.form['prompt']
    
    if not prompt:
        prompt = "Please assess the quality of the following document. Provide a detailed analysis of its structure, content, and overall quality."
    
    logging.info(f"Using model: {'gpt-4' if USE_GPT4 else 'gpt-3.5-turbo'}")
    try:
        model = "gpt-4" if USE_GPT4 else "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a document quality assessment expert."},
                {"role": "user", "content": f"{prompt}\n\nDocument content:\n{document_content}"}
            ]
        )
        assessment = response.choices[0].message.content
        return jsonify({"assessment": assessment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5011)