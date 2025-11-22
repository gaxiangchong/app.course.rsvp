#!/usr/bin/env python3
"""
Initialize Email Verification Setting

This script initializes the email verification setting in the database.
Run this after deploying the new settings feature to ensure the setting exists.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AppSettings

def initialize_email_verification_setting():
    """Initialize email verification setting if it doesn't exist."""
    print("=" * 60)
    print("🔧 Initialize Email Verification Setting")
    print("=" * 60)
    
    with app.app_context():
        # Check if setting exists
        setting = AppSettings.query.filter_by(key='email_verification_enabled').first()
        
        if setting:
            print(f"✅ Setting already exists:")
            print(f"   Key: {setting.key}")
            print(f"   Value: {setting.value}")
            print(f"   Description: {setting.description}")
            print(f"   Last Updated: {setting.updated_at}")
        else:
            # Create default setting (enabled by default)
            AppSettings.set_bool_setting(
                'email_verification_enabled',
                True,  # Default to enabled
                'Enable or disable email verification requirement for new registrations'
            )
            print("✅ Created email verification setting (default: enabled)")
        
        print("\n📋 Current Settings:")
        all_settings = AppSettings.query.all()
        if all_settings:
            for s in all_settings:
                print(f"   • {s.key}: {s.value} ({s.description or 'No description'})")
        else:
            print("   No settings found")
        
        print("\n" + "=" * 60)
        print("✅ Initialization complete!")
        print("=" * 60)

if __name__ == "__main__":
    initialize_email_verification_setting()

