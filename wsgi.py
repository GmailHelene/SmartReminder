"""
WSGI entry point for production deployment
"""

import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

try:
    from app import app as application
except ImportError as e:
    print(f"Import error: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port)
