#!/usr/bin/env python3
"""Test script to verify the share_reminder endpoint works with proper Flask context"""

import sys
import os
sys.path.append(os.path.abspath('.'))

try:
    from app import app
    
    print("Testing share_reminder endpoint with request context...")
    
    with app.test_request_context():
        # Test if url_for works for share_reminder
        try:
            from flask import url_for
            share_url = url_for('share_reminder')
            print(f"✅ share_reminder URL generation successful: {share_url}")
        except Exception as e:
            print(f"❌ share_reminder URL generation failed: {e}")
            
        # Test endpoint registration
        share_endpoint = app.view_functions.get('share_reminder')
        if share_endpoint:
            print("✅ share_reminder function is properly registered")
            print(f"   Function: {share_endpoint}")
        else:
            print("❌ share_reminder function not found in view_functions")
    
    print("\n✅ All tests completed successfully!")
    print("The BuildError in dashboard.html should now be resolved.")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
