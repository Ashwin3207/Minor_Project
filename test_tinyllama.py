import requests
import time

print("\n" + "="*70)
print("TESTING: TinyLlama Model - Response Time")
print("="*70 + "\n")

start = time.time()
r = requests.post('http://localhost:5000/chatbot/api/chat', 
    json={'message': 'Find software engineer positions from Google'},
    timeout=60
)
elapsed = time.time() - start

d = r.json()
print(f"RESPONSE TIME: {elapsed:.2f} seconds")
print(f"AI MODEL USED: {d.get('extraction_method')}")
print(f"SUCCESS: {d.get('success')}")
print(f"\nRESPONSE:\n")
print(d.get('answer', 'N/A'))
print("\n" + "="*70)
