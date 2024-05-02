from flask import Flask, request, jsonify, render_template_string
import time
from utils import fetch_web_page, extract_information, analyze_text_with_gpt4

app = Flask(__name__)
documents_data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Analysis Interface</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      input, textarea, button { width: 100%; padding: 10px; margin-top: 6px; margin-bottom: 16px; box-sizing: border-box; }
      textarea { height: 150px; }
      button { background-color: #4CAF50; color: white; cursor: pointer; }
      button:hover { background-color: #45a049; }
      #response { white-space: pre-wrap; background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; }
    </style>
    </head>
    <body>
    <h1>Document Analysis Interface</h1>
    <label for="documents">Document URLs:</label>
    <textarea id="documents" name="documents" placeholder="Enter each URL on a new line"></textarea>

    <label for="question">Question:</label>
    <textarea id="question" name="question" placeholder="Enter your question here..."></textarea>

    <button onclick="submitQuestionAndDocuments()">Submit</button>

    <h2>Response:</h2>
    <div id="response"></div>

    <script>
    function submitQuestionAndDocuments() {
      const documents = document.getElementById('documents').value.split(',').map(url => url.trim()).filter(url => url.length);
      const question = document.getElementById('question').value;

      fetch('/submit_question_and_documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question, documents: documents })
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'processing') {
          pollForResults(question);
        } else {
          document.getElementById('response').textContent = 'Failed to process documents.';
        }
      })
      .catch(error => console.error('Error:', error));
    }

    function pollForResults(question) {
      setTimeout(() => {
        fetch(`/get_question_and_facts?question=${encodeURIComponent(question)}`)
        .then(response => response.json())
        .then(data => {
          if (data.status === 'done') {
            document.getElementById('response').textContent = data.facts || 'No facts found.';
          } else if (data.status === 'processing') {
            pollForResults(question);  // Poll again if still processing
          } else {
            document.getElementById('response').textContent = 'Error fetching results.';
          }
        })
        .catch(error => console.error('Polling Error:', error));
      }, 1000);  // Poll every second
    }
    </script>
    </body>
    </html>

    """)

@app.route('/submit_question_and_documents', methods=['POST'])
def submit_question_and_documents():
    data = request.get_json()
    question = data['question']
    documents = data['documents']
    document_text = process_documents(documents)

    if document_text:
        analysis_result = analyze_text_with_gpt4(document_text, question)
        documents_data[question] = {"facts": analysis_result, "status": "processing"}
        return jsonify({"status": "processing", "question": question}), 200
    else:
        return jsonify({"error": "Failed to fetch or extract content", "status": "failed"}), 400


@app.route('/get_question_and_facts', methods=['GET'])
def get_question_and_facts():
    question = request.args.get('question')
    if question in documents_data:
        data = documents_data[question]
        if "facts" in data:
            data['status'] = 'done'
        return jsonify(data), 200
    return jsonify({"error": "Question not found"}), 404

def process_documents(documents):
    combined_text = ""
    for url in documents:
        html_content = fetch_web_page(url)
        if html_content:
            combined_text += extract_information(html_content) + "\n\n"
    return combined_text

if __name__ == '__main__':
    app.run(debug=True)
