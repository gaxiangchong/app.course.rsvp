# 🚀 Complete Deployment Guide - Noble Quest Event App

## 📋 Pre-Deployment Checklist

### 1. **Code Changes Summary**
- ✅ Added CarouselImage model and admin management
- ✅ Added meal option fields to Event model
- ✅ Added meal_opt_in field to RSVP model  
- ✅ Updated templates for meal pricing and Pay at Venue
- ✅ Enhanced payment logic for total cost calculation
- ✅ Added version information to profile page

### 2. **Database Migration Required**
- New columns need to be added to existing tables
- Migration script: `migrate_event_meal_pay_options.py`

---

## 🗄️ Database Migration Steps

### Step 1: Backup Your Database
```bash
# Create backup before migration
cp instance/app.db instance/app_backup_$(date +%Y%m%d_%H%M%S).db
```

### Step 2: Run Database Migration
```bash
# Navigate to your app directory
cd /path/to/your/eventapp

# Run the migration script
python migrate_event_meal_pay_options.py
```

**Expected Output:**
```
==================================================
🍽️  Event/RSVP Meal & Pay Options Migration
==================================================
🔄 Starting migration: add meal/pay options to Event and RSVP tables...
📝 Adding column event.meal_option_enabled ...
📝 Adding column event.meal_option_remarks ...
📝 Adding column event.meal_option_price ...
📝 Adding column event.pay_at_venue_enabled ...
📝 Adding column rsvp.meal_opt_in ...
🎉 Migration completed successfully!

Next steps:
1) Restart your Flask app
2) Re-test updating events and submitting RSVPs
==================================================
```

### Step 3: Verify Migration
```bash
# Check if columns were added successfully
sqlite3 instance/app.db ".schema event"
sqlite3 instance/app.db ".schema rsvp"
```

---

## 🚀 Deployment Steps

### Step 1: Update Code on Server
```bash
# SSH into your server
ssh your-username@your-server.com

# Navigate to your app directory
cd /path/to/your/eventapp

# Pull latest changes
git pull origin main

# Or if you're uploading files manually:
# Upload all modified files to the server
```

### Step 2: Install Dependencies (if needed)
```bash
# Activate virtual environment
source venv/bin/activate  # or your virtual env path

# Install any new dependencies
pip install -r requirements.txt
```

### Step 3: Run Database Migration
```bash
# Make sure you're in the app directory
cd /path/to/your/eventapp

# Run the migration
python migrate_event_meal_pay_options.py
```

### Step 4: Update WSGI Configuration (if needed)
```bash
# Check your WSGI file (usually wsgi.py or wsgi_event_mynoblequest.py)
# Ensure it points to the correct app instance
```

### Step 5: Restart Web Server
```bash
# For PythonAnywhere:
# Go to Web tab → Reload button

# For other servers:
sudo systemctl restart your-app-name
# or
sudo service nginx restart
# or
sudo service apache2 restart
```

---

## 🧪 Post-Deployment Testing

### 1. **Test Database Migration**
- [ ] Check that new columns exist in database
- [ ] Verify no errors in application logs

### 2. **Test New Features**
- [ ] **Carousel Management**: Go to `/admin/carousel`
- [ ] **Meal Options**: Update an event with meal options
- [ ] **Pay at Venue**: Test RSVP with Pay at Venue option
- [ ] **Meal Pricing**: Test total cost calculation

### 3. **Test Existing Features**
- [ ] User registration/login
- [ ] Event creation/editing
- [ ] RSVP functionality
- [ ] Payment processing
- [ ] Admin functions

---

## 🔧 Troubleshooting

### If Migration Fails:
```bash
# Check database permissions
ls -la instance/app.db

# Check if database is locked
lsof instance/app.db

# Restart application if needed
```

### If New Features Don't Work:
1. **Check Logs**: Look for error messages
2. **Verify Migration**: Ensure all columns were added
3. **Clear Cache**: Restart web server
4. **Check Permissions**: Ensure app can write to database

### Common Issues:
- **Column already exists**: Migration will skip existing columns
- **Permission denied**: Check file permissions
- **Database locked**: Stop app, run migration, restart app

---

## 📝 Deployment Checklist

### Before Deployment:
- [ ] Code changes committed to git
- [ ] Database backup created
- [ ] Migration script tested locally
- [ ] All new files uploaded to server

### During Deployment:
- [ ] Database migration completed successfully
- [ ] Web server restarted
- [ ] No error messages in logs

### After Deployment:
- [ ] All new features working
- [ ] Existing features still working
- [ ] Admin can access carousel management
- [ ] Users can select meal options
- [ ] Pay at Venue option appears
- [ ] Version info shows in profile

---

## 🆘 Rollback Plan (If Needed)

### If Issues Occur:
```bash
# 1. Restore database backup
cp instance/app_backup_YYYYMMDD_HHMMSS.db instance/app.db

# 2. Revert code changes
git checkout previous-commit-hash

# 3. Restart web server
# (Restart your web server)
```

---

## 📞 Support Information

### Files Modified:
- `app.py` - Added new models and routes
- `templates/update_event.html` - Added meal option fields
- `templates/event_detail.html` - Enhanced RSVP form
- `templates/profile.html` - Added version info
- `migrate_event_meal_pay_options.py` - New migration script

### New Features Added:
1. **Carousel Management System**
2. **Meal Option Pricing**
3. **Pay at Venue Option**
4. **Enhanced RSVP System**
5. **Version Information Display**

---

## ✅ Success Criteria

Deployment is successful when:
- [ ] All new features are accessible
- [ ] Database migration completed without errors
- [ ] Existing functionality remains intact
- [ ] Admin can manage carousel images
- [ ] Users can opt-in for meals with pricing
- [ ] Pay at Venue option works correctly
- [ ] Version information displays properly

**🎉 Your Noble Quest Event App is now ready with enhanced features!**
