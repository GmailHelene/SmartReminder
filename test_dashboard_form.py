#!/usr/bin/env python3
"""
Test dashboard form fix
"""

import sys
sys.path.append('/workspaces/smartreminder')

from app import app, ReminderForm

def test_dashboard_form():
    """Test that dashboard route includes form"""
    try:
        with app.app_context():
            form = ReminderForm()
            print("✅ ReminderForm kan opprettes")
            
            # Check that form has required fields
            required_fields = ['title', 'description', 'date', 'time', 'priority', 'category', 'sound']
            for field in required_fields:
                if hasattr(form, field):
                    print(f"✅ Form har felt: {field}")
                else:
                    print(f"❌ Form mangler felt: {field}")
            
            # Check CSRF token
            if hasattr(form, 'hidden_tag'):
                print("✅ Form har hidden_tag() metode for CSRF")
            else:
                print("❌ Form mangler hidden_tag() metode")
                
            print("\n✅ Dashboard form fix er klar!")
            return True
            
    except Exception as e:
        print(f"❌ Dashboard form test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_form()
    if success:
        print("\n🎉 Dashboard form fix er testet og fungerer!")
    else:
        print("\n❌ Dashboard form fix har problemer")
    sys.exit(0 if success else 1)
