#!/usr/bin/env python3
"""
Test script to verify the nl2br filter works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_nl2br_filter():
    """Test that the nl2br filter converts newlines to <br> tags"""
    with app.test_request_context():
        # Test basic functionality
        test_text = "Line 1\nLine 2\nLine 3"
        result = app.jinja_env.filters['nl2br'](test_text)
        expected = "Line 1<br>Line 2<br>Line 3"
        
        print(f"Input: {repr(test_text)}")
        print(f"Output: {repr(str(result))}")
        print(f"Expected: {repr(expected)}")
        
        assert str(result) == expected, f"Filter failed: expected {expected}, got {str(result)}"
        print("✅ nl2br filter test passed!")
        
        # Test with different line endings
        test_text_crlf = "Line 1\r\nLine 2\r\nLine 3"
        result_crlf = app.jinja_env.filters['nl2br'](test_text_crlf)
        expected_crlf = "Line 1<br>Line 2<br>Line 3"
        
        print(f"\nCRLF Input: {repr(test_text_crlf)}")
        print(f"CRLF Output: {repr(str(result_crlf))}")
        
        assert str(result_crlf) == expected_crlf, f"CRLF filter failed"
        print("✅ nl2br filter CRLF test passed!")
        
        # Test with None
        result_none = app.jinja_env.filters['nl2br'](None)
        assert str(result_none) == '', "None should return empty string"
        print("✅ nl2br filter None test passed!")

if __name__ == "__main__":
    test_nl2br_filter()
    print("\n🎉 All nl2br filter tests passed! The noteboard should now work correctly.")
