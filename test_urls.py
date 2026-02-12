#!/usr/bin/env python
"""Test URL generation"""
from app import create_app

app = create_app()

with app.app_context():
    from flask import url_for
    print("Testing URL generation:\n")
    print(f"url_for('auth.signup'): {url_for('auth.signup')}")
    print(f"url_for('auth.login'): {url_for('auth.login')}")
