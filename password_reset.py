"""
Password Reset Functionality for SmartReminder
Handles password reset tokens and email sending
"""

import secrets
import hashlib
from datetime import datetime, timedelta
import logging
from push_service import send_password_reset_notification, send_password_reset_confirmation

logger = logging.getLogger(__name__)

def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

def create_password_reset_request(user_email, dm=None):
    """Create a password reset request for user"""
    if not dm:
        return False
        
    try:
        # Check if user exists
        users_data = dm.load_data('users')
        if user_email not in users_data:
            logger.warning(f"Password reset requested for non-existent user: {user_email}")
            return False
        
        # Generate reset token
        reset_token = generate_reset_token()
        
        # Store reset request
        reset_requests = dm.load_data('password_reset_requests')
        reset_requests[reset_token] = {
            'user_email': user_email,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
            'used': False
        }
        dm.save_data('password_reset_requests', reset_requests)
        
        # Send notification
        send_password_reset_notification(user_email, reset_token, dm)
        
        logger.info(f"Password reset request created for {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating password reset request for {user_email}: {e}")
        return False

def validate_reset_token(token, dm=None):
    """Validate a password reset token"""
    if not dm or not token:
        return None
        
    try:
        reset_requests = dm.load_data('password_reset_requests')
        request = reset_requests.get(token)
        
        if not request:
            return None
            
        # Check if token is expired
        expires_at = datetime.fromisoformat(request['expires_at'])
        if datetime.now() > expires_at:
            return None
            
        # Check if token is already used
        if request.get('used', False):
            return None
            
        return request['user_email']
        
    except Exception as e:
        logger.error(f"Error validating reset token: {e}")
        return None

def reset_user_password(token, new_password, dm=None):
    """Reset user password using valid token"""
    if not dm:
        return False
        
    try:
        user_email = validate_reset_token(token, dm)
        if not user_email:
            return False
            
        # Update user password
        users_data = dm.load_data('users')
        if user_email in users_data:
            # Hash the new password
            users_data[user_email]['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            dm.save_data('users', users_data)
            
            # Mark token as used
            reset_requests = dm.load_data('password_reset_requests')
            reset_requests[token]['used'] = True
            dm.save_data('password_reset_requests', reset_requests)
            
            # Send confirmation
            send_password_reset_confirmation(user_email, dm)
            
            logger.info(f"Password reset successful for {user_email}")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return False

def cleanup_expired_tokens(dm=None):
    """Remove expired password reset tokens"""
    if not dm:
        return
        
    try:
        reset_requests = dm.load_data('password_reset_requests')
        current_time = datetime.now()
        
        expired_tokens = []
        for token, request in reset_requests.items():
            expires_at = datetime.fromisoformat(request['expires_at'])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del reset_requests[token]
            
        if expired_tokens:
            dm.save_data('password_reset_requests', reset_requests)
            logger.info(f"Cleaned up {len(expired_tokens)} expired reset tokens")
            
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
