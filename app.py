from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

# Health Check
@app.route("/")
def home():
    return "LLM Insurance Policy API is running"

# Document Upload + Query Route
@app.route("/upload", methods=["POST"])
def upload_and_query():
    try:
        # ✅ Step 1: Get document file
        if 'document' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['document']
        text = file.read().decode('utf-8')

        # ✅ Step 2: Get user query
        query_text = request.form.get('query', '')
        if not query_text:
            return jsonify({"error": "No query provided"}), 400

        # ✅ Step 3: Generate Gemini response
        prompt = f"""
You are an insurance assistant. 
Below is a health insurance policy document:

{text}

Now answer the following user question briefly and clearly:
"{query_text}"
"""

        response = model.generate_content(prompt)
        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
