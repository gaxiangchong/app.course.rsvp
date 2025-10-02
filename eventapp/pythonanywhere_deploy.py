#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script for Noble Quest Event App
Run this script in PythonAnywhere console after uploading files
"""

import os
import sys
import subprocess
from datetime import datetime

def print_status(message):
    print(f"🔧 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def main():
    print("🚀 Noble Quest Event App - PythonAnywhere Deployment")
    print("=" * 60)
    
    # Step 1: Check current directory
    print_status("Checking current directory...")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print_error("app.py not found! Please run this script from your app directory.")
        print("Expected location: /home/yourusername/mysite/")
        return False
    
    print_success("Found app.py - correct directory")
    
    # Step 2: Check required files
    print_status("Checking required files...")
    required_files = [
        'app.py',
        'migrate_event_meal_pay_options.py',
        'templates/update_event.html',
        'templates/event_detail.html',
        'templates/profile.html',
        'templates/admin_carousel.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print_error("Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print_success("All required files present")
    
    # Step 3: Backup database
    print_status("Creating database backup...")
    if os.path.exists('instance/app.db'):
        backup_name = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            import shutil
            shutil.copy2('instance/app.db', backup_name)
            print_success(f"Database backup created: {backup_name}")
        except Exception as e:
            print_warning(f"Could not create backup: {e}")
    else:
        print_warning("No existing database found - this might be a fresh installation")
    
    # Step 4: Run migration
    print_status("Running database migration...")
    try:
        result = subprocess.run([sys.executable, 'migrate_event_meal_pay_options.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print_success("Database migration completed successfully")
            print("Migration output:")
            print(result.stdout)
        else:
            print_error("Database migration failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Migration timed out - this might indicate a database lock")
        return False
    except Exception as e:
        print_error(f"Migration failed with error: {e}")
        return False
    
    # Step 5: Test application
    print_status("Testing application...")
    try:
        # Test import
        sys.path.insert(0, '.')
        from app import app, db
        
        # Test database connection
        with app.app_context():
            db.engine.execute('SELECT 1')
        
        print_success("Application test passed")
        
    except Exception as e:
        print_error(f"Application test failed: {e}")
        return False
    
    # Step 6: Final checks
    print_status("Running final checks...")
    
    # Check if new columns exist
    try:
        with app.app_context():
            # Check event table
            result = db.engine.execute("PRAGMA table_info(event)")
            columns = [row[1] for row in result.fetchall()]
            
            new_columns = ['meal_option_enabled', 'meal_option_remarks', 'meal_option_price', 'pay_at_venue_enabled']
            missing_columns = [col for col in new_columns if col not in columns]
            
            if missing_columns:
                print_error(f"Missing columns in event table: {missing_columns}")
                return False
            
            # Check rsvp table
            result = db.engine.execute("PRAGMA table_info(rsvp)")
            columns = [row[1] for row in result.fetchall()]
            
            if 'meal_opt_in' not in columns:
                print_error("Missing column 'meal_opt_in' in rsvp table")
                return False
            
            print_success("All new database columns present")
            
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return False
    
    # Step 7: Deployment summary
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print_success("Database migration: ✅ Completed")
    print_success("Application test: ✅ Passed")
    print_success("Database verification: ✅ Passed")
    print_success("All required files: ✅ Present")
    
    print("\n📋 Next Steps:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click the 'Reload' button")
    print("3. Test your app at your PythonAnywhere URL")
    print("4. Test new features:")
    print("   - Admin: /admin/carousel")
    print("   - Event updates with meal options")
    print("   - RSVP with meal opt-in and Pay at Venue")
    
    print("\n🔧 If you encounter issues:")
    print("- Check PythonAnywhere error logs")
    print("- Verify all files are uploaded correctly")
    print("- Ensure database migration completed")
    print("- Try reloading the web app again")
    
    print("\n🚀 Your Noble Quest Event App is ready!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Deployment failed! Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n✅ Deployment completed successfully!")
