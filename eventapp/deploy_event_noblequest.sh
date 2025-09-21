#!/bin/bash
# Deployment script for event.noblequest.com

echo "🚀 Starting EventApp deployment for event.noblequest.com..."

# Navigate to the project directory
cd /home/rsvp13/app.course.rsvp/eventapp

# Pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python migrate_country_code.py

# Create database tables (ensures all tables and new columns are present)
echo "🗄️ Updating database schema..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Set environment variables for the new domain
export SERVER_NAME=event.noblequest.com
export APPLICATION_ROOT=/
export DOMAIN=event.noblequest.com
export BASE_URL=https://event.noblequest.com

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at https://event.noblequest.com"
echo "🔄 Please reload your web app in PythonAnywhere dashboard"
