#!/usr/bin/env python3
"""
Test script to verify noteboard functionality end-to-end
"""

import requests
import json
from bs4 import BeautifulSoup
import time

BASE_URL = "http://localhost:5000"

def test_noteboard_functionality():
    """Test the complete noteboard workflow"""
    print("🧪 Testing Noteboard Functionality")
    print("=" * 50)
    
    # Test 1: Check if login page loads
    print("1. Testing login page...")
    try:
        response = requests.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            print("   ✅ Login page loads successfully")
        else:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login page error: {e}")
        return False
    
    # Test 2: Login with test user
    print("2. Testing login...")
    session = requests.Session()
    
    # Get login page to extract CSRF token
    login_page = session.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token['value']
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if login_response.status_code == 200 and "dashboard" in login_response.url:
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        # Continue anyway, maybe we can access without login
    
    # Test 3: Access noteboards page
    print("3. Testing noteboards page...")
    try:
        boards_response = session.get(f"{BASE_URL}/noteboards")
        if boards_response.status_code == 200:
            print("   ✅ Noteboards page loads successfully")
            
            # Check if test board is visible
            if "Test Board" in boards_response.text:
                print("   ✅ Test board is visible")
            else:
                print("   ⚠️  Test board not found (may need to create one)")
        else:
            print(f"   ❌ Noteboards page failed: {boards_response.status_code}")
    except Exception as e:
        print(f"   ❌ Noteboards page error: {e}")
    
    # Test 4: Try to view specific board
    print("4. Testing specific board view...")
    try:
        board_response = session.get(f"{BASE_URL}/board/test-board-123")
        if board_response.status_code == 200:
            print("   ✅ Individual board page loads successfully")
            
            # Check if note content is visible
            if "This is a test note" in board_response.text:
                print("   ✅ Board notes are visible")
            else:
                print("   ⚠️  Board notes not found")
        else:
            print(f"   ❌ Board view failed: {board_response.status_code}")
    except Exception as e:
        print(f"   ❌ Board view error: {e}")
    
    # Test 5: Test join board functionality
    print("5. Testing join board page...")
    try:
        join_response = session.get(f"{BASE_URL}/join-board")
        if join_response.status_code == 200:
            print("   ✅ Join board page loads successfully")
        else:
            print(f"   ❌ Join board page failed: {join_response.status_code}")
    except Exception as e:
        print(f"   ❌ Join board page error: {e}")
    
    # Test 6: Check API endpoints
    print("6. Testing API endpoints...")
    try:
        # Test board data API
        api_response = session.get(f"{BASE_URL}/api/board/test-board-123")
        if api_response.status_code == 200:
            board_data = api_response.json()
            print("   ✅ Board API endpoint works")
            print(f"   📊 Board title: {board_data.get('title', 'N/A')}")
            print(f"   📝 Notes count: {len(board_data.get('notes', []))}")
        else:
            print(f"   ❌ Board API failed: {api_response.status_code}")
    except Exception as e:
        print(f"   ❌ Board API error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Noteboard functionality test completed!")
    return True

if __name__ == "__main__":
    test_noteboard_functionality()
