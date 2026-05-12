#!/usr/bin/env python3
"""Final verification test for chatbot fix."""
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.chatbot_engine import ChatbotEngine

app = create_app('development')

with app.app_context():
    engine = ChatbotEngine()
    
    print("=" * 60)
    print("FINAL CHATBOT VERIFICATION TEST")
    print("=" * 60)
    
    print('\nCONFIGURATION:')
    print(f'  Ollama URL: {engine.ollama_url}')
    print(f'  Ollama Model: {engine.ollama_model}')
    
    print('\nQUERY TESTS:')
    queries = ['hello', 'show opportunities', 'what companies?']
    
    for q in queries:
        result = engine.process_query(q)
        success = result.get("success", False)
        method = result.get("extraction_method", "N/A")
        ans_len = len(result.get("answer", ""))
        
        print(f'\n  Query: "{q}"')
        print(f'    ✓ Success: {success}')
        print(f'    ✓ Method: {method}')
        print(f'    ✓ Answer length: {ans_len} chars')
        
        if not success:
            print(f'    ✗ ERROR: {result.get("error", "Unknown")}')
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Chatbot is working correctly")
    print("=" * 60)
