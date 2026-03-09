import requests
import time

q = 'What qualifications do I need for a software engineer job?'
print(f"\nQuestion: {q}\n")

start = time.time()
r = requests.post('http://localhost:5000/chatbot/api/chat', 
    json={'message': q},
    timeout=60
)
elapsed = time.time() - start

d = r.json()
print(f'Response Time: {elapsed:.2f} seconds')
print(f'Model: {d.get("extraction_method")}')
print(f'\nAnswer:\n\n{d.get("answer", "N/A")}')
