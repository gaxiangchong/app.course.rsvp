#!/usr/bin/env python3
"""
Create Admin User Script for PythonAnywhere
This script creates an admin user with a password for your EventApp.
"""

import os
import sys
import getpass

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_admin_user():
    """Create an admin user with password."""
    print("👤 Creating Admin User for EventApp")
    print("=" * 50)
    
    try:
        # Import Flask app components
        from app import app, db, User
        
        with app.app_context():
            # Check if admin user already exists
            existing_admin = User.query.filter_by(username='admin').first()
            
            if existing_admin:
                print("⚠️  Admin user already exists!")
                update = input("Do you want to update the admin password? (y/N): ").strip().lower()
                
                if update == 'y':
                    # Get new password
                    password = getpass.getpass("Enter new admin password: ")
                    if not password:
                        print("❌ Password cannot be empty!")
                        return False
                    
                    # Update password
                    existing_admin.set_password(password)
                    existing_admin.email_verified = True
                    existing_admin.membership_type = 'NA'
                    existing_admin.membership_grade = 'Pending Review'
                    db.session.commit()
                    
                    print("✅ Admin password updated successfully!")
                    print(f"   Username: admin")
                    print(f"   Email: {existing_admin.email}")
                    return True
                else:
                    print("⏸️  Admin user creation cancelled")
                    return False
            
            # Get admin details
            print("📝 Enter admin user details:")
            
            username = input("Username (default: admin): ").strip()
            if not username:
                username = 'admin'
            
            email = input("Email address: ").strip()
            if not email:
                print("❌ Email is required!")
                return False
            
            password = getpass.getpass("Password: ")
            if not password:
                print("❌ Password is required!")
                return False
            
            # Create admin user
            admin_user = User(
                username=username,
                email=email,
                is_admin=True,
                email_verified=True,
                account_status='active',
                membership_type='NA',
                membership_grade='Pending Review',
                country='Singapore'
            )
            
            # Set password
            admin_user.set_password(password)
            
            # Add to database
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n✅ Admin user created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Admin privileges: Yes")
            print(f"   Email verified: Yes")
            print(f"   Account status: Active")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    print("🔐 EventApp Admin User Setup")
    print("=" * 60)
    print("This script will create an admin user for your EventApp.")
    print("The admin user will have full access to manage events and users.")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        print("💡 Make sure you're running this from the eventapp directory")
        return
    
    if not os.path.exists('instance/eventapp.db'):
        print("❌ Database not found!")
        print("💡 Make sure the database exists. You may need to run the app first.")
        return
    
    # Create admin user
    if create_admin_user():
        print("\n🎉 Admin user setup complete!")
        print("🔄 You can now login to your EventApp with the admin credentials")
    else:
        print("\n❌ Admin user setup failed!")
        print("💡 Please check the error messages above")

if __name__ == '__main__':
    main()
