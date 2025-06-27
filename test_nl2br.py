#!/usr/bin/env python3
"""Test the nl2br filter specifically"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_nl2br_filter():
    """Test if the nl2br filter is registered and working"""
    
    # Test the filter directly
    with app.app_context():
        # Get the filter from Jinja2 environment
        nl2br_filter = app.jinja_env.filters.get('nl2br')
        
        if nl2br_filter is None:
            print("❌ nl2br filter is NOT registered!")
            return False
        
        print("✅ nl2br filter is registered")
        
        # Test the filter functionality
        test_text = "Line 1\nLine 2\r\nLine 3"
        result = nl2br_filter(test_text)
        expected = "Line 1<br>Line 2<br>Line 3"
        
        print(f"Input: {repr(test_text)}")
        print(f"Output: {repr(str(result))}")
        print(f"Expected: {repr(expected)}")
        
        if str(result) == expected:
            print("✅ nl2br filter works correctly")
            return True
        else:
            print("❌ nl2br filter does not work correctly")
            return False

def test_noteboard_template():
    """Test if the noteboard template can be rendered"""
    
    try:
        with app.app_context():
            # Try to get the template
            from flask import render_template_string
            
            # Simple test with the nl2br filter
            test_template = "{{ 'Hello\\nWorld'|nl2br }}"
            result = render_template_string(test_template)
            
            print(f"Template test result: {repr(result)}")
            
            if '<br>' in result:
                print("✅ Template rendering with nl2br filter works")
                return True
            else:
                print("❌ Template rendering with nl2br filter failed")
                return False
                
    except Exception as e:
        print(f"❌ Template test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing nl2br filter...")
    
    # Test filter registration
    filter_ok = test_nl2br_filter()
    
    # Test template rendering
    template_ok = test_noteboard_template()
    
    if filter_ok and template_ok:
        print("\n✅ All tests passed! nl2br filter should work.")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
