#!/usr/bin/env python
"""Script to run database migration"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from flask_migrate import upgrade

app = create_app()

with app.app_context():
    print("Running database migrations...")
    try:
        upgrade()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

