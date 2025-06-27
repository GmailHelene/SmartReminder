#!/usr/bin/env python3
"""
Test script to verify the routes work correctly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project directory to path
sys.path.insert(0, '.')

# Set testing environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'true'

def test_routes():
    """Test the problematic routes"""
    try:
        from app import app, dm
        
        # Create temporary directory for testing
        test_dir = tempfile.mkdtemp()
        dm.data_dir = Path(test_dir)
        dm._ensure_data_files()
        
        # Configure app for testing
        app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'MAIL_SUPPRESS_SEND': True
        })
        
        print("🌐 Testing problematic routes...")
        
        with app.test_client() as client:
            # Test routes without login (should redirect to login)
            test_routes = [
                ('/noteboards', 'Noteboards route'),
                ('/email-settings', 'Email settings route')
            ]
            
            for route, description in test_routes:
                try:
                    response = client.get(route)
                    if response.status_code == 302:  # Redirect to login
                        print(f"✅ {description} - Correctly redirects to login")
                    elif response.status_code == 200:
                        print(f"✅ {description} - Returns 200 (might be accessible without login)")
                    else:
                        print(f"❌ {description} - Status: {response.status_code}")
                        print(f"   Response: {response.data.decode()[:200]}...")
                        return False
                except Exception as e:
                    print(f"❌ {description} - Exception: {e}")
                    return False
        
        print("✅ All routes tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_templates():
    """Test template syntax"""
    from jinja2 import Environment, FileSystemLoader
    
    try:
        # Create Jinja2 environment with mock filters
        env = Environment(loader=FileSystemLoader('templates'))
        
        def mock_filter(value, *args, **kwargs):
            return str(value)
        
        env.filters['as_datetime'] = mock_filter
        env.filters['strftime'] = mock_filter
        
        templates_to_test = [
            'noteboards.html',
            'noteboard.html',
            'email_settings.html'
        ]
        
        print("🧪 Testing template syntax...")
        
        for template_name in templates_to_test:
            try:
                template = env.get_template(template_name)
                print(f"✅ {template_name} - Syntax OK")
            except Exception as e:
                print(f"❌ {template_name} - Syntax Error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Template testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing /noteboards and /email-settings routes\n")
    
    template_test_passed = test_templates()
    print()
    
    route_test_passed = test_routes()
    print()
    
    if template_test_passed and route_test_passed:
        print("🎉 All tests passed! The 500 errors should be fixed.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
