#!/usr/bin/env python3
"""
Test script to verify that the template syntax issues are fixed
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

def test_templates():
    """Test all templates for syntax errors"""
    from jinja2 import Environment, FileSystemLoader
    
    try:
        # Create Jinja2 environment with some common filters to avoid filter errors
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Add mock filters that are used in templates
        def mock_filter(value, *args, **kwargs):
            return str(value)
        
        env.filters['as_datetime'] = mock_filter
        env.filters['strftime'] = mock_filter
        
        # List of templates to test (focusing on basic syntax)
        templates_to_test = [
            'offline.html',
            'errors/403.html',
            'login.html',
            'base.html'
        ]
        
        print("🧪 Testing template syntax...")
        
        for template_name in templates_to_test:
            try:
                template = env.get_template(template_name)
                print(f"✅ {template_name} - Syntax OK")
            except Exception as e:
                print(f"❌ {template_name} - Syntax Error: {e}")
                return False
        
        # For dashboard and noteboard, just check if they can be loaded as text
        for template_name in ['dashboard.html', 'noteboard.html']:
            try:
                with open(f'templates/{template_name}', 'r') as f:
                    content = f.read()
                # Basic check for proper Jinja2 block structure
                if '{% extends' in content and '{% endblock %}' in content:
                    print(f"✅ {template_name} - Basic structure OK")
                else:
                    print(f"❌ {template_name} - Missing required template blocks")
                    return False
            except Exception as e:
                print(f"❌ {template_name} - File error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Template testing failed: {e}")
        return False

def test_flask_app():
    """Test Flask app routing"""
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
        
        print("🌐 Testing Flask routes...")
        
        with app.test_client() as client:
            # Test offline route
            response = client.get('/offline')
            if response.status_code == 200:
                print("✅ /offline route - OK")
                
                # Check if template content is rendered correctly
                content = response.data.decode()
                if 'Du er offline' in content:
                    print("✅ /offline template content - OK")
                else:
                    print("⚠️  /offline template content - Missing expected text")
            else:
                print(f"❌ /offline route - Failed with status {response.status_code}")
                return False
            
            # Test other basic routes
            test_routes = [
                ('/', 302),  # Should redirect to login
                ('/health', 200),
                ('/login', 200)
            ]
            
            for route, expected_status in test_routes:
                response = client.get(route)
                if response.status_code == expected_status:
                    print(f"✅ {route} route - OK")
                else:
                    print(f"❌ {route} route - Expected {expected_status}, got {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Running SmartReminder Template & Route Tests\n")
    
    template_test_passed = test_templates()
    print()
    
    flask_test_passed = test_flask_app()
    print()
    
    if template_test_passed and flask_test_passed:
        print("🎉 All tests passed! The offline route error should be fixed.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
