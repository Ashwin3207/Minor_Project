import requests
import time

questions = [
    "Find software engineer positions from Google",
    "What internship opportunities are available?",
    "Tell me about placement process",
    "Search for developer jobs"
]

print("=" * 70)
print("CHATBOT RESPONSE TIME TEST")
print("=" * 70)

for q in questions:
    print(f"\n📝 Question: {q}")
    
    start = time.time()
    try:
        r = requests.post(
            'http://localhost:5000/chatbot/api/chat',
            json={'message': q},
            timeout=120
        )
        elapsed = time.time() - start
        
        data = r.json()
        answer = data.get('answer', '')[:150]
        method = data.get('extraction_method', 'unknown')
        
        print(f"⏱️  Response Time: {elapsed:.2f} seconds")
        print(f"🤖 Method: {method}")
        print(f"💬 Answer Preview: {answer}...")
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {str(e)}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
