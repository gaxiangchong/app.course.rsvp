#!/bin/bash

# 🚀 Noble Quest Event App - Complete Deployment Script
# This script handles the full deployment including database migration

echo "🚀 Starting Noble Quest Event App Deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Backup Database
print_status "Creating database backup..."
if [ -f "instance/app.db" ]; then
    cp instance/app.db instance/app_backup_$(date +%Y%m%d_%H%M%S).db
    print_success "Database backup created successfully"
else
    print_warning "No existing database found - this might be a fresh installation"
fi

# Step 2: Check Python Environment
print_status "Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found! Please install Python first."
    exit 1
fi
print_success "Python found: $PYTHON_CMD"

# Step 3: Install Dependencies
print_status "Installing/updating dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed successfully"
else
    print_warning "No requirements.txt found - skipping dependency installation"
fi

# Step 4: Run Database Migration
print_status "Running database migration..."
if [ -f "migrate_event_meal_pay_options.py" ]; then
    $PYTHON_CMD migrate_event_meal_pay_options.py
    if [ $? -eq 0 ]; then
        print_success "Database migration completed successfully"
    else
        print_error "Database migration failed! Please check the error messages above."
        exit 1
    fi
else
    print_error "Migration script not found! Please ensure migrate_event_meal_pay_options.py exists."
    exit 1
fi

# Step 5: Test Application
print_status "Testing application startup..."
$PYTHON_CMD -c "
import sys
sys.path.append('.')
try:
    from app import app, db
    with app.app_context():
        # Test database connection
        db.engine.execute('SELECT 1')
    print('✅ Application test passed')
except Exception as e:
    print(f'❌ Application test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Application test passed"
else
    print_error "Application test failed! Please check the error messages above."
    exit 1
fi

# Step 6: Set Permissions
print_status "Setting file permissions..."
chmod +x *.py
chmod 644 *.html
chmod 644 *.md
print_success "File permissions set"

# Step 7: Final Checks
print_status "Running final deployment checks..."

# Check if all required files exist
REQUIRED_FILES=(
    "app.py"
    "migrate_event_meal_pay_options.py"
    "templates/update_event.html"
    "templates/event_detail.html"
    "templates/profile.html"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file exists"
    else
        print_error "✗ $file missing!"
        exit 1
    fi
done

# Step 8: Deployment Summary
echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=================================================="
print_success "Database migration: ✅ Completed"
print_success "Dependencies: ✅ Installed"
print_success "Application test: ✅ Passed"
print_success "File permissions: ✅ Set"
print_success "All required files: ✅ Present"

echo ""
echo "📋 Next Steps:"
echo "1. Restart your web server (PythonAnywhere: Web tab → Reload)"
echo "2. Test the new features:"
echo "   - Go to /admin/carousel to manage carousel images"
echo "   - Update an event to add meal options"
echo "   - Test RSVP with meal opt-in and Pay at Venue"
echo "3. Check the profile page for version information"

echo ""
echo "🔧 If you encounter issues:"
echo "- Check application logs for error messages"
echo "- Verify database migration completed successfully"
echo "- Ensure all file permissions are correct"
echo "- Restart your web server"

echo ""
print_success "🚀 Noble Quest Event App is ready with enhanced features!"
echo "=================================================="
