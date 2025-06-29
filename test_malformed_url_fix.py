#!/usr/bin/env python3
"""
Test calendar hanging issue fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_malformed_url_protection():
    """Test protection against malformed URLs with JSON data"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        print("🧪 Testing Malformed URL Protection")
        print("=" * 50)
        
        # Test 1: Test the exact problematic URL from the log
        problematic_url = '/[{"id": "f9077094-97d2-4dd1-a3be-7a20bcc10f9d", "title": "ryry", "start": "2025-06-02 09:00", "backgroundColor": ""'
        
        print(f"\n1. Testing problematic URL: {problematic_url[:60]}...")
        response = client.get(problematic_url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            print("   ✅ URL correctly redirected (not 404)")
            location = response.headers.get('Location', '')
            print(f"   Redirected to: {location}")
        else:
            print(f"   Response: {response.get_data(as_text=True)[:100]}")
        
        # Test 2: Test other JSON-like malformed URLs
        malformed_urls = [
            '/{"title": "test"}',
            '/[{"id": "123"}]',
            '/"id": "test"',
            '/{"start": "2025-01-01"}'
        ]
        
        print(f"\n2. Testing various malformed JSON URLs...")
        for url in malformed_urls:
            response = client.get(url)
            status = "✅ Protected" if response.status_code in [302, 404] else "❌ Not protected"
            print(f"   {url[:30]:<30} - {response.status_code} - {status}")
        
        # Test 3: Test normal URLs still work
        print(f"\n3. Testing normal URLs still work...")
        normal_urls = [
            '/',
            '/login',
            '/api/calendar-events',  # This should redirect to login for unauthenticated user
        ]
        
        for url in normal_urls:
            response = client.get(url)
            status = "✅ Normal" if response.status_code in [200, 302] else "❌ Broken"
            print(f"   {url:<30} - {response.status_code} - {status}")
        
        print("\n" + "=" * 50)
        print("🎯 Malformed URL protection test completed!")

if __name__ == '__main__':
    test_malformed_url_protection()
