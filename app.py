from flask import Flask, request, jsonify, send_from_directory
from bot_logic import DataChatbot
import os

app = Flask(__name__)

# Config paths - assuming csvs are in the parent directory as per user structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
HOLDINGS_FILE = os.path.join(PARENT_DIR, 'holdings.csv')
TRADES_FILE = os.path.join(PARENT_DIR, 'trades.csv')

chatbot = DataChatbot(HOLDINGS_FILE, TRADES_FILE)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400
    
    response = chatbot.process_query(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
