#!/usr/bin/env python3
"""Test script to verify the dashboard template renders without BuildError"""

import sys
import os
sys.path.append(os.path.abspath('.'))

try:
    from app import app, User, dm
    from flask import url_for
    
    print("Testing dashboard template rendering...")
    
    with app.app_context():
        # Test if url_for works for share_reminder
        try:
            share_url = url_for('share_reminder')
            print(f"✅ share_reminder URL generation successful: {share_url}")
        except Exception as e:
            print(f"❌ share_reminder URL generation failed: {e}")
            
        # Test if we can render the dashboard template
        try:
            from flask import render_template
            
            # Create a mock user for testing
            test_user = User()
            test_user.email = "test@example.com"
            test_user.name = "Test User"
            
            # Create mock data for the template
            reminders = []
            shared_reminders = []
            focus_mode = "normal"
            
            # Try to render the template with mock data
            rendered = render_template('dashboard.html', 
                                     user=test_user,
                                     reminders=reminders,
                                     shared_reminders=shared_reminders,
                                     focus_mode=focus_mode,
                                     active_page='dashboard')
            
            if rendered:
                print("✅ Dashboard template rendered successfully!")
                print(f"   Template length: {len(rendered)} characters")
            else:
                print("❌ Dashboard template rendering returned empty result")
                
        except Exception as e:
            print(f"❌ Dashboard template rendering failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nTest completed!")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
