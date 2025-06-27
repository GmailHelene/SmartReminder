#!/usr/bin/env python3
"""
Simple deployment test script to verify all dependencies and imports work correctly.
"""

import sys
import os

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    
    try:
        # Test Flask imports
        from flask import Flask
        print("✓ Flask imported successfully")
        
        from flask_login import LoginManager
        print("✓ Flask-Login imported successfully")
        
        from flask_mail import Mail
        print("✓ Flask-Mail imported successfully")
        
        from flask_wtf import FlaskForm
        print("✓ Flask-WTF imported successfully")
        
        from wtforms import StringField
        print("✓ WTForms imported successfully")
        
        from werkzeug.security import generate_password_hash
        print("✓ Werkzeug imported successfully")
        
        # Test APScheduler
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✓ APScheduler imported successfully")
        
        # Test other dependencies
        import json, os, logging, hashlib, uuid
        from pathlib import Path
        from datetime import datetime, timedelta
        print("✓ Standard library imports successful")
        
        print("\nAll imports successful! ✓")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created."""
    print("\nTesting Flask app creation...")
    
    try:
        from app import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    
    try:
        # Test environment variables
        env_vars = ['SECRET_KEY', 'MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        missing_vars = []
        
        for var in env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠ Missing environment variables: {', '.join(missing_vars)}")
            print("  (This is normal for local testing)")
        else:
            print("✓ All environment variables set")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Deployment Test Script ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_config,
        test_app_creation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results ===")
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("✓ All tests passed! App should deploy successfully.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
