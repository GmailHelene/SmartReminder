# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'din-hemmelighets-nøkkel-her'
    
    # E-post konfigurering (Gmail eksempel)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Din Gmail-adresse
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # App-passord fra Gmail
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Påminnelse innstillinger
    NOTIFICATION_ADVANCE_MINUTES = 30  # Send varsel 30 min før
    REMINDER_CHECK_INTERVAL = 300  # Sjekk hver 5. minutt
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
