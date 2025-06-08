import requests

OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"

def generate_reply(prompt):
    url = f"{OLLAMA_API_URL}/api/generate"
    try:
        response = requests.post(url, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"❌ Failed: {response.status_code} | {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Could not connect to Ollama server. Is it running?"
