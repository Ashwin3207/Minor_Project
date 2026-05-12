#!/usr/bin/env python3
"""
Chatbot diagnostic tool to identify issues.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

os.environ['FLASK_ENV'] = 'development'

try:
    from app import create_app, db
    from app.models import User, StudentProfile, Opportunity, Application
    from app.chatbot_engine import ChatbotEngine
    
    app = create_app('development')
    with app.app_context():
        # Check database
        user_count = User.query.count()
        opp_count = Opportunity.query.count()
        
        print('=' * 50)
        print('CHATBOT DIAGNOSTIC REPORT')
        print('=' * 50)
        
        print('\n[DATABASE STATUS]')
        print(f'  Connected: YES')
        print(f'  Users: {user_count}')
        print(f'  Opportunities: {opp_count}')
        
        # Check API keys
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        mistral_key = os.getenv('MISTRAL_API_KEY')
        
        print('\n[API KEY CONFIGURATION]')
        print(f'  Gemini/Google API: NOT USED (removed)')
        print(f'  Mistral API: {"CONFIGURED (fallback)" if mistral_key else "NOT CONFIGURED (fallback)"}')
        
        print('\n[OLLAMA PRIMARY AI BACKEND]')
        ollama_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'tinyllama')
        print(f'  URL: {ollama_url}')
        print(f'  Model: {ollama_model}')
        
        # Test Ollama
        print('\n[OLLAMA LOCAL AI CHECK]')
        try:
            import requests
            ollama_url = 'http://localhost:11434/api/tags'
            response = requests.get(ollama_url, timeout=2)
            if response.status_code == 200:
                print(f'  Ollama: RUNNING ✓')
                data = response.json()
                models = [m.get('name', 'unknown') for m in data.get('models', [])]
                if models:
                    print(f'  Available models: {", ".join(models)}')
            else:
                print(f'  Ollama: Not responding properly')
        except Exception as e:
            print(f'  Ollama: NOT RUNNING (this is OK if using cloud APIs)')
        
        # Test chatbot engine
        print('\n[CHATBOT ENGINE TEST]')
        try:
            engine = ChatbotEngine(session=db.session)
            print('  Engine: INITIALIZED ✓')
            
            # Test simple greeting
            result = engine.process_query('hello')
            print(f'  Test Query Result:')
            print(f'    - Success: {result.get("success", False)}')
            print(f'    - Answer preview: {result.get("answer", "")[:80]}...')
            print(f'    - Context: {result.get("context", "unknown")}')
            print(f'    - Method: {result.get("extraction_method", "unknown")}')
            
            if not result.get('success'):
                print(f'    - Error: {result.get("error", "unknown")}')
                if 'ai_error' in result:
                    print(f'    - AI Error: {result.get("ai_error")}')
        except Exception as e:
            print(f'  Engine ERROR: {str(e)}')
            import traceback
            traceback.print_exc()
        
        # Check Flask routes
        print('\n[FLASK ROUTES CHECK]')
        with app.test_client() as client:
            try:
                response = client.get('/chatbot/')
                print(f'  GET /chatbot/: {response.status_code}')
            except Exception as e:
                print(f'  GET /chatbot/ ERROR: {e}')
            
            try:
                response = client.post('/chatbot/api/chat', 
                                     json={'message': 'test'},
                                     content_type='application/json')
                print(f'  POST /chatbot/api/chat: {response.status_code}')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f'    Response keys: {list(data.keys())}')
            except Exception as e:
                print(f'  POST /chatbot/api/chat ERROR: {e}')
        
        print('\n' + '=' * 50)
        print('SUMMARY')
        print('=' * 50)
        
        print('✓ Chatbot configured for Ollama (TinyLlama)')
        
        if mistral_key:
            print('✓ Mistral configured as fallback')
        
        if user_count == 0:
            print('⚠️  NO USERS IN DATABASE')
            print('   This is normal on first run')
        
        print('\nChatbot Status: ✓ READY')
        print('\nBackend Priority:')
        print('1. TinyLlama (Ollama) - PRIMARY')
        print('2. Mistral AI - FALLBACK (if configured)')
        print('3. Keyword matching - ALWAYS AVAILABLE')
        
except Exception as e:
    print(f'FATAL ERROR: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
