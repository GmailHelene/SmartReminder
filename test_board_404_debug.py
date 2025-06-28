#!/usr/bin/env python3
"""
Debug script to test board API endpoints and identify 404 errors.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_board_endpoints():
    """Test all board-related endpoints to identify 404 errors."""
    print("=== Testing Board API Endpoints for 404 Errors ===\n")
    
    # Test routes without authentication first
    with app.test_client() as client:
        
        # Test endpoints that should be accessible
        test_cases = [
            # Basic board endpoints
            ('GET', '/noteboards', 'Noteboards listing'),
            ('GET', '/join-board', 'Join board page'),
            
            # Board-specific endpoints (will need valid board_id)
            ('GET', '/board/test-board-id', 'View specific board'),
            ('GET', '/noteboard/test-board-id', 'View specific noteboard'),
            
            # API endpoints
            ('GET', '/api/reminder-count', 'Reminder count API'),
            
            # POST endpoints (will test structure, not functionality)
            ('POST', '/create-board', 'Create board endpoint'),
            ('POST', '/join-board', 'Join board POST endpoint'),
            ('POST', '/add-note-to-board/test-board-id', 'Add note to board'),
            ('POST', '/api/update-note-position/test-note-id', 'Update note position'),
            ('POST', '/api/edit-note/test-note-id', 'Edit note'),
            ('DELETE', '/api/delete-note/test-note-id', 'Delete note'),
        ]
        
        results = []
        
        for method, endpoint, description in test_cases:
            try:
                if method == 'GET':
                    response = client.get(endpoint)
                elif method == 'POST':
                    response = client.post(endpoint, json={})
                elif method == 'DELETE':
                    response = client.delete(endpoint)
                
                status_code = response.status_code
                if status_code == 404:
                    results.append(f"❌ 404 ERROR: {description} ({method} {endpoint})")
                elif status_code in [200, 302, 400, 401, 403, 500]:  # Expected codes
                    results.append(f"✅ OK: {description} ({method} {endpoint}) - Status: {status_code}")
                else:
                    results.append(f"⚠️  UNEXPECTED: {description} ({method} {endpoint}) - Status: {status_code}")
                    
            except Exception as e:
                results.append(f"❌ ERROR: {description} ({method} {endpoint}) - Exception: {str(e)}")
            
        print("Test Results:")
        print("=" * 60)
        for result in results:
            print(result)
        
        # Count 404 errors
        error_404_count = len([r for r in results if "404 ERROR" in r])
        print(f"\n📊 Summary: {error_404_count} endpoints returning 404 errors")
        
        if error_404_count > 0:
            print("\n🔍 Investigating 404 errors...")
            return False
        else:
            print("\n✅ No 404 errors found in board API endpoints!")
            return True

def test_route_registration():
    """Check if all routes are properly registered."""
    print("\n=== Checking Route Registration ===\n")
    
    with app.app_context():
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Filter board-related routes
        board_routes = [r for r in routes if 'board' in r['rule'].lower() or 'note' in r['endpoint'].lower()]
        
        print("Board-related routes registered:")
        print("-" * 50)
        for route in board_routes:
            methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
            print(f"  {route['rule']} -> {route['endpoint']} [{methods}]")
        
        # Check for specific endpoints we expect
        expected_endpoints = [
            '/noteboards',
            '/create-board',
            '/join-board',
            '/board/<board_id>',
            '/noteboard/<board_id>',
            '/add-note-to-board/<board_id>',
            '/api/update-note-position/<note_id>',
            '/api/edit-note/<note_id>',
            '/api/delete-note/<note_id>'
        ]
        
        registered_rules = [r['rule'] for r in routes]
        
        print(f"\n📋 Expected endpoints check:")
        print("-" * 40)
        for endpoint in expected_endpoints:
            if endpoint in registered_rules:
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - NOT REGISTERED")
        
        return len(board_routes)

def main():
    """Main test function."""
    print("🚀 Starting Board API 404 Debug Test")
    print("=" * 50)
    
    # Test route registration
    route_count = test_route_registration()
    print(f"\n📊 Found {route_count} board-related routes registered")
    
    # Test for 404 errors
    no_404_errors = test_board_endpoints()
    
    if no_404_errors:
        print("\n🎉 All board API endpoints are accessible (no 404 errors)")
    else:
        print("\n⚠️  Some board API endpoints are returning 404 errors")
        print("    This could be due to:")
        print("    - Missing route registration")
        print("    - URL pattern mismatch")
        print("    - Authentication requirements")
        print("    - Missing parameters")
    
    return no_404_errors

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
