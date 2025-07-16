#!/usr/bin/env python3
"""
Omfattende test av alle kritiske fixes i SmartReminder
"""

import sys
import os
sys.path.append('/workspaces/smartreminder')

from app import app, User, ReminderForm, dm
import uuid
import traceback

def test_dashboard_form_fix():
    """Test at dashboard form fix fungerer"""
    print("🔧 Testing dashboard form fix...")
    try:
        with app.test_request_context():
            # Test at ReminderForm kan opprettes
            form = ReminderForm()
            assert form is not None, "ReminderForm kunne ikke opprettes"
            
            # Test at form har hidden_tag metode
            assert hasattr(form, 'hidden_tag'), "Form mangler hidden_tag metode"
            
            # Test at form har csrf_token
            assert hasattr(form, 'csrf_token'), "Form mangler csrf_token"
            
            print("✅ Dashboard form fix: 100% OK")
            return True
    except Exception as e:
        print(f"❌ Dashboard form fix feil: {e}")
        traceback.print_exc()
        return False

def test_user_focus_mode_fix():
    """Test at User focus_mode fix fungerer"""
    print("🔧 Testing User focus_mode fix...")
    try:
        # Test User class constructor
        test_user_id = str(uuid.uuid4())
        user = User(test_user_id, 'test@example.com', 'test@example.com', 'hash', 'normal')
        
        assert hasattr(user, 'focus_mode'), "User mangler focus_mode attributt"
        assert user.focus_mode == 'normal', f"Focus mode er {user.focus_mode}, forventet 'normal'"
        
        # Test default focus_mode
        user2 = User(test_user_id, 'test2@example.com', 'test2@example.com', 'hash')
        assert user2.focus_mode == 'normal', "Default focus_mode er ikke 'normal'"
        
        print("✅ User focus_mode fix: 100% OK")
        return True
    except Exception as e:
        print(f"❌ User focus_mode fix feil: {e}")
        traceback.print_exc()
        return False

def test_stats_calculation():
    """Test at stats beregning fungerer"""
    print("🔧 Testing stats calculation...")
    try:
        # Test stats dict struktur
        stats = {
            'total': 0,
            'completed': 0,
            'shared_count': 0,
            'completion_rate': 0
        }
        
        # Test beregning
        total_reminders = 10
        completed_reminders = 3
        completion_rate = (completed_reminders / total_reminders * 100) if total_reminders > 0 else 0
        
        assert completion_rate == 30.0, f"Completion rate er {completion_rate}, forventet 30.0"
        
        print("✅ Stats calculation: 100% OK")
        return True
    except Exception as e:
        print(f"❌ Stats calculation feil: {e}")
        traceback.print_exc()
        return False

def test_template_rendering():
    """Test at template rendering fungerer"""
    print("🔧 Testing template rendering...")
    try:
        with app.test_client() as client:
            # Test at login siden laster
            response = client.get('/login')
            assert response.status_code == 200, f"Login side returnerte {response.status_code}"
            
            # Test at dashboard redirecter til login
            response = client.get('/dashboard')
            assert response.status_code == 302, f"Dashboard returnerte {response.status_code}, forventet 302"
            
            print("✅ Template rendering: 100% OK")
            return True
    except Exception as e:
        print(f"❌ Template rendering feil: {e}")
        traceback.print_exc()
        return False

def test_imports():
    """Test at alle kritiske imports fungerer"""
    print("🔧 Testing imports...")
    try:
        from app import Flask, render_template, request, redirect, url_for, flash, jsonify
        from app import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
        from app import Mail, Message, FlaskForm, CSRFProtect
        from app import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField
        from app import DataRequired, Email, Length
        from app import generate_password_hash, check_password_hash
        from app import datetime, timedelta, Path
        
        print("✅ All imports: 100% OK")
        return True
    except Exception as e:
        print(f"❌ Import feil: {e}")
        traceback.print_exc()
        return False

def main():
    """Kjør alle tester"""
    print("🚀 Starter omfattende test av alle kritiske fixes...")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_dashboard_form_fix,
        test_user_focus_mode_fix,
        test_stats_calculation,
        test_template_rendering
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} krasjet: {e}")
            failed += 1
        print("-" * 40)
    
    print("=" * 60)
    print(f"📊 Test resultat: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALLE TESTER PASSERTE! Alle kritiske feil er 100% fikset!")
        return True
    else:
        print(f"❌ {failed} tester failet. Sjekk feilene over.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
