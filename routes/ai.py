import openai
from flask import Blueprint, request, jsonify
import os

ai_bp = Blueprint('ai', __name__)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Set this in your environment variables

@ai_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    language = data.get('language', 'en')
    system_prompt = (
        "You are a helpful, friendly AI assistant for the Barangay Management System. "
        "Guide users on registration, login, document requests, blotter filing, and other features. "
        "Answer in English or Tagalog as needed. If the user asks about a feature, explain how to use it or where to find it in the system."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=300,
        temperature=0.5,
    )
    reply = response['choices'][0]['message']['content']
    return jsonify({'reply': reply}) 