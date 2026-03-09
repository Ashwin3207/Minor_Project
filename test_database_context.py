#!/usr/bin/env python
"""Test database context extraction from chatbot engine."""

import sys
import os
from app import create_app, db
from app.chatbot_engine import ChatbotEngine

# Create Flask app context
app = create_app()

with app.app_context():
    engine = ChatbotEngine()
    
    print("=" * 60)
    print("TESTING DATABASE CONTEXT EXTRACTION")
    print("=" * 60)
    
    # Test 1: Opportunity Query
    print("\n[TEST 1] Opportunity Query")
    print("User message: 'Find software engineer positions'")
    context = engine._extract_database_context("Find software engineer positions")
    print(f"Extracted context:\n{context if context else '(No context extracted)'}")
    
    # Test 2: Eligibility Query
    print("\n[TEST 2] Eligibility Query")
    print("User message: 'Am I eligible for this position?'")
    context = engine._extract_database_context("Am I eligible for this position?")
    print(f"Extracted context:\n{context if context else '(No context extracted)'}")
    
    # Test 3: Status Query
    print("\n[TEST 3] Application Status Query")
    print("User message: 'What is my application status?'")
    context = engine._extract_database_context("What is my application status?")
    print(f"Extracted context:\n{context if context else '(No context extracted)'}")
    
    # Test 4: Statistics Query
    print("\n[TEST 4] Placement Statistics Query")
    print("User message: 'What is the placement rate?'")
    context = engine._extract_database_context("What is the placement rate?")
    print(f"Extracted context:\n{context if context else '(No context extracted)'}")
    
    # Test 5: Full process_query Flow
    print("\n" + "=" * 60)
    print("[TEST 5] Full process_query() Flow")
    print("=" * 60)
    print("User message: 'Find opportunities in tech'")
    result = engine.process_query("Find opportunities in tech")
    print(f"\nResult:")
    print(f"  Success: {result.get('success')}")
    print(f"  Context: {result.get('context')}")
    print(f"  Extraction Method: {result.get('extraction_method')}")
    print(f"  Answer (first 200 chars):\n    {result.get('answer', '')[:200]}...")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed")
    print("=" * 60)
