from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import logging


USE_GPT4 = True  # Set to True to use GPT-4, False for GPT-3.5-turbo
os.environ["OPENAI_API_KEY"] = "[INSERT YOUR OPENAI API KEY HERE]"

load_dotenv()

# Print the API key to check if it's loaded (remove this in production)
print(f"API Key: {os.getenv('OPENAI_API_KEY')}")

app = Flask(__name__)

# Only create the client if the API key is available
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    print("WARNING: OPENAI_API_KEY not found in environment variables")
    client = None

@app.route('/')
def home():
    return render_template('index.html')

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
        model = "gpt-4" if USE_GPT4 else "gpt-3.5-turbo"
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