#!/usr/bin/env python3
"""
Test the chatbot with various queries to verify Ollama integration.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.chatbot_engine import ChatbotEngine

app = create_app('development')
with app.app_context():
    engine = ChatbotEngine(session=db.session)
    
    print("=" * 60)
    print("CHATBOT OLLAMA INTEGRATION TEST")
    print("=" * 60)
    
    test_queries = [
        "show me opportunities",
        "what jobs are available?",
        "tell me about placements",
        "find internships",
        "list companies",
    ]
    
    for query in test_queries:
        print(f"\n[Query] {query}")
        result = engine.process_query(query)
        print(f"[Success] {result.get('success')}")
        print(f"[Method] {result.get('extraction_method', 'unknown')}")
        print(f"[Context] {result.get('context')}")
        answer = result.get('answer', '')
        preview = answer[:150] + '...' if len(answer) > 150 else answer
        print(f"[Answer] {preview}")
        if result.get('ai_error'):
            print(f"[Error] {result.get('ai_error')}")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
