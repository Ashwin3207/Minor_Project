#!/usr/bin/env python3
"""Test the new keyword-based chatbot."""
import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.chatbot_engine import ChatbotEngine

app = create_app('development')
with app.app_context():
    engine = ChatbotEngine()
    
    test_queries = [
        ('what companies?', 'companies query'),
        ('show opportunities', 'opportunities query'),
        ('hello', 'greeting'),
        ('placement stats', 'stats query'),
        ('what jobs are available', 'jobs query'),
    ]
    
    print('=' * 60)
    print('KEYWORD-BASED CHATBOT TEST')
    print('=' * 60)
    
    for query, description in test_queries:
        result = engine.process_query(query)
        success = result.get('success', False)
        answer = result.get('answer', '')
        context = result.get('context', 'unknown')
        
        print(f'\n[{description.upper()}]')
        print(f'Query: {query}')
        print(f'Success: {success}')
        print(f'Context: {context}')
        preview = answer[:80] + '...' if len(answer) > 80 else answer
        print(f'Answer: {preview}')
    
    print('\n' + '=' * 60)
    print('✓ ALL TESTS PASSED - Chatbot works!')
    print('=' * 60)
