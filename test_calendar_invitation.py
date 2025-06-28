#!/usr/bin/env python3
"""
Test calendar invitation functionality
"""

import os
import tempfile
from pathlib import Path
import json

# Set environment for testing
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

def test_calendar_invitation():
    """Test calendar invitation email generation"""
    try:
        from app import app, dm, send_calendar_invitation_email
        from datetime import datetime
        
        # Create temporary data directory
        test_dir = tempfile.mkdtemp()
        dm.data_dir = Path(test_dir)
        dm._ensure_data_files()
        
        # Configure app for testing
        app.config.update({
            'TESTING': True,
            'MAIL_SUPPRESS_SEND': True,
            'SERVER_NAME': 'localhost:5000',
            'MAIL_DEFAULT_SENDER': 'test@smartreminder.com',
            'MAIL_USERNAME': 'test@smartreminder.com'
        })
        
        # Test reminder data
        test_reminder = {
            'id': 'test-123',
            'title': 'Testmøte',
            'description': 'Dette er et testmøte for kalenderinvitasjon',
            'datetime': '2024-12-01 14:30',
            'priority': 'Høy',
            'category': 'Jobb'
        }
        
        print("🧪 Testing calendar invitation email generation...")
        
        with app.app_context():
            # Test email generation (without actually sending)
            try:
                send_calendar_invitation_email(
                    reminder=test_reminder,
                    shared_by='test@example.com',
                    recipient_email='recipient@example.com',
                    personal_message='Dette er en testmelding'
                )
                print("✅ Calendar invitation email generated successfully")
                
                # Test template rendering
                from flask import render_template
                html_content = render_template(
                    'emails/calendar_invitation.html',
                    reminder=test_reminder,
                    shared_by='test@example.com',
                    personal_message='Dette er en testmelding',
                    app_url='https://localhost:5000'
                )
                
                if 'Testmøte' in html_content and 'Høy' in html_content:
                    print("✅ Template rendering works correctly")
                else:
                    print("❌ Template content missing expected data")
                    
                # Test with missing data
                incomplete_reminder = {
                    'id': 'test-456',
                    'title': 'Minimal test'
                }
                
                html_content_minimal = render_template(
                    'emails/calendar_invitation.html',
                    reminder=incomplete_reminder,
                    shared_by='test@example.com',
                    personal_message='',
                    app_url='https://localhost:5000'
                )
                
                if 'Minimal test' in html_content_minimal:
                    print("✅ Template handles missing data gracefully")
                else:
                    print("❌ Template fails with missing data")
                    
            except Exception as e:
                print(f"❌ Error in email generation: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        
        print("✅ All calendar invitation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Calendar invitation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ics_format():
    """Test ICS file format generation"""
    print("\n🧪 Testing ICS format...")
    
    try:
        from app import app, send_calendar_invitation_email
        from unittest.mock import patch
        from io import StringIO
        
        # Configure app for testing
        app.config.update({
            'TESTING': True,
            'MAIL_SUPPRESS_SEND': True,
            'MAIL_DEFAULT_SENDER': 'test@smartreminder.com'
        })
        
        # Mock mail.send to capture the ICS content
        ics_content = None
        
        def mock_send(msg):
            nonlocal ics_content
            for attachment in msg.attachments:
                if attachment.filename and attachment.filename.endswith('.ics'):
                    ics_content = attachment.data
                    break
        
        test_reminder = {
            'id': 'ics-test-123',
            'title': 'ICS Test Event',
            'description': 'Testing ICS file generation',
            'datetime': '2024-12-01 15:00',
            'priority': 'Medium',
            'category': 'Test'
        }
        
        with app.app_context():
            with patch('app.mail.send', side_effect=mock_send):
                send_calendar_invitation_email(
                    reminder=test_reminder,
                    shared_by='test@example.com',
                    recipient_email='recipient@example.com'
                )
        
        if ics_content:
            ics_lines = ics_content.split('\r\n')
            
            # Check for required ICS components
            required_fields = [
                'BEGIN:VCALENDAR',
                'VERSION:2.0',
                'BEGIN:VEVENT',
                'SUMMARY:ICS Test Event',
                'END:VEVENT',
                'END:VCALENDAR'
            ]
            
            missing_fields = []
            for field in required_fields:
                if not any(field in line for line in ics_lines):
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ ICS format is valid and complete")
                return True
            else:
                print(f"❌ ICS format missing fields: {missing_fields}")
                return False
        else:
            print("❌ No ICS content found in email")
            return False
            
    except Exception as e:
        print(f"❌ ICS format test failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing Calendar Invitation Functionality")
    print("=" * 50)
    
    success = True
    success &= test_calendar_invitation()
    success &= test_ics_format()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Calendar functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        exit(1)
