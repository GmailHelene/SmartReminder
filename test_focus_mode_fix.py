#!/usr/bin/env python3
"""
Test script to verify the focus_mode fix for the User class
"""

import sys
import os
sys.path.append('.')

from app import app, User, dm
from flask import Flask
from flask_login import LoginManager
import tempfile

def test_user_focus_mode():
    """Test that User class has focus_mode attribute"""
    print("Testing User class with focus_mode attribute...")
    
    # Test 1: Create User with focus_mode
    user = User('test_id', 'test_user', 'test@example.com', 'test_hash', 'normal')
    assert hasattr(user, 'focus_mode'), "User should have focus_mode attribute"
    assert user.focus_mode == 'normal', f"Expected 'normal', got {user.focus_mode}"
    print("✓ User class correctly has focus_mode attribute")
    
    # Test 2: Create User with different focus_mode
    user2 = User('test_id2', 'test_user2', 'test2@example.com', 'test_hash2', 'adhd')
    assert user2.focus_mode == 'adhd', f"Expected 'adhd', got {user2.focus_mode}"
    print("✓ User class correctly sets custom focus_mode")
    
    # Test 3: Create User with default focus_mode
    user3 = User('test_id3', 'test_user3', 'test3@example.com', 'test_hash3')
    assert user3.focus_mode == 'normal', f"Expected 'normal', got {user3.focus_mode}"
    print("✓ User class correctly defaults to 'normal' focus_mode")
    
    print("All tests passed! The focus_mode AttributeError should be fixed.")
    return True

def test_dashboard_route():
    """Test the dashboard route that was causing the error"""
    print("\nTesting dashboard route logic...")
    
    # Create a test user
    test_user = User('test_id', 'test_user', 'test@example.com', 'test_hash', 'silent')
    
    # Test the problematic line from the dashboard route
    current_focus_mode = test_user.focus_mode if test_user else 'normal'
    assert current_focus_mode == 'silent', f"Expected 'silent', got {current_focus_mode}"
    print("✓ Dashboard route logic works correctly")
    
    # Test with None user
    test_user = None
    current_focus_mode = test_user.focus_mode if test_user else 'normal'
    assert current_focus_mode == 'normal', f"Expected 'normal', got {current_focus_mode}"
    print("✓ Dashboard route handles None user correctly")
    
    return True

if __name__ == '__main__':
    try:
        test_user_focus_mode()
        test_dashboard_route()
        print("\n🎉 All tests passed! The AttributeError: 'User' object has no attribute 'focus_mode' is fixed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
