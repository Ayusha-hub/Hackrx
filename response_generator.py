import google.generativeai as genai

# Read your API key from the txt file
with open("apikey.txt", "r") as f:
    api_key = f.read().strip()

# Configure Gemini API with v1 (default)
genai.configure(api_key=api_key)

# Use Gemini Pro (text model)
model = genai.GenerativeModel(model_name="gemini-pro")

def generate_llm_response(prompt):
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

