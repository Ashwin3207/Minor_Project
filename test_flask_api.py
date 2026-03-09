#!/usr/bin/env python
"""Test the Flask chatbot API endpoint with database context."""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
CHATBOT_ENDPOINT = f"{BASE_URL}/chatbot/api/chat"

print("=" * 70)
print("FLASK CHATBOT API TEST - DATABASE CONTEXT INTEGRATION")
print("=" * 70)

test_messages = [
    {"message": "Find software engineer positions", "name": "Opportunity Query"},
    {"message": "What is the placement rate?", "name": "Statistics Query"},
    {"message": "Hello!", "name": "Greeting"},
    {"message": "Am I eligible for any positions?", "name": "Eligibility Query"},
]

print(f"\nTesting endpoint: {CHATBOT_ENDPOINT}\n")

for test in test_messages:
    print("-" * 70)
    print(f"[TEST] {test['name']}")
    print(f"Message: {test['message']}")
    print("-" * 70)
    
    try:
        response = requests.post(
            CHATBOT_ENDPOINT,
            json={"message": test['message']},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"  Success: {data.get('success')}")
            print(f"  Context: {data.get('context')}")
            print(f"  Method: {data.get('extraction_method', 'N/A')}")
            
            answer = data.get('answer', '').strip()
            if len(answer) > 250:
                print(f"\nAnswer:\n{answer[:250]}...\n")
            else:
                print(f"\nAnswer:\n{answer}\n")
        else:
            print(f"✗ Status: {response.status_code}")
            print(f"Response: {response.text}\n")
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to Flask server")
        print("  Make sure Flask is running on localhost:5000\n")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}\n")

print("=" * 70)
print("API Test Complete")
print("=" * 70)
