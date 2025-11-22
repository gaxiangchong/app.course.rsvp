# Email Verification Toggle Feature

## Overview

This feature allows administrators to enable or disable email verification directly from the admin members page, without needing to redeploy code or modify configuration files.

## Features

- ✅ **Runtime Toggle**: Enable/disable email verification without code changes
- ✅ **Database Storage**: Settings stored in database for persistence
- ✅ **Admin Only**: Protected by superuser password authentication
- ✅ **Immediate Effect**: Changes take effect immediately
- ✅ **User-Friendly UI**: Simple toggle switch in admin members page

## How It Works

### Database Model

A new `AppSettings` model stores application-wide settings:
- `key`: Unique setting identifier
- `value`: Setting value (stored as string)
- `description`: Human-readable description
- `updated_at`: Last modification timestamp

### Settings Location

The email verification toggle is located in the **Admin Members** page (`/admin/members`), in a new "Application Settings" section at the top of the page.

### How to Use

1. **Navigate to Admin Members Page**
   - Log in as an administrator
   - Go to `/admin/members`

2. **Find Application Settings Section**
   - Located at the top, before the membership statistics
   - Shows current status (Enabled/Disabled)

3. **Toggle Email Verification**
   - Check/uncheck the "Email Verification" toggle
   - Enter superuser password for security
   - Click "Save Settings"

4. **Changes Take Effect Immediately**
   - New registrations will follow the new setting
   - Existing unverified users can log in if disabled
   - No server restart required

## Technical Implementation

### Files Modified

1. **`app.py`**
   - Added `AppSettings` database model
   - Updated `check_email_verification()` middleware to check setting
   - Updated registration route to check setting
   - Updated login route to check setting
   - Added `/admin/settings/email-verification` route
   - Updated `admin_members()` route to pass setting to template
   - Updated `create_tables()` to initialize default setting

2. **`templates/admin_members.html`**
   - Added "Application Settings" section
   - Added email verification toggle switch
   - Added superuser password field
   - Added form submission handling

### Database Changes

New table: `app_settings`
```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value VARCHAR(500) NOT NULL,
    description VARCHAR(200),
    updated_at DATETIME
);
```

### Default Behavior

- **Default Setting**: Email verification is **enabled** by default
- **Initialization**: Setting is automatically created when tables are created
- **Migration**: Run `initialize_email_verification_setting.py` for existing databases

## Behavior When Disabled

When email verification is **disabled**:
- ✅ New users are automatically verified upon registration
- ✅ Users can log in immediately after registration
- ✅ No verification emails are sent
- ✅ No email verification checks during login
- ✅ No redirects to verification pages

When email verification is **enabled**:
- ✅ New users must verify email before logging in
- ✅ Verification emails are sent automatically
- ✅ Users are redirected to verification page if not verified
- ✅ Standard email verification flow applies

## Security

- **Superuser Password Required**: Changing settings requires superuser password
- **Admin Only**: Only administrators can access the settings
- **Audit Trail**: Settings include `updated_at` timestamp for tracking changes

## Migration for Existing Deployments

If you have an existing deployment:

1. **Deploy the code changes** (new model and routes)

2. **Run the initialization script**:
   ```bash
   python initialize_email_verification_setting.py
   ```

3. **Or manually initialize** (if script doesn't work):
   ```python
   from app import app, db, AppSettings
   with app.app_context():
       AppSettings.set_bool_setting('email_verification_enabled', True)
   ```

## Future Enhancements

The `AppSettings` model can be extended to support other application settings:
- Maintenance mode toggle
- Registration open/closed
- Feature flags
- System-wide configurations

## Troubleshooting

### Setting Not Showing
- Ensure you're logged in as an administrator
- Check that the `AppSettings` table exists in the database
- Run `initialize_email_verification_setting.py` to create the setting

### Changes Not Taking Effect
- Clear browser cache
- Check that the setting was saved in the database
- Verify the setting value in the database directly

### Superuser Password Not Working
- Check the `SUPERUSER_PASSWORD` environment variable
- Default password: `TXGF#813193` (if not set in environment)

## Testing

To test the feature:

1. **Enable Email Verification**
   - Toggle ON
   - Register a new user
   - Verify that verification email is required

2. **Disable Email Verification**
   - Toggle OFF
   - Register a new user
   - Verify that user can log in immediately

3. **Toggle Back and Forth**
   - Verify changes take effect immediately
   - Check that existing users are not affected

---

**✅ Feature Complete!** You can now manage email verification from the admin interface without redeploying code.

