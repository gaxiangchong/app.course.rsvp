#!/usr/bin/env python3
"""
Admin user setup script for EventApp.

This script creates an admin user for the application.
Run this script after setting up the database.
"""

import os
import sys
from getpass import getpass

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_admin_user():
    """Create an admin user interactively."""
    print("EventApp Admin User Setup")
    print("=" * 30)
    
    # Check if admin already exists
    with app.app_context():
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username} ({existing_admin.email})")
            response = input("Do you want to create another admin user? (y/N): ")
            if response.lower() != 'y':
                print("Exiting...")
                return
    
    # Get admin details
    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    email = input("Enter admin email: ").strip().lower()
    if not email:
        print("Email cannot be empty!")
        return
    
    # Validate email format
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        print("Invalid email format!")
        return
    
    # Check if email already exists
    with app.app_context():
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return
    
    password = getpass("Enter admin password: ")
    if len(password) < 6:
        print("Password must be at least 6 characters long!")
        return
    
    confirm_password = getpass("Confirm admin password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    # Create admin user
    try:
        with app.app_context():
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                email_notifications=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            print(f"\n✅ Admin user created successfully!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Admin privileges: Yes")
            print("\nYou can now log in and create events.")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return

def list_users():
    """List all users in the system."""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the system.")
            return
        
        print("\nCurrent Users:")
        print("-" * 50)
        for user in users:
            admin_status = "Admin" if user.is_admin else "User"
            print(f"{user.username} ({user.email}) - {admin_status}")

def main():
    """Main function."""
    print("EventApp Setup Utility")
    print("=" * 20)
    print("1. Create admin user")
    print("2. List all users")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            create_admin_user()
            break
        elif choice == '2':
            list_users()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == '__main__':
    main()
