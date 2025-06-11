import os
from pathlib import Path
from dotenv import load_dotenv

# Last miljøvariabler
load_dotenv()

class Config:
    # Sikkerhet
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production-please'
    WTF_CSRF_ENABLED = True
    
    # Database/Data
    DATA_DIR = Path('data')
    DATA_DIR.mkdir(exist_ok=True)
    
    # E-post konfigurasjon
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # App-innstillinger
    REMINDER_CHECK_INTERVAL = int(os.environ.get('REMINDER_CHECK_INTERVAL') or 300)  # 5 minutter
    NOTIFICATION_ADVANCE_MINUTES = int(os.environ.get('NOTIFICATION_ADVANCE_MINUTES') or 15)  # 15 minutter før

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SUPPRESS_SEND = False  # Sett til True for å ikke sende e-post i utvikling

class ProductionConfig(Config):
    DEBUG = False
    # Legg til SSL/sikkerhet for produksjon
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutter

# Velg konfigurasjon basert på miljø
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}