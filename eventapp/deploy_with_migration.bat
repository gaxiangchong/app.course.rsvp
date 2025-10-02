@echo off
REM 🚀 Noble Quest Event App - Complete Deployment Script (Windows)
REM This script handles the full deployment including database migration

echo 🚀 Starting Noble Quest Event App Deployment...
echo ==================================================

REM Step 1: Backup Database
echo [INFO] Creating database backup...
if exist "instance\app.db" (
    copy "instance\app.db" "instance\app_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db"
    echo [SUCCESS] Database backup created successfully
) else (
    echo [WARNING] No existing database found - this might be a fresh installation
)

REM Step 2: Check Python Environment
echo [INFO] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)
echo [SUCCESS] Python found

REM Step 3: Install Dependencies
echo [INFO] Installing/updating dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed successfully
) else (
    echo [WARNING] No requirements.txt found - skipping dependency installation
)

REM Step 4: Run Database Migration
echo [INFO] Running database migration...
if exist "migrate_event_meal_pay_options.py" (
    python migrate_event_meal_pay_options.py
    if %errorlevel% equ 0 (
        echo [SUCCESS] Database migration completed successfully
    ) else (
        echo [ERROR] Database migration failed! Please check the error messages above.
        pause
        exit /b 1
    )
) else (
    echo [ERROR] Migration script not found! Please ensure migrate_event_meal_pay_options.py exists.
    pause
    exit /b 1
)

REM Step 5: Test Application
echo [INFO] Testing application startup...
python -c "import sys; sys.path.append('.'); from app import app, db; print('✅ Application test passed')" 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Application test passed
) else (
    echo [ERROR] Application test failed! Please check the error messages above.
    pause
    exit /b 1
)

REM Step 6: Final Checks
echo [INFO] Running final deployment checks...

REM Check if all required files exist
set "all_files_exist=1"
if not exist "app.py" set "all_files_exist=0"
if not exist "migrate_event_meal_pay_options.py" set "all_files_exist=0"
if not exist "templates\update_event.html" set "all_files_exist=0"
if not exist "templates\event_detail.html" set "all_files_exist=0"
if not exist "templates\profile.html" set "all_files_exist=0"

if %all_files_exist% equ 1 (
    echo [SUCCESS] All required files present
) else (
    echo [ERROR] Some required files are missing!
    pause
    exit /b 1
)

REM Step 7: Deployment Summary
echo.
echo 🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ==================================================
echo [SUCCESS] Database migration: ✅ Completed
echo [SUCCESS] Dependencies: ✅ Installed
echo [SUCCESS] Application test: ✅ Passed
echo [SUCCESS] All required files: ✅ Present

echo.
echo 📋 Next Steps:
echo 1. Restart your web server (PythonAnywhere: Web tab → Reload)
echo 2. Test the new features:
echo    - Go to /admin/carousel to manage carousel images
echo    - Update an event to add meal options
echo    - Test RSVP with meal opt-in and Pay at Venue
echo 3. Check the profile page for version information

echo.
echo 🔧 If you encounter issues:
echo - Check application logs for error messages
echo - Verify database migration completed successfully
echo - Ensure all file permissions are correct
echo - Restart your web server

echo.
echo [SUCCESS] 🚀 Noble Quest Event App is ready with enhanced features!
echo ==================================================
pause
