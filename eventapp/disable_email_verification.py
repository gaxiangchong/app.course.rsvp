#!/usr/bin/env python3
"""
Temporary Email Verification Disable
This script temporarily disables email verification so you can use the app.
"""

import os
import shutil
from datetime import datetime

def backup_current_config():
    """Backup current configuration."""
    if os.path.exists('.env'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f'.env.backup_{timestamp}'
        shutil.copy2('.env', backup_name)
        print(f"✅ Backed up current config to: {backup_name}")
        return backup_name
    return None

def create_no_email_config():
    """Create configuration without email verification."""
    config = """# EventApp Environment Configuration
# Temporary configuration without email verification

# Flask Configuration
SECRET_KEY=ff51f8a92aaa245c385f100331f943ed1dd42a2726d4546578ef5f787a980635
FLASK_ENV=development
DATABASE_URL=sqlite:///eventapp.db

# Email Configuration (Disabled)
MAIL_SERVER=
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=

# App Configuration
APP_NAME=EventApp
"""
    
    with open('.env', 'w') as f:
        f.write(config)
    
    print("✅ Created configuration without email verification")

def update_app_for_no_email():
    """Update app.py to skip email verification."""
    print("📝 Updating app.py to skip email verification...")
    
    # Read current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = False
    
    # 1. Update registration to skip email verification
    old_registration_code = """        # Send verification email
        if send_verification_email(user):
            flash('Registration successful! Please check your email to verify your account before logging in.', 'success')
        else:
            flash('Registration successful, but failed to send verification email. Please contact support.', 'warning')
        
        return redirect(url_for('resend_verification'))"""
    
    new_registration_code = """        # Skip email verification for now
        user.email_verified = True
        flash('Registration successful! You can now log in.', 'success')
        
        return redirect(url_for('login'))"""
    
    if old_registration_code in content:
        content = content.replace(old_registration_code, new_registration_code)
        changes_made = True
        print("✅ Updated registration to skip email verification")
    else:
        print("⚠️ Could not find registration email verification code to replace")
    
    # 2. Disable the check_email_verification middleware
    old_middleware_code = """@app.before_request
def check_email_verification():
    \"\"\"Check if logged-in user has verified their email.\"\"\"
    if current_user.is_authenticated and not current_user.email_verified:
        # Allow users with default passwords to bypass email verification
        if current_user.has_default_password:
            # Skip email verification for users with default passwords
            pass
        else:
            # Allow access to verification-related routes
            if request.endpoint in ['verify_email', 'resend_verification', 'logout']:
                return
            # Redirect to verification page for other routes
            flash('Please verify your email address to continue using your account.', 'warning')
            return redirect(url_for('resend_verification'))"""
    
    new_middleware_code = """@app.before_request
def check_email_verification():
    \"\"\"Check if logged-in user has verified their email.\"\"\"
    # Email verification temporarily disabled
    pass"""
    
    if old_middleware_code in content:
        content = content.replace(old_middleware_code, new_middleware_code)
        changes_made = True
        print("✅ Disabled email verification middleware")
    else:
        print("⚠️ Could not find email verification middleware to disable")
    
    # 3. Update login to skip email verification check
    # Look for the login check
    old_login_check = """            # Check if email is verified (only for users without default passwords)
            if not user.email_verified:
                flash('Please verify your email address before logging in. Check your email for a verification link.', 'warning')
                return redirect(url_for('resend_verification'))"""
    
    new_login_check = """            # Email verification check disabled
            # Auto-verify email for login
            if not user.email_verified:
                user.email_verified = True
                db.session.commit()"""
    
    if old_login_check in content:
        content = content.replace(old_login_check, new_login_check)
        changes_made = True
        print("✅ Updated login to skip email verification check")
    else:
        print("⚠️ Could not find login email verification check to replace")
    
    if changes_made:
        # Write updated content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated app.py to skip email verification")
        return True
    else:
        print("⚠️ No changes were made to app.py")
        return False

def main():
    print("=" * 60)
    print("🔧 Temporary Email Verification Disable")
    print("=" * 60)
    
    print("\n⚠️ This will temporarily disable email verification so you can use the app.")
    print("You can re-enable it later when email is working.")
    
    confirm = input("\nDo you want to proceed? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Operation cancelled.")
        return False
    
    # Backup current config
    backup_file = backup_current_config()
    
    # Create no-email config
    create_no_email_config()
    
    # Update app.py
    success = update_app_for_no_email()
    
    if success:
        print("\n🎉 Email verification temporarily disabled!")
        print("\n📋 What this means:")
        print("• New users can register without email verification")
        print("• All users are automatically verified")
        print("• You can use the app normally")
        print("• Email features are disabled")
        
        print("\n🔄 To re-enable email verification later:")
        print(f"• Restore config: copy {backup_file} to .env")
        print("• Fix email configuration")
        print("• Restart the app")
        
        return True
    else:
        print("\n❌ Failed to update app.py")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Setup complete! Restart your Flask app to apply changes.")
        print("📱 You can now register users without email verification.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    print("=" * 60)
