# 🚀 PythonAnywhere Deployment Guide - Noble Quest Event App

## 📋 Pre-Deployment Checklist

### ✅ **Files to Upload to PythonAnywhere:**
- All modified Python files (`app.py`)
- All modified templates (`templates/update_event.html`, `templates/event_detail.html`, `templates/profile.html`)
- New migration script (`migrate_event_meal_pay_options.py`)
- New carousel template (`templates/admin_carousel.html`)
- All existing files (templates, static files, etc.)

---

## 🚀 Step-by-Step PythonAnywhere Deployment

### **Step 1: Upload Files to PythonAnywhere**

#### **Option A: Using Git (Recommended)**
```bash
# If you have your code in a Git repository:
# 1. Push your changes to GitHub/GitLab
git add .
git commit -m "Add carousel management, meal options, and Pay at Venue features"
git push origin main

# 2. On PythonAnywhere, pull the changes:
cd /home/yourusername/mysite
git pull origin main
```

#### **Option B: Manual Upload**
1. **Go to PythonAnywhere Files tab**
2. **Navigate to your app directory** (usually `/home/yourusername/mysite/`)
3. **Upload all modified files:**
   - `app.py`
   - `templates/update_event.html`
   - `templates/event_detail.html`
   - `templates/profile.html`
   - `templates/admin_carousel.html`
   - `migrate_event_meal_pay_options.py`

### **Step 2: Run Database Migration**

#### **Open PythonAnywhere Console:**
1. Go to **Consoles** tab
2. Click **Bash** to open a new console
3. Navigate to your app directory:
```bash
cd /home/yourusername/mysite
```

#### **Run the Migration:**
```bash
# Make sure you're in the right directory
ls -la  # Should see your app files

# Run the migration script
python3.10 migrate_event_meal_pay_options.py
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

### **Step 3: Update WSGI Configuration (if needed)**

#### **Check your WSGI file:**
1. Go to **Web** tab in PythonAnywhere
2. Click on your WSGI configuration file
3. Ensure it points to your app correctly:

```python
# Example WSGI configuration
import sys
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### **Step 4: Reload Your Web App**

#### **Reload the Application:**
1. Go to **Web** tab
2. Click the **Reload** button (green button)
3. Wait for the reload to complete
4. Check for any error messages

### **Step 5: Test Your Deployment**

#### **Test New Features:**

1. **Visit your app URL** (e.g., `https://yourusername.pythonanywhere.com`)

2. **Test Carousel Management:**
   - Login as admin
   - Go to `/admin/carousel`
   - Try adding a carousel image
   - Check if carousel appears on homepage

3. **Test Meal Options:**
   - Go to an existing event
   - Click "Edit Event"
   - Enable meal option
   - Set meal price and remarks
   - Save the event

4. **Test RSVP with New Features:**
   - Go to event detail page
   - Try RSVP with meal opt-in
   - Test "Pay at Venue" option
   - Verify total cost calculation

5. **Test Version Information:**
   - Go to Profile page
   - Check if version info appears in sidebar

---

## 🔧 Troubleshooting Common Issues

### **Issue 1: Migration Fails**
```bash
# Check if database exists
ls -la instance/

# Check database permissions
ls -la instance/app.db

# If database is locked, restart the web app first
```

### **Issue 2: Import Errors**
```bash
# Check if all files are uploaded correctly
ls -la templates/
ls -la *.py

# Verify file permissions
chmod 644 *.py
chmod 644 templates/*.html
```

### **Issue 3: Template Not Found**
- Ensure all template files are in `templates/` directory
- Check file names match exactly (case-sensitive)
- Verify file permissions

### **Issue 4: Database Connection Issues**
```bash
# Check database file
sqlite3 instance/app.db ".tables"

# Verify migration completed
sqlite3 instance/app.db ".schema event"
sqlite3 instance/app.db ".schema rsvp"
```

---

## 📋 Post-Deployment Verification

### **✅ Checklist:**
- [ ] **Homepage loads** without errors
- [ ] **Carousel appears** on homepage (if images added)
- [ ] **Admin can access** `/admin/carousel`
- [ ] **Event update form** shows meal option fields
- [ ] **RSVP form** shows meal opt-in checkbox
- [ ] **Pay at Venue** option appears for events
- [ ] **Profile page** shows version information
- [ ] **Existing features** still work (login, RSVP, etc.)

### **🧪 Test Scenarios:**

#### **Scenario 1: Admin Carousel Management**
1. Login as admin
2. Go to `/admin/carousel`
3. Add a promotional image
4. Check if it appears on homepage carousel

#### **Scenario 2: Event with Meal Options**
1. Create or edit an event
2. Enable meal option
3. Set meal price (e.g., $5.00)
4. Add meal remarks
5. Save event

#### **Scenario 3: User RSVP with Meal**
1. Go to event detail page
2. Select "Accept" for RSVP
3. Check "I would like to opt-in for the meal"
4. Select "Pay at Venue" or "Pay by Credit"
5. Submit RSVP
6. Verify total cost includes meal price

---

## 🆘 Rollback Plan (If Needed)

### **If Deployment Fails:**
1. **Restore Database:**
```bash
# If you have a backup
cp instance/app_backup_*.db instance/app.db
```

2. **Revert Code:**
```bash
# If using Git
git checkout previous-commit-hash
```

3. **Reload Web App:**
   - Go to Web tab
   - Click Reload button

---

## 📞 Support Information

### **PythonAnywhere Specific Notes:**
- **File Path**: Usually `/home/yourusername/mysite/`
- **WSGI File**: Usually `wsgi.py` or `wsgi_event_mynoblequest.py`
- **Static Files**: Should be in `static/` directory
- **Templates**: Should be in `templates/` directory

### **Common PythonAnywhere Issues:**
- **File Permissions**: Ensure files are readable (644)
- **Database Location**: Usually in `instance/app.db`
- **Console Access**: Use Bash console for commands
- **Web App Reload**: Always reload after code changes

---

## ✅ Success Criteria

**Deployment is successful when:**
- [ ] All new features are accessible
- [ ] Database migration completed without errors
- [ ] Existing functionality remains intact
- [ ] Admin can manage carousel images
- [ ] Users can opt-in for meals with pricing
- [ ] Pay at Venue option works correctly
- [ ] Version information displays properly
- [ ] No error messages in PythonAnywhere logs

**🎉 Your Noble Quest Event App is now live on PythonAnywhere with enhanced features!**
