#!/usr/bin/env python3
"""Test the noteboard template fix"""

import os
os.environ['FLASK_ENV'] = 'development'

try:
    from app import app
    from jinja2 import Template
    
    # Test the replace approach
    test_template = """{{ content|replace('\\n', '<br>')|replace('\\r\\n', '<br>')|replace('\\r', '<br>')|safe }}"""
    
    # Create a Jinja2 template
    template = Template(test_template)
    
    # Test with newline content
    test_content = "Line 1\nLine 2\r\nLine 3"
    result = template.render(content=test_content)
    
    print(f"Input: {repr(test_content)}")
    print(f"Output: {repr(result)}")
    
    if '<br>' in result:
        print("✅ Template fix works correctly")
    else:
        print("❌ Template fix failed")
        
    # Also test the Flask filter registration
    print(f"\nFlask app nl2br filter registered: {'nl2br' in app.jinja_env.filters}")
    
    # Test the filter directly if it's registered
    if 'nl2br' in app.jinja_env.filters:
        filter_func = app.jinja_env.filters['nl2br']
        filter_result = filter_func(test_content)
        print(f"Filter result: {repr(str(filter_result))}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
