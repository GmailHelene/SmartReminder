from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import logging
from pathlib import Path
import hashlib
import uuid

# Import local modules with fallbacks
try:
    from config import config
except ImportError:
    # Fallback configuration if config.py doesn't exist
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
        MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
        MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
        REMINDER_CHECK_INTERVAL = int(os.environ.get('REMINDER_CHECK_INTERVAL') or 300)
        NOTIFICATION_ADVANCE_MINUTES = int(os.environ.get('NOTIFICATION_ADVANCE_MINUTES') or 15)
        WTF_CSRF_ENABLED = True
        TESTING = False
        MAIL_SUPPRESS_SEND = False
    
    config = {'development': Config, 'testing': Config, 'production': Config, 'default': Config}

try:
    from focus_modes import FocusModeManager
except ImportError:
    # Fallback if focus_modes module doesn't exist
    class FocusModeManager:
        @staticmethod
        def get_all_modes():
            return {
                'normal': type('obj', (object,), {'name': 'Normal', 'description': 'Standard mode'}),
                'focus': type('obj', (object,), {'name': 'Focus', 'description': 'High focus mode'}),
                'break': type('obj', (object,), {'name': 'Break', 'description': 'Break time mode'})
            }
        
        @staticmethod
        def get_mode(mode_name):
            modes = FocusModeManager.get_all_modes()
            return modes.get(mode_name, modes['normal'])
        
        @staticmethod
        def apply_mode_to_reminders(reminders, mode_name):
            return reminders
        
        @staticmethod
        def get_mode_settings(mode_name):
            return {}

try:
    from shared_noteboard import NoteboardManager
    print("Successfully imported NoteboardManager from shared_noteboard")
except ImportError as e:
    print(f"Failed to import NoteboardManager: {e}")
    # Fallback if shared_noteboard module doesn't exist
    class NoteboardManager:
        def __init__(self, dm):
            self.dm = dm
        
        def get_user_boards(self, email):
            return []
        
        def create_board(self, title, description, creator_email):
            # Mock board object
            return type('Board', (), {
                'board_id': str(uuid.uuid4()),
                'title': title,
                'description': description,
                'access_code': str(uuid.uuid4())[:8].upper(),
                'members': [creator_email]
            })()
        
        def get_board_by_id(self, board_id):
            return None
        
        def join_board(self, access_code, email):
            return None
        
        def save_board(self, board):
            pass

try:
    from email_service import EmailService
except ImportError:
    # Fallback if email_service module doesn't exist
    class EmailService:
        def __init__(self, mail, dm):
            self.mail = mail
            self.dm = dm
        
        def send_reminder_notification(self, reminder, email):
            subject = f"Påminnelse: {reminder['title']}"
            return send_email(email, subject, 'emails/reminder_notification.html', reminder=reminder)
        
        def send_shared_reminder_notification(self, reminder, shared_by, email):
            subject = f"Delt påminnelse fra {shared_by}: {reminder['title']}"
            return send_email(email, subject, 'emails/shared_reminder.html', reminder=reminder, shared_by=shared_by)
        
        def send_test_email(self, email):
            subject = "Test e-post fra SmartReminder"
            return send_email(email, subject, 'emails/test_email.html', user_email=email)
        
        def get_email_statistics(self):
            email_log = self.dm.load_data('email_log')
            total_sent = len([log for log in email_log if log.get('status') == 'sent'])
            total_failed = len([log for log in email_log if log.get('status') == 'failed'])
            success_rate = (total_sent / len(email_log) * 100) if email_log else 0
            
            return {
                'total_sent': total_sent,
                'total_failed': total_failed,
                'success_rate': round(success_rate, 2),
                'by_template': {},
                'recent_emails': email_log[-10:] if email_log else []
            }

# Mock APScheduler for testing
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    if not os.environ.get('TESTING'):
        scheduler = BackgroundScheduler()
        scheduler.start()
    else:
        # Mock scheduler for testing
        class MockScheduler:
            def add_job(self, **kwargs):
                pass
            def start(self):
                pass
        scheduler = MockScheduler()
except ImportError:
    # Mock scheduler for testing
    class MockScheduler:
        def add_job(self, **kwargs):
            pass
        def start(self):
            pass
    scheduler = MockScheduler()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)

# Configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Custom Jinja2 filters
def nl2br_filter(text):
    """Convert newlines to HTML break tags"""
    if text is None:
        return ''
    # Replace \n with <br> and also handle \r\n
    result = text.replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>')
    
    # Try to use Markup for safety, fallback to string
    try:
        from markupsafe import Markup
        return Markup(result)
    except ImportError:
        # Fallback if markupsafe is not available
        return result

def as_datetime_filter(date_string):
    """Convert ISO date string to datetime object"""
    if not date_string:
        return None
    try:
        if isinstance(date_string, datetime):
            return date_string
        if isinstance(date_string, str):
            # Handle different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    return datetime.strptime(date_string.split('.')[0] if '.' in date_string else date_string, fmt)
                except ValueError:
                    continue
        return date_string
    except Exception as e:
        logger.warning(f"as_datetime filter error: {e}")
        return None

def format_datetime_filter(date_input, format_string='%d.%m.%Y %H:%M'):
    """Combined filter to safely format datetime - handles None and invalid dates"""
    if not date_input:
        return 'Ikke satt'
    
    try:
        # First convert to datetime if needed
        if isinstance(date_input, str):
            # Try to parse string to datetime
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    date_obj = datetime.strptime(date_input.split('.')[0] if '.' in date_input else date_input, fmt)
                    return date_obj.strftime(format_string)
                except ValueError:
                    continue
            return 'Ugyldig datoformat'
        elif hasattr(date_input, 'strftime'):
            # Already a datetime object
            return date_input.strftime(format_string)
        else:
            return str(date_input)
    except Exception as e:
        logger.warning(f"format_datetime filter error: {e} for input: {date_input}")
        return 'Datefeil'

def strftime_filter(date_obj, format_string='%Y-%m-%d %H:%M'):
    """Format datetime object to string"""
    if not date_obj:
        return 'Ikke satt'
    try:
        if isinstance(date_obj, str):
            # If it's already a string, try to parse it first
            date_obj = as_datetime_filter(date_obj)
            if not date_obj:
                return 'Ugyldig dato'
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime(format_string)
        return str(date_obj)
    except Exception as e:
        logger.warning(f"strftime filter error: {e} for object: {date_obj}")
        return 'Ugyldig dato'

# Register the filters
app.template_filter('nl2br')(nl2br_filter)
app.jinja_env.filters['nl2br'] = nl2br_filter
app.template_filter('as_datetime')(as_datetime_filter)
app.jinja_env.filters['as_datetime'] = as_datetime_filter
app.template_filter('strftime')(strftime_filter)
app.jinja_env.filters['strftime'] = strftime_filter
app.template_filter('format_datetime')(format_datetime_filter)
app.jinja_env.filters['format_datetime'] = format_datetime_filter

# Add safe url_for function
def safe_url_for(endpoint, **values):
    """Safely generate URL, return # if endpoint doesn't exist"""
    try:
        return url_for(endpoint, **values)
    except Exception:
        return '#'

app.jinja_env.globals['safe_url_for'] = safe_url_for

# Verification prints (for debugging)
print(f"🔧 nl2br filter registered: {'nl2br' in app.jinja_env.filters}")
print(f"🔧 as_datetime filter registered: {'as_datetime' in app.jinja_env.filters}")
print(f"🔧 strftime filter registered: {'strftime' in app.jinja_env.filters}")
print(f"🔧 format_datetime filter registered: {'format_datetime' in app.jinja_env.filters}")

# Extensions
csrf = CSRFProtect(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vennligst logg inn for å få tilgang til denne siden.'
login_manager.login_message_category = 'info'

# Template context processors
@app.context_processor
def inject_csrf_token():
    """Make CSRF token available in all templates"""
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)

# 📊 Data Manager (forbedret)
class DataManager:
    def __init__(self):
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Sørg for at alle data-filer eksisterer"""
        files = ['users', 'reminders', 'shared_reminders', 'notifications', 'email_log', 'shared_noteboards']
        for filename in files:
            filepath = self.data_dir / f"{filename}.json"
            if not filepath.exists():
                # users skal være dict, resten liste eller dict
                initial_data = {} if filename == 'users' else ([] if filename in ['reminders', 'shared_reminders', 'notifications', 'email_log'] else {})
                self.save_data(filename, initial_data)
            else:
                # MIGRERING: Konverter users fra liste til dict hvis nødvendig
                if filename == 'users':
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            # Konverter til dict
                            users_dict = {}
                            for user in data:
                                user_id = user.get('id') or user.get('user_id') or str(uuid.uuid4())
                                users_dict[user_id] = user
                            self.save_data('users', users_dict)
                    except Exception as e:
                        logger.error(f"Feil ved migrering av users: {e}")

    def load_data(self, filename):
        """Last inn data fra JSON-fil med error handling"""
        filepath = self.data_dir / f"{filename}.json"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Sikre at users alltid er dict
                if filename == 'users' and isinstance(data, list):
                    users_dict = {}
                    for user in data:
                        user_id = user.get('id') or user.get('user_id') or str(uuid.uuid4())
                        users_dict[user_id] = user
                    self.save_data('users', users_dict)
                    return users_dict
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Feil ved lasting av {filename}: {e}")
            return {} if filename == 'users' else []

    def save_data(self, filename, data):
        """Lagre data til JSON-fil med backup"""
        filepath = self.data_dir / f"{filename}.json"
        backup_path = self.data_dir / f"{filename}.backup.json"
        
        try:
            # Opprett backup
            if filepath.exists():
                import shutil
                shutil.copy2(filepath, backup_path)
            
            # Lagre ny data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Feil ved lagring av {filename}: {e}")
            # Gjenopprett fra backup
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, filepath)
            raise

# Global data manager
dm = DataManager()

# Initialize services after dm is created
email_service = EmailService(mail, dm)
noteboard_manager = NoteboardManager(dm)

# 📧 E-post funksjoner
def send_email(to, subject, template, **kwargs):
    """Send e-post med template"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=render_template(template, **kwargs),
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        
        # Logg e-post
        email_log = dm.load_data('email_log')
        email_log.append({
            'to': to,
            'subject': subject,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        })
        dm.save_data('email_log', email_log)
        
        logger.info(f"E-post sendt til {to}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Feil ved sending av e-post til {to}: {e}")
        
        # Logg feil
        email_log = dm.load_data('email_log')
        email_log.append({
            'to': to,
            'subject': subject,
            'sent_at': datetime.now().isoformat(),
            'status': 'failed',
            'error': str(e)
        })
        dm.save_data('email_log', email_log)
        
        return False

def send_reminder_notification(reminder, recipient_email):
    """Send påminnelse-notifikasjon via e-post"""
    return email_service.send_reminder_notification(reminder, recipient_email)

def send_shared_reminder_notification(reminder, shared_by, recipient_email):
    """Send notifikasjon om delt påminnelse"""
    return email_service.send_shared_reminder_notification(reminder, shared_by, recipient_email)

def check_reminders_for_notifications():
    """Sjekk påminnelser og send notifikasjoner"""
    try:
        now = datetime.now()
        notification_time = now + timedelta(minutes=app.config['NOTIFICATION_ADVANCE_MINUTES'])
        
        # Sjekk alle påminnelser
        reminders = dm.load_data('reminders')
        shared_reminders = dm.load_data('shared_reminders')
        notifications = dm.load_data('notifications')
        
        sent_notifications = {n['reminder_id'] for n in notifications}
        
        all_reminders = []
        
        # Forbered mine påminnelser
        for reminder in reminders:
            if not reminder['completed'] and reminder['id'] not in sent_notifications:
                reminder_dt = datetime.fromisoformat(reminder['datetime'].replace(' ', 'T'))
                if now <= reminder_dt <= notification_time:
                    all_reminders.append((reminder, reminder['user_id']))
        
        # Forbered delte påminnelser
        for reminder in shared_reminders:
            if not reminder['completed'] and reminder['id'] not in sent_notifications:
                reminder_dt = datetime.fromisoformat(reminder['datetime'].replace(' ', 'T'))
                if now <= reminder_dt <= notification_time:
                    all_reminders.append((reminder, reminder['shared_with']))
        
        # Send notifikasjoner
        for reminder, recipient_email in all_reminders:
            # Extract sound setting from reminder
            sound = reminder.get('sound', 'pristine.mp3')
            
            # Import push_service function for direct notification
            try:
                from push_service import send_reminder_notification as send_push_reminder
                # Try to send push notification first (more immediate)
                push_sent = send_push_reminder(
                    recipient_email, 
                    reminder['title'], 
                    reminder['datetime'], 
                    sound=sound,
                    dm=dm
                )
                logger.info(f"Push notification {'sent' if push_sent else 'failed'} for {reminder['id']}")
            except Exception as push_err:
                logger.error(f"Error sending push notification: {push_err}")
                push_sent = False
                
            # Also send email notification as backup
            if send_reminder_notification(reminder, recipient_email):
                # Logg notifikasjon
                notifications.append({
                    'reminder_id': reminder['id'],
                    'recipient': recipient_email,
                    'sent_at': now.isoformat(),
                    'type': 'reminder_notification',
                    'push_sent': push_sent
                })
        
        # Lagre oppdaterte notifikasjoner
        if all_reminders:
            dm.save_data('notifications', notifications)
            logger.info(f"Sendt {len(all_reminders)} påminnelse-notifikasjoner")
            
    except Exception as e:
        logger.error(f"Feil ved sjekking av påminnelser: {e}")

# 📝 WTForms
class LoginForm(FlaskForm):
    username = StringField('Brukernavn/E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    submit = SubmitField('Logg inn')

class RegisterForm(FlaskForm):
    username = StringField('Brukernavn/E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrer deg')

class ReminderForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired()])
    description = TextAreaField('Beskrivelse')
    date = DateField('Dato', validators=[DataRequired()], default=datetime.now().date())
    time = TimeField('Tid', validators=[DataRequired()], default=datetime.now().time())
    priority = SelectField('Prioritet', choices=[('Lav', 'Lav'), ('Medium', 'Medium'), ('Høy', 'Høy')])
    category = SelectField('Kategori', choices=[
        ('Jobb', 'Jobb'), ('Privat', 'Privat'), ('Helse', 'Helse'), 
        ('Familie', 'Familie'), ('Annet', 'Annet')
    ])
    sound = SelectField('Lyd', choices=[
        ('pristine.mp3', 'Standard lyd'), 
        ('ding.mp3', 'Ding! lyd'),
        ('beep.mp3', 'Beep lyd')
    ], default='pristine.mp3')
    submit = SubmitField('Opprett påminnelse')

# 👤 User Class (forbedret)
class User(UserMixin):
    def __init__(self, user_id, username, email, password_hash=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get(user_id):
        users = dm.load_data('users')
        # Sikre at users er dict
        if isinstance(users, list):
            users_dict = {}
            for user in users:
                uid = user.get('id') or user.get('user_id') or str(uuid.uuid4())
                users_dict[uid] = user
            users = users_dict
        if user_id in users:
            user_data = users[user_id]
            return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
        return None
    
    @staticmethod
    def get_by_email(email):
        users = dm.load_data('users')
        # Sikre at users er dict
        if isinstance(users, list):
            users_dict = {}
            for user in users:
                uid = user.get('id') or user.get('user_id') or str(uuid.uuid4())
                users_dict[uid] = user
            users = users_dict
        for user_id, user_data in users.items():
            if user_data['email'] == email:
                return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Planlegg automatisk sjekking av påminnelser (only if not testing)
if not os.environ.get('TESTING'):
    scheduler.add_job(
        func=check_reminders_for_notifications,
        trigger="interval",
        seconds=app.config['REMINDER_CHECK_INTERVAL'],
        id='reminder_check'
    )

# 🌐 Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.get_by_email(form.username.data)
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Velkommen tilbake, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Feil e-post eller passord!', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Sjekk om bruker eksisterer
        if User.get_by_email(form.username.data):
            flash('E-post er allerede registrert!', 'error')
            return render_template('login.html', form=LoginForm(), register_form=form)
        
        # Opprett ny bruker
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(form.password.data)
        
        users = dm.load_data('users')
        # Sikre at users er dict
        if not isinstance(users, dict):
            users = {}
        users[user_id] = {
            'username': form.username.data,
            'email': form.username.data,
            'password_hash': password_hash,
            'created': datetime.now().isoformat(),
            'focus_mode': 'normal'  # Sett default fokusmodus
        }
        dm.save_data('users', users)
        
        # Logg inn bruker
        user = User(user_id, form.username.data, form.username.data, password_hash)
        login_user(user, remember=True)
        
        flash(f'Velkommen, {user.username}! Din konto er opprettet.', 'success')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du er nå logget ut.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Hent data
    reminders = dm.load_data('reminders')
    shared_reminders = dm.load_data('shared_reminders')
    users = dm.load_data('users')
    
    # Filtrer påminnelser (safely handle missing completed field)
    my_reminders = [r for r in reminders if r.get('user_id') == current_user.email and not r.get('completed', False)]
    shared_with_me = [r for r in shared_reminders if r.get('shared_with') == current_user.email and not r.get('completed', False)]
    
    # Sorter etter dato
    my_reminders.sort(key=lambda x: x['datetime'])
    shared_with_me.sort(key=lambda x: x['datetime'])
    
    # Statistikk (safely handle missing completed field)
    total_my = len([r for r in reminders if r.get('user_id') == current_user.email])
    completed_my = len([r for r in reminders if r.get('user_id') == current_user.email and r.get('completed', False)])
    completion_rate = (completed_my / total_my * 100) if total_my > 0 else 0
    
    # Tilgjengelige brukere for deling
    available_users = [user_data['email'] for user_data in users.values() 
                      if user_data['email'] != current_user.email]
    
    # Get boards count
    try:
        boards = noteboard_manager.get_user_boards(current_user.email)
        boards_count = len(boards)
    except:
        boards_count = 0
    
    # Former
    form = ReminderForm()
    
    # Prepare events for calendar (JSON format)
    events_json = []
    
    # Add my reminders
    for reminder in my_reminders:
        color = '#dc3545' if reminder['priority'] == 'Høy' else '#fd7e14' if reminder['priority'] == 'Medium' else '#198754'
        events_json.append({
            'id': reminder['id'],
            'title': reminder['title'],
            'start': reminder['datetime'],
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'description': reminder.get('description', ''),
                'category': reminder.get('category', ''),
                'priority': reminder.get('priority', ''),
                'type': 'my'
            }
        })
    
    # Add shared reminders
    for reminder in shared_with_me:
        events_json.append({
            'id': f"shared_{reminder['id']}",
            'title': f"{reminder['title']} ({reminder.get('shared_by', 'Ukjent')})",
            'start': reminder['datetime'],
            'backgroundColor': '#6f42c1',
            'borderColor': '#6f42c1',
            'extendedProps': {
                'description': reminder.get('description', ''),
                'category': reminder.get('category', ''),
                'priority': reminder.get('priority', ''),
                'sharedBy': reminder.get('shared_by', ''),
                'type': 'shared'
            }
        })
    
    import json
    
    return render_template('dashboard.html', 
                         form=form,
                         my_reminders=my_reminders,
                         shared_reminders=shared_with_me,
                         stats={
                             'total': total_my,
                             'completed': completed_my,
                             'completion_rate': completion_rate,
                             'shared_count': len(shared_with_me)
                         },
                         boards_count=boards_count,
                         available_users=available_users,
                         current_time=datetime.now(),
                         events_json=json.dumps(events_json))

@app.route('/complete_reminder/<reminder_id>')
@login_required
def complete_reminder(reminder_id):
    # Sjekk mine påminnelser
    reminders = dm.load_data('reminders')
    for reminder in reminders:
        if reminder['id'] == reminder_id and reminder['user_id'] == current_user.email:
            reminder['completed'] = True
            reminder['completed_at'] = datetime.now().isoformat()
            dm.save_data('reminders', reminders)
            flash('Påminnelse fullført!', 'success')
            return redirect(url_for('dashboard'))
    
    # Sjekk delte påminnelser
    shared_reminders = dm.load_data('shared_reminders')
    for reminder in shared_reminders:
        if reminder['id'] == reminder_id and reminder['shared_with'] == current_user.email:
            reminder['completed'] = True
            reminder['completed_at'] = datetime.now().isoformat()
            dm.save_data('shared_reminders', shared_reminders)
            flash('Delt påminnelse fullført!', 'success')
            return redirect(url_for('dashboard'))
    
    flash('Påminnelse ikke funnet!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_reminder/<reminder_id>')
@login_required
def delete_reminder(reminder_id):
    reminders = dm.load_data('reminders')
    original_count = len(reminders)
    
    reminders = [r for r in reminders if not (r['id'] == reminder_id and r['user_id'] == current_user.email)]
    
    if len(reminders) < original_count:
        dm.save_data('reminders', reminders)
        flash('Påminnelse slettet!', 'success')
    else:
        flash('Påminnelse ikke funnet eller tilhører ikke deg!', 'error')
    
    return redirect(url_for('dashboard'))

# Add missing API endpoint
@app.route('/api/reminder-count')
@login_required
def api_reminder_count():
    """API endpoint for reminder counts"""
    try:
        reminders = dm.load_data('reminders')
        shared_reminders = dm.load_data('shared_reminders')
        
        my_count = len([r for r in reminders if r['user_id'] == current_user.email and not r['completed']])
        shared_count = len([r for r in shared_reminders if r['shared_with'] == current_user.email and not r['completed']])
        completed_count = len([r for r in reminders if r['user_id'] == current_user.email and r['completed']])
        
        return jsonify({
            'my_count': my_count,
            'shared_count': shared_count,
            'completed_count': completed_count,
            'total_count': my_count + shared_count
        })
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Failed to get reminder counts'}), 500

@app.route('/api/update-reminder-datetime', methods=['POST'])
@login_required
def api_update_reminder_datetime():
    """API endpoint for updating reminder date/time via drag & drop"""
    try:
        data = request.get_json()
        reminder_id = data.get('reminder_id')
        new_date = data.get('date')
        new_time = data.get('time')
        
        if not all([reminder_id, new_date, new_time]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Update in regular reminders
        reminders = dm.load_data('reminders')
        updated = False
        
        for reminder in reminders:
            if reminder['id'] == reminder_id and reminder['user_id'] == current_user.email:
                reminder['datetime'] = f"{new_date} {new_time}"
                updated = True
                break
        
        if updated:
            dm.save_data('reminders', reminders)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Reminder not found or access denied'}), 404
            
    except Exception as e:
        logger.error(f"API error updating reminder datetime: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add_reminder', methods=['POST'])
@login_required
def add_reminder():
    """Handle both form and JSON requests for creating reminders"""
    try:
        logger.info(f"add_reminder called - is_json: {request.is_json}, content_type: {request.content_type}")
        
        # Check if it's a JSON request (from calendar)
        if request.is_json:
            data = request.get_json()
            logger.info(f"JSON data received: {data}")
            
            # Validate required fields
            if not data.get('title') or not data.get('date') or not data.get('time'):
                logger.warning(f"Missing required fields in JSON data: {data}")
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Create reminder from JSON data
            reminder_id = str(uuid.uuid4())
            new_reminder = {
                'id': reminder_id,
                'user_id': current_user.email,
                'title': data.get('title'),
                'description': data.get('description', ''),
                'datetime': f"{data.get('date')} {data.get('time')}",
                'priority': data.get('priority', 'Medium'),
                'category': data.get('category', 'Annet'),
                'completed': False,
                'created': datetime.now().isoformat(),
                'shared_with': []
            }
            
            # Save reminder
            reminders = dm.load_data('reminders')
            reminders.append(new_reminder)
            dm.save_data('reminders', reminders)
            
            return jsonify({'success': True, 'reminder_id': reminder_id})
            
        else:
            # Handle regular form submission (existing functionality)
            form = ReminderForm()
            
            if form.validate_on_submit():
                # Hent deling-data fra request
                share_with = request.form.getlist('share_with')
                
                # Opprett påminnelse
                reminder_id = str(uuid.uuid4())
                new_reminder = {
                    'id': reminder_id,
                    'user_id': current_user.email,
                    'title': form.title.data,
                    'description': form.description.data,
                    'datetime': f"{form.date.data} {form.time.data}",
                    'priority': form.priority.data,
                    'category': form.category.data,
                    'sound': request.form.get('sound', 'pristine.mp3'),
                    'completed': False,
                    'created': datetime.now().isoformat(),
                    'shared_with': share_with
                }
                
                # Lagre påminnelse
                reminders = dm.load_data('reminders')
                reminders.append(new_reminder)
                dm.save_data('reminders', reminders)
                
                # Opprett delte påminnelser og send notifikasjoner
                if share_with:
                    shared_reminders = dm.load_data('shared_reminders')
                    
                    for recipient in share_with:
                        shared_reminder = {
                            'id': str(uuid.uuid4()),
                            'original_id': reminder_id,
                            'shared_by': current_user.email,
                            'shared_with': recipient,
                            'title': form.title.data,
                            'description': form.description.data,
                            'datetime': f"{form.date.data} {form.time.data}",
                            'priority': form.priority.data,
                            'category': form.category.data,
                            'sound': request.form.get('sound', 'pristine.mp3'),
                            'completed': False,
                            'created': datetime.now().isoformat(),
                            'is_shared': True
                        }
                        shared_reminders.append(shared_reminder)
                        
                        # Send e-post notifikasjon om delt påminnelse
                        send_shared_reminder_notification(shared_reminder, current_user.email, recipient)
                    
                    dm.save_data('shared_reminders', shared_reminders)
                    flash(f'Påminnelse "{form.title.data}" opprettet og delt med {len(share_with)} personer!', 'success')
                else:
                    flash(f'Påminnelse "{form.title.data}" opprettet!', 'success')
                    
            else:
                flash('Feil i skjema. Sjekk alle felt.', 'error')
            
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Feil ved opprettelse av påminnelse', 'error')
            return redirect(url_for('dashboard'))

@app.route('/share_reminder', methods=['POST'])
@login_required
def share_reminder():
    """Handle sharing reminders via email"""
    try:
        reminder_id = request.form.get('reminder_id')
        email_addresses = request.form.get('email_addresses', '')
        personal_message = request.form.get('personal_message', '')
        
        if not reminder_id or not email_addresses:
            flash('Påminnelse ID og e-post adresser er påkrevd', 'error')
            return redirect(url_for('dashboard'))
        
        # Find the reminder to share
        reminders = dm.load_data('reminders')
        reminder_to_share = None
        for reminder in reminders:
            if reminder['id'] == reminder_id and reminder['user_id'] == current_user.email:
                reminder_to_share = reminder
                break
        
        if not reminder_to_share:
            flash('Påminnelse ikke funnet eller du har ikke tilgang', 'error')
            return redirect(url_for('dashboard'))
        
        # Parse email addresses (split by comma, semicolon, or whitespace)
        import re
        emails = re.split(r'[,;\s]+', email_addresses.strip())
        emails = [email.strip() for email in emails if email.strip()]
        
        if not emails:
            flash('Ingen gyldig e-post adresser funnet', 'error')
            return redirect(url_for('dashboard'))
        
        # Validate email addresses
        valid_emails = []
        for email in emails:
            if '@' in email and '.' in email.split('@')[1]:
                valid_emails.append(email)
            else:
                flash(f'Ugyldig e-post adresse: {email}', 'warning')
        
        if not valid_emails:
            flash('Ingen gyldige e-post adresser å sende til', 'error')
            return redirect(url_for('dashboard'))
        
        # Load shared reminders
        shared_reminders = dm.load_data('shared_reminders')
        shared_count = 0
        
        # Create shared reminder entries and send notifications
        for email in valid_emails:
            # Check if already shared with this email
            already_shared = False
            for shared in shared_reminders:
                if (shared['original_id'] == reminder_id and 
                    shared['shared_with'] == email):
                    already_shared = True
                    break
            
            if not already_shared:
                # Create shared reminder entry
                shared_reminder = {
                    'id': str(uuid.uuid4()),
                    'original_id': reminder_id,
                    'user_id': reminder_to_share['user_id'],
                    'shared_by': current_user.email,
                    'shared_with': email,
                    'title': reminder_to_share['title'],
                    'description': reminder_to_share['description'],
                    'datetime': reminder_to_share['datetime'],
                    'priority': reminder_to_share['priority'],
                    'category': reminder_to_share['category'],
                    'completed': False,
                    'shared_date': datetime.now().isoformat(),
                    'personal_message': personal_message
                }
                
                shared_reminders.append(shared_reminder)
                
                # Send notification email
                try:
                    email_sent = send_shared_reminder_notification(
                        reminder_to_share, 
                        current_user.email, 
                        email
                    )
                    if email_sent:
                        shared_count += 1
                    else:
                        flash(f'Kunne ikke sende e-post til {email}', 'warning')
                except Exception as e:
                    logger.error(f"Error sending email to {email}: {e}")
                    flash(f'Feil ved sending av e-post til {email}', 'warning')
            else:
                flash(f'Påminnelse allerede delt med {email}', 'info')
        
        # Save shared reminders
        if shared_count > 0:
            dm.save_data('shared_reminders', shared_reminders)
            flash(f'Påminnelse delt med {shared_count} person(er)', 'success')
        else:
            flash('Ingen nye delinger ble opprettet', 'info')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error sharing reminder: {e}")
        flash('Feil ved deling av påminnelse', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/share-calendar-event', methods=['POST'])
@login_required
def api_share_calendar_event():
    """API endpoint for sharing calendar events via email"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        reminder_id = data.get('reminder_id')
        email_addresses = data.get('email_addresses', '')
        personal_message = data.get('personal_message', '')
        
        if not reminder_id or not email_addresses:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Parse email addresses
        emails = []
        for email in email_addresses.replace(',', ' ').split():
            email = email.strip()
            if email and '@' in email:
                emails.append(email)
        
        if not emails:
            return jsonify({'success': False, 'error': 'No valid email addresses provided'}), 400
        
        # Find the reminder
        reminders = dm.load_data('reminders')
        reminder = None
        
        for r in reminders:
            if r['id'] == reminder_id and r['user_id'] == current_user.email:
                reminder = r
                break
        
        if not reminder:
            return jsonify({'success': False, 'error': 'Reminder not found or access denied'}), 404
        
        # Send calendar invitation emails
        success_count = 0
        for email in emails:
            try:
                send_calendar_invitation_email(reminder, current_user.email, email, personal_message)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send calendar invitation to {email}: {e}")
        
        if success_count > 0:
            return jsonify({
                'success': True, 
                'message': f'Kalenderinvitasjon sendt til {success_count} av {len(emails)} mottakere'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to send any invitations'}), 500
            
    except Exception as e:
        logger.error(f"Error sharing calendar event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def send_calendar_invitation_email(reminder, shared_by, recipient_email, personal_message=None):
    """
    Send a calendar invitation (ICS) for a reminder via email.
    """
    from flask_mail import Message
    import pytz
    from email.utils import formataddr
    import base64
    
    # Prepare event details
    event_title = reminder.get('title', 'Påminnelse')
    event_description = reminder.get('description', '')
    event_start = reminder.get('datetime')
    event_end = reminder.get('datetime')
    event_category = reminder.get('category', '')
    event_priority = reminder.get('priority', 'Medium')
    
    # Parse start/end time
    try:
        start_dt = datetime.strptime(event_start, '%Y-%m-%d %H:%M')
        end_dt = start_dt + timedelta(minutes=30)
    except Exception:
        start_dt = datetime.now()
        end_dt = start_dt + timedelta(minutes=30)
    
    # ICS content
    dtstamp = start_dt.strftime('%Y%m%dT%H%M%SZ')
    dtstart = start_dt.strftime('%Y%m%dT%H%M%SZ')
    dtend = end_dt.strftime('%Y%m%dT%H%M%SZ')
    uid = f"{reminder.get('id')}@smartreminder"
    
    ics = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//SmartReminder//EN\nCALSCALE:GREGORIAN\nBEGIN:VEVENT\nUID:{uid}\nDTSTAMP:{dtstamp}\nDTSTART:{dtstart}\nDTEND:{dtend}\nSUMMARY:{event_title}\nDESCRIPTION:{event_description}\nCATEGORIES:{event_category}\nPRIORITY:{'1' if event_priority=='Høy' else '5' if event_priority=='Medium' else '9'}\nEND:VEVENT\nEND:VCALENDAR"""
    
    # Email body
    html_body = render_template(
        'emails/calendar_invitation.html',
        reminder=reminder,
        shared_by=shared_by,
        personal_message=personal_message or ''
    )
    
    msg = Message(
        subject=f"Delt kalenderhendelse: {event_title}",
        recipients=[recipient_email],
        html=html_body
    )
    msg.body = f"{event_title}\n\n{event_description}\n\nTid: {event_start}"
    msg.sender = formataddr(("SmartReminder", current_app.config.get('MAIL_DEFAULT_SENDER', shared_by)))
    
    # Attach ICS
    msg.attach(
        filename="invitasjon.ics",
        content_type="text/calendar; charset=utf-8; method=REQUEST",
        data=ics
    )
    
    mail.send(msg)

# 📝 Noteboard Routes
@app.route('/noteboards')
@login_required
def noteboards():
    """Display all noteboards for the current user"""
    try:
        boards = noteboard_manager.get_user_boards(current_user.email)
        return render_template('noteboards.html', boards=boards)
    except Exception as e:
        logger.error(f"Error loading noteboards: {e}")
        flash('Feil ved lasting av tavler', 'error')
        return redirect(url_for('dashboard'))

@app.route('/create-board', methods=['POST'])
@login_required
def create_board():
    """Create a new noteboard"""
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            flash('Tavletittel er påkrevd', 'error')
            return redirect(url_for('noteboards'))
        
        board = noteboard_manager.create_board(title, description, current_user.email)
        flash(f'Tavle "{title}" opprettet! Tilgangskode: {board.access_code}', 'success')
        return redirect(url_for('view_board', board_id=board.board_id))
        
    except Exception as e:
        logger.error(f"Error creating board: {e}")
        flash('Feil ved opprettelse av tavle', 'error')
        return redirect(url_for('noteboards'))

@app.route('/join-board', methods=['GET', 'POST'])
@login_required
def join_board():
    """Join a noteboard using access code"""
    if request.method == 'GET':
        # Handle join via URL with code parameter
        access_code = request.args.get('code')
        if access_code:
            try:
                board = noteboard_manager.join_board(access_code, current_user.email)
                if board:
                    flash(f'Du har blitt med på tavlen "{board.title}"!', 'success')
                    return redirect(url_for('view_board', board_id=board.board_id))
                else:
                    flash('Ugyldig tilgangskode', 'error')
            except Exception as e:
                logger.error(f"Error joining board: {e}")
                flash('Feil ved tilkobling til tavle', 'error')
        
        return redirect(url_for('noteboards'))
    
    # Handle POST request from form
    try:
        access_code = request.form.get('access_code', '').strip().upper()
        
        if not access_code:
            flash('Tilgangskode er påkrevd', 'error')
            return redirect(url_for('noteboards'))
        
        board = noteboard_manager.join_board(access_code, current_user.email)
        if board:
            flash(f'Du har blitt med på tavlen "{board.title}"!', 'success')
            return redirect(url_for('view_board', board_id=board.board_id))
        else:
            flash('Ugyldig tilgangskode', 'error')
            return redirect(url_for('noteboards'))
            
    except Exception as e:
        logger.error(f"Error joining board: {e}")
        flash('Feil ved tilkobling til tavle', 'error')
        return redirect(url_for('noteboards'))

@app.route('/board/<board_id>')
@app.route('/noteboard/<board_id>')
@login_required 
def view_board(board_id):
    """View a specific noteboard"""
    try:
        board = noteboard_manager.get_board_by_id(board_id)
        
        if not board:
            flash('Tavle ikke funnet', 'error')
            return redirect(url_for('noteboards'))
        
        # Check if user has access to this board
        if current_user.email not in board.members:
            flash('Du har ikke tilgang til denne tavlen', 'error')
            return redirect(url_for('noteboards'))
        
        return render_template('noteboard.html', board=board)
        
    except Exception as e:
        logger.error(f"Error viewing board {board_id}: {e}")
        flash('Feil ved lasting av tavle', 'error')
        return redirect(url_for('noteboards'))

@app.route('/add-note-to-board/<board_id>', methods=['POST'])
@login_required
def add_note_to_board(board_id):
    """Add a note to a noteboard"""
    try:
        board = noteboard_manager.get_board_by_id(board_id)
        
        if not board or current_user.email not in board.members:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            flash('Du har ikke tilgang til denne tavlen', 'error')
            return redirect(url_for('noteboards'))
        
        if request.is_json:
            # Handle JSON request (from JavaScript)
            data = request.get_json()
            content = data.get('content', '').strip()
            color = data.get('color', 'warning')
            x = data.get('x', 0)
            y = data.get('y', 0)
        else:
            # Handle form request
            content = request.form.get('content', '').strip()
            color = request.form.get('color', 'warning')
            x = 0
            y = 0
        
        if not content:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Content is required'}), 400
            flash('Innhold er påkrevd', 'error')
            flash('Innhold er påkrevd', 'error')
            return redirect(url_for('view_board', board_id=board_id))
        
        # Add note to board
        note = board.add_note(content, current_user.email, color=color)
        if x or y:
            note['position'] = {'x': x, 'y': y}
        
        # Save board
        noteboard_manager.save_board(board)
        
        # Send notification to other board members
        try:
            noteboard_manager.notify_board_update(
                board_id, 
                'Nytt notat lagt til', 
                current_user.email, 
                note_content=content
            )
        except Exception as e:
            logger.error(f"Error sending board update notification: {e}")
        
        if request.is_json:
            return jsonify({'success': True, 'note_id': note['id']})
        else:
            flash('Notat lagt til!', 'success')
            return redirect(url_for('view_board', board_id=board_id))
            
    except Exception as e:
        logger.error(f"Error adding note to board {board_id}: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash('Feil ved tillegging av notat', 'error')
        return redirect(url_for('view_board', board_id=board_id))

@app.route('/api/update-note-position/<note_id>', methods=['POST'])
@login_required
def api_update_note_position(note_id):
    """Update note position via API"""
    try:
        data = request.get_json()
        x = data.get('x', 0)
        y = data.get('y', 0)
        
        # Find the board containing this note
        boards = noteboard_manager.dm.load_data('shared_noteboards')
        for board_data in boards.values():
            if current_user.email in board_data.get('members', []):
                board = noteboard_manager.get_board_by_id(board_data['board_id'])
                if board:
                    updated_note = board.update_note(note_id, position={'x': x, 'y': y})
                    if updated_note:
                        noteboard_manager.save_board(board)
                        return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Note not found'}), 404
        
    except Exception as e:
        logger.error(f"Error updating note position: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/edit-note/<note_id>', methods=['POST'])
@login_required  
def api_edit_note(note_id):
    """Edit note content via API"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Find the board containing this note
        boards = noteboard_manager.dm.load_data('shared_noteboards')
        for board_data in boards.values():
            if current_user.email in board_data.get('members', []):
                board = noteboard_manager.get_board_by_id(board_data['board_id'])
                if board:
                    # Check if user can edit this note
                    for note in board.notes:
                        if note['id'] == note_id:
                            if note['author'] == current_user.email or board.created_by == current_user.email:
                                updated_note = board.update_note(note_id, content=content)
                                if updated_note:
                                    noteboard_manager.save_board(board)
                                    
                                    # Send notifications
                                    try:
                                        noteboard_manager.notify_board_update(
                                            board.board_id,
                                            'Notat oppdatert',
                                            current_user.email,
                                            note_content=content
                                        )
                                    except Exception as e:
                                        logger.error(f"Error sending update notification: {e}")
                                    
                                    return jsonify({'success': True})
                            else:
                                return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        return jsonify({'success': False, 'error': 'Note not found'}), 404
        
    except Exception as e:
        logger.error(f"Error editing note: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-note/<note_id>', methods=['DELETE'])
@login_required
def api_delete_note(note_id):
    """Delete note via API"""
    try:
        # Find the board containing this note
        boards = noteboard_manager.dm.load_data('shared_noteboards')
        for board_data in boards.values():
            if current_user.email in board_data.get('members', []):
                board = noteboard_manager.get_board_by_id(board_data['board_id'])
                if board:
                    if board.delete_note(note_id, current_user.email):
                        noteboard_manager.save_board(board)
                        
                        # Send notifications
                        try:
                            noteboard_manager.notify_board_update(
                                board.board_id,
                                'Notat slettet',
                                current_user.email
                            )
                        except Exception as e:
                            logger.error(f"Error sending delete notification: {e}")
                        
                        return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Note not found or permission denied'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Email settings route
@app.route('/email-settings', methods=['GET', 'POST'])
@login_required
def email_settings():
    """Email settings page - restricted to admin only"""
    # Only allow admin access
    if current_user.email != 'helene721@gmail.com':
        flash('Du har ikke tilgang til denne siden', 'error')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        # Handle email settings form
        flash('E-postinnstillinger oppdatert!', 'success')
        return redirect(url_for('email_settings'))
    
    # Get email statistics
    email_log = dm.load_data('email_log')
    total_sent = len([e for e in email_log if e.get('status') == 'sent'])
    total_failed = len([e for e in email_log if e.get('status') == 'failed'])
    total_emails = len(email_log)
    success_rate = round((total_sent / total_emails * 100) if total_emails > 0 else 0)
    recent_emails = sorted(email_log, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    
    email_stats = {
        'total_sent': total_sent,
        'total_failed': total_failed,
        'success_rate': success_rate,
        'recent_emails': recent_emails
    }
    
    return render_template('email_settings.html', email_stats=email_stats, config=app.config)

@app.route('/test-email', methods=['POST'])
@login_required
def test_email():
    """Send test email - restricted to admin only"""
    # Only allow admin access
    if current_user.email != 'helene721@gmail.com':
        flash('Du har ikke tilgang til denne funksjonen', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        email = request.form.get('email')
        if not email:
            flash('E-post adresse er påkrevd', 'error')
            return redirect(url_for('email_settings'))
        
        # Send test email
        success = email_service.send_test_email(email)
        if success:
            flash(f'Test-e-post sendt til {email}!', 'success')
        else:
            flash('Kunne ikke sende test-e-post', 'error')
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        flash('Feil ved sending av test-e-post', 'error')
    
    return redirect(url_for('email_settings'))

# Offline page route
@app.route('/offline')
def offline():
    """Offline page for PWA"""
    return render_template('offline.html')

# Focus modes route
@app.route('/focus-modes', methods=['GET', 'POST'])
@login_required
def focus_modes():
    """Focus modes page"""
    if request.method == 'POST':
        # Handle focus mode update
        focus_mode = request.form.get('focus_mode', 'normal')
        
        # Update user's focus mode
        users = dm.load_data('users')
        for user_data in users.values():
            if user_data['email'] == current_user.email:
                user_data['focus_mode'] = focus_mode
                break
        dm.save_data('users', users)
        
        flash('Fokusmodus oppdatert!', 'success')
        return redirect(url_for('focus_modes'))
    
    # Get current user's focus mode
    users = dm.load_data('users')
    current_focus_mode = 'normal'
    for user_data in users.values():
        if user_data['email'] == current_user.email:
            current_focus_mode = user_data.get('focus_mode', 'normal')
            break
    
    # Get available focus modes
    try:
        focus_modes_dict = FocusModeManager.get_all_modes()
    except:
        # Fallback if FocusModeManager doesn't work
        focus_modes_dict = {
            'normal': type('obj', (object,), {
                'name': 'Normal',
                'description': 'Standard modus for daglig bruk'
            }),
            'silent': type('obj', (object,), {
                'name': 'Stillemodus', 
                'description': 'Reduserte notifikasjoner'
            }),
            'adhd': type('obj', (object,), {
                'name': 'ADHD-modus',
                'description': 'Økt fokus og struktur'
            }),
            'elderly': type('obj', (object,), {
                'name': 'Modus for eldre',
                'description': 'Forenklet grensesnitt'
            })
        }
    
    return render_template('focus_modes.html', 
                         current_focus_mode=current_focus_mode,
                         focus_modes=focus_modes_dict)

@app.route('/api/calendar-events')
@login_required
def api_calendar_events():
    """API endpoint to get all calendar events for the current user (my + shared)"""
    try:
        # Get all reminders
        all_reminders = dm.load_data('reminders')
        shared_reminders = dm.load_data('shared_reminders')
        
        # Filter for current user's reminders
        my_reminders = [r for r in all_reminders if r.get('user_id') == current_user.email]
        
        # Filter shared reminders that are shared with current user
        shared_with_me = [r for r in shared_reminders if r.get('shared_with') == current_user.email]
        
        events_json = []
        
        # Add my reminders
        for reminder in my_reminders:
            color = '#dc3545' if reminder['priority'] == 'Høy' else '#fd7e14' if reminder['priority'] == 'Medium' else '#198754'
            events_json.append({
                'id': reminder['id'],
                'title': reminder['title'],
                'start': reminder['datetime'],
                'color': color
            })

        # Add shared reminders
        for reminder in shared_with_me:
            events_json.append({
                'id': f"shared_{reminder['id']}",
                'title': f"{reminder['title']} ({reminder.get('shared_by', 'Ukjent')})",
                'start': reminder['datetime'],
                'backgroundColor': '#6f42c1',
                'borderColor': '#6f42c1',
                'extendedProps': {
                    'description': reminder.get('description', ''),
                    'category': reminder.get('category', ''),
                    'priority': reminder.get('priority', ''),
                    'sharedBy': reminder.get('shared_by', ''),
                    'type': 'shared'
                }
            })
        
        logger.info(f"Calendar API: Returning {len(events_json)} events for user {current_user.email}")
        return jsonify(events_json)
        
    except Exception as e:
        logger.error(f"Error in calendar API: {e}")
        return jsonify({'error': 'Failed to load calendar events'}), 500

# Push notification routes
@app.route('/api/subscribe-push', methods=['POST'])
@login_required
def subscribe_push_notifications():
    """Subscribe user to push notifications"""
    try:
        subscription_data = request.get_json()
        
        # Store subscription in user data
        subscriptions = dm.load_data('push_subscriptions')
        user_email = current_user.email
        
        if user_email not in subscriptions:
            subscriptions[user_email] = []
        
        # Check if subscription already exists
        existing = False
        for sub in subscriptions[user_email]:
            if sub.get('endpoint') == subscription_data.get('endpoint'):
                existing = True
                break
        
        if not existing:
            subscription_data['created_at'] = datetime.now().isoformat()
            subscriptions[user_email].append(subscription_data)
            dm.save_data('push_subscriptions', subscriptions)
        
        return jsonify({'success': True, 'message': 'Push notifications enabled'})
        
    except Exception as e:
        logger.error(f"Error subscribing to push notifications: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-test-notification', methods=['POST'])
@login_required
def send_test_notification():
    """Send test push notification"""
    try:
        # Import push service
        try:
            from push_service import send_push_notification
        except ImportError:
            logger.warning("Push service not available")
            return jsonify({'success': False, 'error': 'Push notifications not configured'})
        
        success = send_push_notification(
            current_user.email,
            "Test notifikasjon",
            "Dette er en test-notifikasjon fra SmartReminder!",
            dm=dm
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Test notification sent'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send notification'})
            
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# VAPID public key endpoint for push notifications
@app.route('/api/vapid-public-key')
def get_vapid_public_key():
    """Get VAPID public key for push notifications"""
    try:
        from push_service import VAPID_PUBLIC_KEY
        return jsonify({'public_key': VAPID_PUBLIC_KEY})
    except ImportError:
        return jsonify({'error': 'Push notifications not configured'}), 500

@app.route('/set-instructor-status', methods=['POST'])
@login_required
def set_instructor_status():
    status = request.form.get('status')
    users = dm.load_data('users')
    user = users.get(current_user.email, {})
    user['status'] = status
    users[current_user.email] = user
    dm.save_data('users', users)
    # Varsle eier (eller alle instruktører unntatt deg selv)
    owner_email = user.get('owner')
    if owner_email and owner_email != current_user.email:
        send_push_notification(
            owner_email,
            title="Instruktørstatus oppdatert",
            body=f"{current_user.email} satte status til '{status}'",
            data={"type": "instructor_status", "status": status, "by": current_user.email},
            dm=dm
        )
    flash(f'Status oppdatert til {status}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/send-quick-message', methods=['POST'])
@login_required
def send_quick_message():
    template = request.form.get('template')
    # Send til alle instruktører (unntatt deg selv)
    users = dm.load_data('users')
    recipients = [u['email'] for u in users.values() if u.get('role') == 'instructor' and u['email'] != current_user.email]
    for email in recipients:
        send_push_notification(
            email,
            title="Hurtigbeskjed fra kjøreskole",
            body=template,
            data={"type": "quick_message", "from": current_user.email, "message": template},
            dm=dm
        )
    flash(f'Hurtigbeskjed sendt: {template}', 'info')
    return redirect(url_for('dashboard'))

@app.route('/api/send-quick-reply', methods=['POST'])
@login_required
def api_send_quick_reply():
    reply = request.json.get('reply')
    # Varsle eier (eller instruktør)
    users = dm.load_data('users')
    user = users.get(current_user.email, {})
    owner_email = user.get('owner')
    if owner_email and owner_email != current_user.email:
        send_push_notification(
            owner_email,
            title="Hurtigsvar fra elev",
            body=reply,
            data={"type": "quick_reply", "from": current_user.email, "reply": reply},
            dm=dm
        )
    return jsonify({'success': True, 'message': f'Reply sent: {reply}'})

@app.route('/notify-delay', methods=['POST'])
@login_required
def notify_delay():
    minutes = request.form.get('minutes')
    # Varsle eier (eller instruktør)
    users = dm.load_data('users')
    user = users.get(current_user.email, {})
    owner_email = user.get('owner')
    if owner_email and owner_email != current_user.email:
        send_push_notification(
            owner_email,
            title="Forsinkelse varslet",
            body=f"{current_user.email} er forsinket {minutes} min",
            data={"type": "delay", "minutes": minutes, "by": current_user.email},
            dm=dm
        )
    flash(f'Forsinkelse sendt: {minutes} min', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/log-lesson', methods=['POST'])
@login_required
def log_lesson():
    note = request.form.get('note')
    # Append to lesson log (could be per user)
    lesson_log = dm.load_data('lesson_log') or []
    lesson_log.append({'user': current_user.email, 'timestamp': datetime.now().strftime('%d.%m.%Y %H:%M'), 'note': note})
    dm.save_data('lesson_log', lesson_log)
    # Varsle eier (eller instruktør)
    users = dm.load_data('users')
    user = users.get(current_user.email, {})
    owner_email = user.get('owner')
    if owner_email and owner_email != current_user.email:
        send_push_notification(
            owner_email,
            title="Kjøretime logget",
            body=f"{current_user.email}: {note}",
            data={"type": "lesson_log", "by": current_user.email, "note": note},
            dm=dm
        )
    flash('Kjøretime logget!', 'success')
    return redirect(url_for('dashboard'))