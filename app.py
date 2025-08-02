from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
import docx

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

uploaded_doc_text = ""

def extract_text(file, filename):
    if filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()

    else:  # txt
        return file.read().decode('utf-8', errors='ignore')

@app.route("/upload", methods=["POST"])
def upload_document():
    global uploaded_doc_text
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No document uploaded"}), 400

        file = request.files['document']
        uploaded_doc_text = extract_text(file, file.filename)

        if not uploaded_doc_text:
            return jsonify({"error": "Could not extract text from file"}), 400

        prompt = f"Summarize the following document in 3-4 lines:\n\n{uploaded_doc_text}"
        response = model.generate_content(prompt)
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        query_text = data.get("query", "")

        if not uploaded_doc_text:
            return jsonify({"error": "No document uploaded yet"}), 400
        if not query_text:
            return jsonify({"error": "No query provided"}), 400

        prompt = f"""
You have read the following document:

{uploaded_doc_text}

Now answer the following question in 2-3 lines:
{query_text}
"""
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
