#!/usr/bin/env python3
"""
Mistral AI Chatbot Integration Verification Script
Tests Mistral, Ollama, and fallback functionality
"""

import os
import sys
import json
import requests
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_mistral_api_key() -> bool:
    """Check if Mistral API key is configured."""
    print_section("1. Mistral API Key Configuration")
    
    api_key = os.getenv('MISTRAL_API_KEY')
    
    if api_key:
        masked_key = api_key[:10] + '*' * 20 + (api_key[-4:] if len(api_key) > 14 else '')
        print(f"✅ MISTRAL_API_KEY configured: {masked_key}")
        return True
    else:
        print("❌ MISTRAL_API_KEY not set")
        print("   Run: export MISTRAL_API_KEY=your_key_here")
        print("   Or: Add MISTRAL_API_KEY=your_key_here to .env")
        return False

def test_mistral_connectivity() -> bool:
    """Test Mistral API connectivity."""
    print_section("2. Mistral API Connectivity")
    
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("⚠️  Skipping (API key not configured)")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 10
        }
        
        print("Testing connection to api.mistral.ai...")
        response = requests.post(
            "https://api.mistral.ai/v1/messages",
            headers=headers,
            json=data,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Mistral API responsive (Status: {response.status_code})")
            return True
        else:
            print(f"❌ Mistral API error (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Mistral API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot reach api.mistral.ai (network issue?)")
        return False
    except Exception as e:
        print(f"❌ Mistral API error: {str(e)}")
        return False

def test_ollama_connectivity() -> bool:
    """Test Ollama local service."""
    print_section("3. Ollama Local Service")
    
    try:
        print("Testing connection to localhost:11434...")
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running (Status: {response.status_code})")
            print(f"   Available models: {len(models)}")
            if models:
                for model in models[:5]:
                    print(f"   - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"⚠️  Ollama responded but with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Ollama is not running on localhost:11434")
        print("   Optional: Install Ollama from ollama.ai and run 'ollama serve'")
        return False
    except requests.exceptions.Timeout:
        print("⚠️  Ollama request timed out")
        return False
    except Exception as e:
        print(f"⚠️  Cannot connect to Ollama: {str(e)}")
        return False

def test_mistral_intent_extraction() -> bool:
    """Test Mistral intent extraction."""
    print_section("4. Mistral Intent Extraction")
    
    try:
        from app.chatbot_mistral import mistral_intent_extractor
        
        test_message = "Find opportunities from Google"
        print(f"Testing: '{test_message}'")
        
        result = mistral_intent_extractor(test_message)
        
        if result:
            print(f"✅ Mistral successfully extracted:")
            print(f"   Intent: {result.get('intent')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Parameters: {result.get('parameters', {})}")
            return True
        else:
            print("❌ Mistral returned None (API key missing or request failed)")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import Mistral module: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing Mistral: {str(e)}")
        return False

def test_chatbot_engine() -> bool:
    """Test ChatbotEngine with full pipeline."""
    print_section("5. Chatbot Engine Full Pipeline")
    
    try:
        from app.chatbot_engine import ChatbotEngine
        from app import db, create_app
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            engine = ChatbotEngine(session=db.session)
            
            test_queries = [
                "Find opportunities from Google",
                "Show upcoming drives",
                "What are my applications"
            ]
            
            for query in test_queries:
                print(f"\nQuery: '{query}'")
                result = engine.process_query(query, user_id=None)
                
                print(f"  ✅ Success: {result.get('success')}")
                print(f"  Intent: {result.get('intent')}")
                print(f"  Method: {result.get('extraction_method', 'unknown')}")
                print(f"  Confidence: {result.get('confidence', 'unknown')}")
                
            return True
            
    except ImportError as e:
        print(f"⚠️  Cannot import app (not in Flask context?): {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing engine: {str(e)}")
        return False

def test_requirements() -> bool:
    """Check if required packages are installed."""
    print_section("6. Required Packages")
    
    required_packages = [
        'flask',
        'requests',
        'mistralai',
        'sqlalchemy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (not installed)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all verification tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Mistral AI Chatbot Integration Verification Test      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Run tests
    results['API Key'] = test_mistral_api_key()
    results['Mistral Connectivity'] = test_mistral_connectivity()
    results['Ollama Connectivity'] = test_ollama_connectivity()
    results['Requirements'] = test_requirements()
    
    # Only test extraction and engine if requirements met
    if results['Requirements']:
        results['Mistral Extraction'] = test_mistral_intent_extraction()
        results['ChatbotEngine'] = test_chatbot_engine()
    
    # Summary
    print_section("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 All tests passed! Your Mistral integration is ready.")
        print("\nNext steps:")
        print("1. Run your Flask app: python run.py")
        print("2. Test chatbot at: http://localhost:5000/chatbot")
        print("3. Try sample queries to verify AI responses")
    elif passed >= total - 2:
        print("⚠️  Some optional tests failed but core functionality may work.")
        print("\nCheck:")
        print("- Mistral API key configuration")
        print("- Network connectivity")
        print("- Installed dependencies")
    else:
        print("❌ Integration needs attention. Check failures above.")
        print("\nSetup instructions:")
        print("1. Get API key from console.mistral.ai")
        print("2. Set MISTRAL_API_KEY in .env or environment")
        print("3. Run: pip install -r requirements.txt")
        print("4. Run verification script again")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
