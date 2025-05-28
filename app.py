from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
import os
import base64

load_dotenv()
app = Flask(__name__)

# Correct new client usage for v1.82
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['drawing']
        image_data = base64.b64encode(file.read()).decode('utf-8')

        response = client.chat.completions.create(
model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "This is a child's drawing. Can you interpret what emotions or messages the child might be expressing?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                }
            ],
            max_tokens=500
        )

        ai_response = response.choices[0].message.content
        return jsonify({'result': ai_response})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
