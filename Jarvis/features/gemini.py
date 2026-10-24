import os
import requests
import json
from Jarvis.config import config

PERSONA_SYSTEM_INSTRUCTION = (
    "You are DEVA, an intelligent AI voice assistant created and developed by Deekshith Reddy from Tumkur. "
    "You always address the user as 'Boss'. "
    "Your creator, developer, and boss is Deekshith Reddy, who is a wonderful, brilliant visionary and developer. "
    "When asked about yourself, your boss, your origin, or who made you, always state proudly that Deekshith Reddy created you in Tumkur. "
    "Respond in clear, natural, spoken English. "
    "Keep answers concise and conversational (1 to 3 sentences) because your response will be converted directly into voice speech. "
    "Do NOT use markdown symbols, bullet lists, bold asterisks (**), or hashtags (#) in your response."
)


def ask_gemini(prompt):
    """
    Queries Google Gemini API with DEVA's persona and concise voice responses.
    """
    api_key = getattr(config, 'gemini_api_key', '') or os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": PERSONA_SYSTEM_INSTRUCTION}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    text = parts[0].get("text", "").strip()
                    text = text.replace("*", "").replace("#", "").strip()
                    return text
        else:
            print(f"Gemini API returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Gemini API request error: {e}")
        return None
