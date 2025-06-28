#!/usr/bin/env python3
"""Test to debug route registration"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

try:
    from app import app
    
    print("🌐 Checking registered routes...")
    
    with app.app_context():
        # List all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.rule, rule.endpoint, rule.methods))
        
        # Sort by endpoint name
        routes.sort(key=lambda x: x[1])
        
        print(f"Total routes registered: {len(routes)}")
        print("\nRoutes:")
        for rule, endpoint, methods in routes:
            print(f"  {endpoint:25} -> {rule:30} {sorted(methods)}")
        
        # Check specifically for the problematic ones
        problematic_endpoints = ['noteboards', 'focus_modes', 'email_settings']
        
        print("\n🔍 Checking problematic endpoints:")
        for endpoint in problematic_endpoints:
            found = False
            for rule, ep, methods in routes:
                if ep == endpoint:
                    print(f"  ✅ {endpoint} -> {rule}")
                    found = True
                    break
            if not found:
                print(f"  ❌ {endpoint} -> NOT FOUND")
        
        # Try to generate URLs for the problematic ones
        print("\n🧪 Testing URL generation:")
        from flask import url_for
        
        for endpoint in problematic_endpoints:
            try:
                url = url_for(endpoint)
                print(f"  ✅ url_for('{endpoint}') -> {url}")
            except Exception as e:
                print(f"  ❌ url_for('{endpoint}') -> Error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
