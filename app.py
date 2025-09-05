"""
Flask RSVP event application

This application implements comprehensive event management features including:
- User registration and authentication
- Event creation and management
- RSVP responses with guest tracking
- QR code generation and verification
- Email notifications
- Analytics and reporting
- Admin dashboard
- Security best practices

Designed for deployment on PythonAnywhere with minimal external dependencies.
"""

import base64
import io
import os
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for, jsonify)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

import qrcode

# Load environment variables
try:
    load_dotenv()
except:
    pass  # Continue without .env file for local testing


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'replace-with-a-secure-random-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///eventapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    """Represents a registered user.

    Attributes:
        id (int): primary key.
        first_name (str): user's first name.
        last_name (str): user's last name.
        username (str): display name.
        email (str): unique email address.
        password_hash (str): hashed password.
        phone (str): phone number (optional).
        timezone (str): user's timezone.
        locale (str): user's locale preference.
        country (str): user's country.
        city (str): user's city.
        avatar_url (str): URL to user's avatar image.
        is_admin (bool): True if user is an administrator/organiser.
        email_notifications (bool): Whether user wants email notifications.
        push_notifications (bool): Whether user wants push notifications.
        sms_notifications (bool): Whether user wants SMS notifications.
        time_format_24h (bool): Whether user prefers 24-hour time format.
        privacy_show_city (bool): Whether to show city in public profile.
        privacy_show_full_name (bool): Whether to show full name in public profile.
        account_status (str): Account status (active/suspended).
        email_verified (bool): Whether email is verified.
        created_at (datetime): Account creation timestamp.
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    locale = db.Column(db.String(10), default='en')
    country = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    time_format_24h = db.Column(db.Boolean, default=False)
    privacy_show_city = db.Column(db.Boolean, default=True)
    privacy_show_full_name = db.Column(db.Boolean, default=True)
    account_status = db.Column(db.String(20), default='active')
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship('Event', backref='creator', lazy=True)
    rsvps = db.relationship('RSVP', backref='attendee', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def validate_email(self) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None

    @property
    def full_name(self) -> str:
        """Return full name if available, otherwise username."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def display_name(self) -> str:
        """Return display name based on privacy settings."""
        if self.privacy_show_full_name and self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class Event(db.Model):
    """Represents an event created by an organiser.

    Attributes:
        id (int): primary key.
        name (str): event name.
        description (str): event objective/description (markdown supported).
        start_date (datetime): event start date and time.
        end_date (datetime): event end date and time.
        timezone (str): event timezone.
        location (str): venue address or location.
        city (str): event city.
        country (str): event country.
        capacity (int): maximum number of attendees.
        creator_id (int): user ID of the organiser.
        rsvp_deadline (datetime): last date/time to RSVP.
        visibility (str): event visibility (public/private/unlisted).
        allow_plus_ones (bool): whether attendees can bring guests.
        waitlist_enabled (bool): whether waitlist is enabled.
        auto_approval (bool): whether RSVPs are auto-approved.
        cover_image_url (str): URL to event cover image.
        tags (str): comma-separated event tags.
        status (str): event status (active/cancelled/completed).
        created_at (datetime): creation timestamp.
        updated_at (datetime): last update timestamp.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)  # None means unlimited
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rsvp_deadline = db.Column(db.DateTime, nullable=True)
    visibility = db.Column(db.String(20), default='public')  # public/private/unlisted
    allow_plus_ones = db.Column(db.Boolean, default=True)
    waitlist_enabled = db.Column(db.Boolean, default=False)
    auto_approval = db.Column(db.Boolean, default=True)
    cover_image_url = db.Column(db.String(200), nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # comma-separated
    status = db.Column(db.String(20), default='active')  # active/cancelled/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rsvps = db.relationship('RSVP', backref='event', lazy=True)
    invitations = db.relationship('Invitation', backref='event', lazy=True)

    @property
    def accepted_count(self) -> int:
        """Return total number of accepted attendees including guest counts."""
        count = 0
        for rsvp in self.rsvps:
            if rsvp.status == 'Accepted':
                count += 1 + (rsvp.guests or 0)
        return count

    @property
    def maybe_count(self) -> int:
        return sum(1 for rsvp in self.rsvps if rsvp.status == 'Maybe')

    @property
    def declined_count(self) -> int:
        return sum(1 for rsvp in self.rsvps if rsvp.status == 'Declined')

    @property
    def waitlist_count(self) -> int:
        return sum(1 for rsvp in self.rsvps if rsvp.status == 'Waitlisted')

    @property
    def available_spots(self) -> int:
        if self.capacity is None:
            return float('inf')  # Unlimited capacity
        return max(self.capacity - self.accepted_count, 0)

    @property
    def is_full(self) -> bool:
        return self.capacity is not None and self.accepted_count >= self.capacity

    @property
    def is_past(self) -> bool:
        return self.start_date < datetime.utcnow()

    @property
    def is_upcoming(self) -> bool:
        return self.start_date > datetime.utcnow()

    @property
    def date(self) -> datetime:
        """Backward compatibility property."""
        return self.start_date


class RSVP(db.Model):
    """Represents an RSVP response from a user for an event.

    Attributes:
        id (int): primary key.
        event_id (int): associated event.
        user_id (int): associated user.
        status (str): 'Accepted', 'Maybe', 'Declined', or 'Waitlisted'.
        guests (int): number of additional guests.
        note (str): optional note from attendee.
        qr_code (str): unique code string for admission.
        checked_in (bool): whether user has been checked in.
        checked_in_at (datetime): when user was checked in.
        created_at (datetime): timestamp when RSVP was created.
        updated_at (datetime): timestamp when RSVP was last updated.
    """

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Accepted/Maybe/Declined/Waitlisted
    guests = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)
    qr_code = db.Column(db.String(64), unique=True, nullable=True)
    checked_in = db.Column(db.Boolean, default=False)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invitation(db.Model):
    """Represents an invitation to an event.

    Attributes:
        id (int): primary key.
        event_id (int): associated event.
        email (str): invitee email address.
        user_id (int): associated user (if they have an account).
        token (str): unique invitation token.
        status (str): invitation status (pending/accepted/declined).
        personal_message (str): optional personal message from organizer.
        sent_at (datetime): when invitation was sent.
        responded_at (datetime): when invitee responded.
    """

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/accepted/declined
    personal_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)


class Notification(db.Model):
    """Represents an in-app notification for a user.

    Attributes:
        id (int): primary key.
        user_id (int): recipient user.
        type (str): notification type (invite/rsvp/event_update/etc).
        title (str): notification title.
        message (str): notification message.
        payload (str): JSON payload with additional data.
        read_at (datetime): when notification was read.
        created_at (datetime): when notification was created.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    payload = db.Column(db.Text, nullable=True)  # JSON data
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_email(to_email, subject, body, html_body=None):
    """Send email notification."""
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print(f"Email not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = to_email
        
        # Add text and HTML parts
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def create_notification(user_id, notification_type, title, message, payload=None):
    """Create an in-app notification."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        payload=payload
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def send_event_notification(event, notification_type, user=None):
    """Send event-related email notifications."""
    if not user:
        # Send to all attendees
        attendees = User.query.join(RSVP).filter(
            RSVP.event_id == event.id,
            RSVP.status == 'Accepted',
            User.email_notifications == True
        ).all()
    else:
        attendees = [user] if user.email_notifications else []
    
    for attendee in attendees:
        if notification_type == 'event_created':
            subject = f"New Event: {event.name}"
            body = f"""Hello {attendee.display_name},

A new event has been created:

Event: {event.name}
Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}
Location: {event.location}
Description: {event.description}

Please RSVP at: {request.url_root}event/{event.id}

Best regards,
EventApp Team"""
        elif notification_type == 'event_updated':
            subject = f"Event Updated: {event.name}"
            body = f"""Hello {attendee.display_name},

The event "{event.name}" has been updated:

Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}
Location: {event.location}
Description: {event.description}

Please check the updated details at: {request.url_root}event/{event.id}

Best regards,
EventApp Team"""
        elif notification_type == 'rsvp_confirmation':
            subject = f"RSVP Confirmation: {event.name}"
            body = f"""Hello {attendee.display_name},

Thank you for your RSVP to "{event.name}".

Event Details:
Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}
Location: {event.location}

Your QR code for check-in is available at: {request.url_root}event/{event.id}

Best regards,
EventApp Team"""
        elif notification_type == 'waitlist_promotion':
            subject = f"You're In! {event.name}"
            body = f"""Hello {attendee.display_name},

Great news! You've been promoted from the waitlist for "{event.name}".

Event Details:
Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}
Location: {event.location}

Your QR code for check-in is available at: {request.url_root}event/{event.id}

Best regards,
EventApp Team"""
        
        send_email(attendee.email, subject, body)
        
        # Also create in-app notification
        create_notification(
            attendee.id,
            notification_type,
            subject,
            body.split('\n\n')[1] if '\n\n' in body else body
        )


def generate_qr_image(code: str) -> str:
    """Generate a QR code image as a base64 string for embedding in HTML.

    Args:
        code: Unique code to encode in the QR image.

    Returns:
        Base64 encoded PNG image string.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_b64


def create_tables():
    db.create_all()
    
    # Add sample events with cover images if no events exist
    if Event.query.count() == 0:
        sample_events = [
            {
                'name': 'Tech Conference 2024',
                'description': 'Join us for the biggest technology conference of the year. Learn about the latest trends in AI, cloud computing, and software development.',
                'start_date': datetime(2024, 10, 15, 9, 0),
                'end_date': datetime(2024, 10, 15, 17, 0),
                'location': 'Convention Center, Downtown',
                'city': 'New York',
                'capacity': 500,
                'cover_image_url': '/static/images/events/conference.jpg'
            },
            {
                'name': 'Design Workshop',
                'description': 'Hands-on workshop covering modern design principles, user experience, and creative thinking techniques.',
                'start_date': datetime(2024, 10, 20, 10, 0),
                'end_date': datetime(2024, 10, 20, 16, 0),
                'location': 'Creative Studio, Arts District',
                'city': 'San Francisco',
                'capacity': 30,
                'cover_image_url': '/static/images/events/workshop.jpg'
            },
            {
                'name': 'Business Networking Event',
                'description': 'Connect with industry leaders, entrepreneurs, and professionals. Great opportunity to expand your network.',
                'start_date': datetime(2024, 10, 25, 18, 0),
                'end_date': datetime(2024, 10, 25, 21, 0),
                'location': 'Grand Hotel Ballroom',
                'city': 'Chicago',
                'capacity': 200,
                'cover_image_url': '/static/images/events/networking.jpg'
            },
            {
                'name': 'Product Training Session',
                'description': 'Comprehensive training on our latest product features. Perfect for new team members and existing users.',
                'start_date': datetime(2024, 11, 5, 9, 0),
                'end_date': datetime(2024, 11, 5, 12, 0),
                'location': 'Training Center, Office Building',
                'city': 'Austin',
                'capacity': 50,
                'cover_image_url': '/static/images/events/training.jpg'
            },
            {
                'name': 'Annual Company Party',
                'description': 'Celebrate another successful year with food, drinks, music, and great company. All employees and families welcome!',
                'start_date': datetime(2024, 12, 15, 19, 0),
                'end_date': datetime(2024, 12, 15, 23, 0),
                'location': 'Rooftop Garden, Main Office',
                'city': 'Seattle',
                'capacity': 150,
                'cover_image_url': '/static/images/events/party.jpg'
            }
        ]
        
        # Get the first admin user to be the creator
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            for event_data in sample_events:
                event = Event(
                    name=event_data['name'],
                    description=event_data['description'],
                    start_date=event_data['start_date'],
                    end_date=event_data['end_date'],
                    location=event_data['location'],
                    city=event_data['city'],
                    capacity=event_data['capacity'],
                    cover_image_url=event_data['cover_image_url'],
                    creator=admin_user
                )
                db.session.add(event)
        
        db.session.commit()
        print("Sample events with cover images created!")

# Create tables when app starts
with app.app_context():
    create_tables()


@app.route('/')
def index():
    """Home page showing upcoming events."""
    events = Event.query.order_by(Event.start_date.asc()).all()
    return render_template('index.html', events=events)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        errors = []
        if not username or len(username) < 2:
            errors.append('Username must be at least 2 characters long.')
        if not email:
            errors.append('Email is required.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event (admin/organiser only)."""
    if not current_user.is_admin:
        flash('Only organisers can create events.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date_str = request.form.get('date')  # format: YYYY-MM-DD
        time_str = request.form.get('time')  # format: HH:MM
        location = request.form.get('location')
        capacity = request.form.get('capacity')
        rsvp_deadline_str = request.form.get('rsvp_deadline')  # optional
        try:
            event_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            flash('Invalid date or time.', 'danger')
            return redirect(url_for('create_event'))
        try:
            capacity_int = int(capacity)
        except (ValueError, TypeError):
            flash('Capacity must be a number.', 'danger')
            return redirect(url_for('create_event'))
        rsvp_deadline = None
        if rsvp_deadline_str:
            try:
                rsvp_deadline = datetime.strptime(rsvp_deadline_str, '%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                flash('Invalid RSVP deadline.', 'danger')
                return redirect(url_for('create_event'))
        event = Event(name=name,
                      description=description,
                      start_date=event_datetime,
                      location=location,
                      capacity=capacity_int,
                      creator=current_user,
                      rsvp_deadline=rsvp_deadline)
        db.session.add(event)
        db.session.commit()
        
        # Send notifications to all users (optional - you might want to limit this)
        # send_event_notification(event, 'event_created')
        
        flash('Event created successfully.', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    return render_template('create_event.html')


@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_detail(event_id):
    """View event details and handle RSVP responses."""
    event = Event.query.get_or_404(event_id)
    rsvp = RSVP.query.filter_by(event_id=event.id, user_id=current_user.id).first()
    if request.method == 'POST':
        # Handle RSVP submission
        status = request.form.get('status')
        guests = request.form.get('guests') or 0
        try:
            guests_int = int(guests)
            if guests_int < 0:
                raise ValueError
        except ValueError:
            flash('Guests must be a non‑negative integer.', 'danger')
            return redirect(url_for('event_detail', event_id=event.id))
        # Check capacity
        total_attending = event.accepted_count
        new_total = total_attending + (1 + guests_int if status == 'Accepted' else 0)
        if status == 'Accepted' and new_total > event.capacity:
            flash('Event capacity reached. You can no longer accept.', 'danger')
            return redirect(url_for('event_detail', event_id=event.id))
        if rsvp is None:
            rsvp = RSVP(event_id=event.id, user_id=current_user.id)
            db.session.add(rsvp)
        # Update RSVP details
        rsvp.status = status
        rsvp.guests = guests_int
        # Generate unique QR code if accepted
        if status == 'Accepted':
            if not rsvp.qr_code:
                code = str(uuid.uuid4())
                # Ensure uniqueness across RSVPs
                while RSVP.query.filter_by(qr_code=code).first():
                    code = str(uuid.uuid4())
                rsvp.qr_code = code
            # Send confirmation email
            send_event_notification(event, 'rsvp_confirmation', current_user)
        else:
            # clear qr code if not attending
            rsvp.qr_code = None
        db.session.commit()
        flash('Your RSVP has been updated.', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    qr_image = None
    if rsvp and rsvp.qr_code:
        qr_image = generate_qr_image(rsvp.qr_code)
    return render_template('event_detail.html', event=event, rsvp=rsvp, qr_image=qr_image)


@app.route('/verify', methods=['GET', 'POST'])
@login_required
def verify_qr():
    """Page for organisers to verify a QR code and check‑in attendees."""
    if not current_user.is_admin:
        flash('Only organisers can verify attendees.', 'danger')
        return redirect(url_for('index'))
    attendee = None
    if request.method == 'POST':
        code = request.form.get('code')
        rsvp = RSVP.query.filter_by(qr_code=code).first()
        if not rsvp:
            flash('QR code not found.', 'danger')
        else:
            if rsvp.checked_in:
                flash('Attendee already checked in.', 'warning')
                attendee = rsvp
            else:
                rsvp.checked_in = True
                db.session.commit()
                flash('Check‑in successful.', 'success')
                attendee = rsvp
    return render_template('verify.html', attendee=attendee)


@app.route('/dashboard')
@login_required
def dashboard():
    """Organiser dashboard showing events and RSVP stats."""
    if not current_user.is_admin:
        flash('Only organisers can view the dashboard.', 'danger')
        return redirect(url_for('index'))
    events = Event.query.filter_by(creator_id=current_user.id).order_by(Event.start_date.desc()).all()
    return render_template('dashboard.html', events=events)


@app.route('/my-events')
@login_required
def my_events():
    """Shows events the user has RSVP’d to."""
    rsvps = RSVP.query.filter_by(user_id=current_user.id).all()
    return render_template('my_events.html', rsvps=rsvps)


@app.route('/event/<int:event_id>/update', methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    """Update an existing event (organiser only)."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.creator_id and not current_user.is_admin:
        flash('You do not have permission to update this event.', 'danger')
        return redirect(url_for('event_detail', event_id=event.id))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        location = request.form.get('location')
        capacity = request.form.get('capacity')
        rsvp_deadline_str = request.form.get('rsvp_deadline')
        try:
            event_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            flash('Invalid date or time.', 'danger')
            return redirect(url_for('update_event', event_id=event.id))
        try:
            capacity_int = int(capacity)
        except (ValueError, TypeError):
            flash('Capacity must be a number.', 'danger')
            return redirect(url_for('update_event', event_id=event.id))
        rsvp_deadline = None
        if rsvp_deadline_str:
            try:
                rsvp_deadline = datetime.strptime(rsvp_deadline_str, '%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                flash('Invalid RSVP deadline.', 'danger')
                return redirect(url_for('update_event', event_id=event.id))
        event.name = name
        event.description = description
        event.date = event_datetime
        event.location = location
        event.capacity = capacity_int
        event.rsvp_deadline = rsvp_deadline
        db.session.commit()
        
        # Send notifications to attendees about update
        send_event_notification(event, 'event_updated')
        
        flash('Event updated successfully.', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    # Prepopulate form with current values
    return render_template('update_event.html', event=event)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management."""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        timezone = request.form.get('timezone', 'UTC')
        country = request.form.get('country', '').strip()
        city = request.form.get('city', '').strip()
        email_notifications = request.form.get('email_notifications') == 'on'
        push_notifications = request.form.get('push_notifications') == 'on'
        time_format_24h = request.form.get('time_format_24h') == 'on'
        privacy_show_city = request.form.get('privacy_show_city') == 'on'
        privacy_show_full_name = request.form.get('privacy_show_full_name') == 'on'
        
        # Validation
        if not username or len(username) < 2:
            flash('Username must be at least 2 characters long.', 'danger')
            return redirect(url_for('profile'))
        
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('profile'))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already registered by another user.', 'danger')
            return redirect(url_for('profile'))
        
        # Update user fields
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.username = username
        current_user.email = email
        current_user.phone = phone
        current_user.timezone = timezone
        current_user.country = country
        current_user.city = city
        current_user.email_notifications = email_notifications
        current_user.push_notifications = push_notifications
        current_user.time_format_24h = time_format_24h
        current_user.privacy_show_city = privacy_show_city
        current_user.privacy_show_full_name = privacy_show_full_name
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')


@app.route('/analytics')
@login_required
def analytics():
    """Event analytics for organizers."""
    if not current_user.is_admin:
        flash('Only organizers can view analytics.', 'danger')
        return redirect(url_for('index'))
    
    # Get statistics
    total_events = Event.query.filter_by(creator_id=current_user.id).count()
    total_rsvps = db.session.query(RSVP).join(Event).filter(Event.creator_id == current_user.id).count()
    total_attendees = db.session.query(RSVP).join(Event).filter(
        Event.creator_id == current_user.id,
        RSVP.status == 'Accepted'
    ).count()
    
    # Recent events with stats
    recent_events = Event.query.filter_by(creator_id=current_user.id).order_by(Event.start_date.desc()).limit(5).all()
    
    return render_template('analytics.html', 
                         total_events=total_events,
                         total_rsvps=total_rsvps,
                         total_attendees=total_attendees,
                         recent_events=recent_events)


@app.route('/past-events')
@login_required
def past_events():
    """View past events."""
    # Get past events for current user (both organized and attended)
    organized_events = Event.query.filter(
        Event.creator_id == current_user.id,
        Event.start_date < datetime.utcnow()
    ).order_by(Event.start_date.desc()).all()
    
    attended_events = Event.query.join(RSVP).filter(
        RSVP.user_id == current_user.id,
        Event.start_date < datetime.utcnow()
    ).order_by(Event.start_date.desc()).all()
    
    # Combine and deduplicate
    all_past_events = list(set(organized_events + attended_events))
    all_past_events.sort(key=lambda x: x.start_date, reverse=True)
    
    return render_template('past_events.html', events=all_past_events)


@app.route('/notifications')
@login_required
def notifications():
    """View notifications."""
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, read_at=None).count()
    
    return render_template('notifications.html', notifications=user_notifications, unread_count=unread_count)


@app.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@app.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    Notification.query.filter_by(user_id=current_user.id, read_at=None).update({'read_at': datetime.utcnow()})
    db.session.commit()
    return jsonify({'success': True})


@app.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    """Cancel an event."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.creator_id and not current_user.is_admin:
        flash('You do not have permission to cancel this event.', 'danger')
        return redirect(url_for('event_detail', event_id=event.id))
    
    event.status = 'cancelled'
    db.session.commit()
    
    # Notify attendees
    send_event_notification(event, 'event_cancelled')
    
    flash('Event has been cancelled.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/event/<int:event_id>/duplicate', methods=['POST'])
@login_required
def duplicate_event(event_id):
    """Duplicate an event."""
    original_event = Event.query.get_or_404(event_id)
    if current_user.id != original_event.creator_id and not current_user.is_admin:
        flash('You do not have permission to duplicate this event.', 'danger')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Create new event with same details but new date
    new_event = Event(
        name=f"{original_event.name} (Copy)",
        description=original_event.description,
        start_date=original_event.start_date + timedelta(days=7),  # Default to 1 week later
        end_date=original_event.end_date + timedelta(days=7) if original_event.end_date else None,
        timezone=original_event.timezone,
        location=original_event.location,
        city=original_event.city,
        country=original_event.country,
        capacity=original_event.capacity,
        creator_id=current_user.id,
        visibility=original_event.visibility,
        allow_plus_ones=original_event.allow_plus_ones,
        waitlist_enabled=original_event.waitlist_enabled,
        auto_approval=original_event.auto_approval,
        cover_image_url=original_event.cover_image_url,
        tags=original_event.tags
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    flash('Event duplicated successfully.', 'success')
    return redirect(url_for('event_detail', event_id=new_event.id))


@app.route('/event/<int:event_id>/attendees')
@login_required
def event_attendees(event_id):
    """View and manage event attendees."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.creator_id and not current_user.is_admin:
        flash('You do not have permission to view attendees.', 'danger')
        return redirect(url_for('event_detail', event_id=event.id))
    
    attendees = RSVP.query.filter_by(event_id=event.id).order_by(RSVP.created_at.asc()).all()
    
    return render_template('event_attendees.html', event=event, attendees=attendees)


@app.route('/event/<int:event_id>/export')
@login_required
def export_attendees(event_id):
    """Export attendee list to CSV."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.creator_id and not current_user.is_admin:
        flash('You do not have permission to export attendees.', 'danger')
        return redirect(url_for('event_detail', event_id=event.id))
    
    attendees = RSVP.query.filter_by(event_id=event.id).all()
    
    # Create CSV content
    csv_content = "Name,Email,Status,Guests,Note,Checked In,RSVP Date\n"
    for rsvp in attendees:
        csv_content += f'"{rsvp.attendee.display_name}","{rsvp.attendee.email}","{rsvp.status}",{rsvp.guests},"{rsvp.note or ""}","{"Yes" if rsvp.checked_in else "No"}","{rsvp.created_at.strftime("%Y-%m-%d %H:%M")}"\n'
    
    from flask import Response
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={event.name}_attendees.csv'}
    )


@app.route('/api/event/<int:event_id>/stats')
@login_required
def event_stats(event_id):
    """API endpoint for event statistics."""
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.creator_id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = {
        'accepted': event.accepted_count,
        'maybe': event.maybe_count,
        'declined': event.declined_count,
        'waitlisted': event.waitlist_count,
        'capacity': event.capacity,
        'available_spots': event.available_spots,
        'checked_in': sum(1 for rsvp in event.rsvps if rsvp.checked_in)
    }
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, port=5001)