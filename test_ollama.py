import requests
import json

prompt = "Extract intent from: Find software engineer from Google. Return only JSON."

response = requests.post('http://localhost:11434/api/generate', 
    json={'model': 'orca-mini', 'prompt': prompt, 'stream': False, 'temperature': 0.1, 'num_predict': 80},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    text = data.get('response', '')
    print('Ollama response:')
    print(text)
    print('\n---Length:', len(text))
else:
    print('Error:', response.status_code, response.text[:200])
