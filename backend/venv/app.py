from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import logging
import os

app = Flask(__name__)
CORS(app, origins="*")

logging.basicConfig(level=logging.DEBUG)

model = "codellama:7b"

def load_few_shot_examples():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "few_shot_examples.txt")
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        logging.error("Error: few_shot_examples.txt not found. Please ensure the file exists in the same directory.")
        return "Error: Few-shot examples are not available. Please ensure the file is present."

FEW_SHOT_PROMPT = load_few_shot_examples()

@app.route('/api/analyze_code', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json()
        code = data.get('code', '')

        if not code:
            return jsonify({"error": "No code provided"}), 400

        prompt = (
            f"{FEW_SHOT_PROMPT}\n" \
            "The examples above are for reference only and do not require any analysis or corrections. \n\n" \
            "You are a computer science teacher. Your task is to analyze the provided code for mistakes. Under no circumstances should you explain or rewrite the given code, provide corrected code, or suggest fixes. \n\n" \
            "Your sole focus should be:\n" \
            "- Identifying and explaining the issues in the code.\n" \
            "- Highlighting syntax errors, logical errors, and areas for improvement.\n" \
            "- Clearly stating the **exact line number(s)** where each issue exists.\n\n" \
            "**Important Instructions:**\n" \
            "- DO NOT generate or provide any code corrections, rewritten code, or solutions under any circumstances.\n" \
            "- Always reference specific line numbers for each error or problem.\n" \
            "- Use a friendly and clear tone to explain the issues and suggest ways to resolve them.\n\n" \
            f"Code:\n```\n{code}\n```\n\n" \
            "**Final Reminder:** DO NOT generate any code corrections or solutions under any circumstances. Always include line numbers when describing the issues."
        )

        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        logging.debug(f"Model response: {response}")

        message_content = response.get('message', {}).get('content', "No content available")

        return jsonify({"response": message_content}), 200

    except Exception as e:
        logging.error(f"Error during code analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
