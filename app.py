from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import hashlib
import uuid
import os
import logging
from pathlib import Path

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
except ImportError:
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

# Extensions
csrf = CSRFProtect(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vennligst logg inn for å få tilgang til denne siden.'
login_manager.login_message_category = 'info'

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
            if send_reminder_notification(reminder, recipient_email):
                # Logg notifikasjon
                notifications.append({
                    'reminder_id': reminder['id'],
                    'recipient': recipient_email,
                    'sent_at': now.isoformat(),
                    'type': 'reminder_notification'
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
    
    # Filtrer påminnelser
    my_reminders = [r for r in reminders if r['user_id'] == current_user.email and not r['completed']]
    shared_with_me = [r for r in shared_reminders if r['shared_with'] == current_user.email and not r['completed']]
    
    # Sorter etter dato
    my_reminders.sort(key=lambda x: x['datetime'])
    shared_with_me.sort(key=lambda x: x['datetime'])
    
    # Statistikk
    total_my = len([r for r in reminders if r['user_id'] == current_user.email])
    completed_my = len([r for r in reminders if r['user_id'] == current_user.email and r['completed']])
    completion_rate = (completed_my / total_my * 100) if total_my > 0 else 0
    
    # Tilgjengelige brukere for deling
    available_users = [user_data['email'] for user_data in users.values() 
                      if user_data['email'] != current_user.email]
    
    # Former
    form = ReminderForm()
    
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
                         available_users=available_users,
                         current_time=datetime.now())

@app.route('/add_reminder', methods=['POST'])
@login_required
def add_reminder():
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
            'my_reminders': my_count,
            'shared_reminders': shared_count,
            'completed': completed_count
        })
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Failed to get reminder counts'}), 500

@app.route('/offline')
def offline():
    """Offline page for PWA"""
    return render_template('offline.html')

@app.route('/static/sw.js')
def service_worker():
    """Serve service worker with correct headers"""
    response = app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/static/manifest.json')
def manifest():
    """Serve PWA manifest with correct headers"""
    response = app.send_static_file('manifest.json')
    response.headers['Content-Type'] = 'application/manifest+json'
    return response

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('errors/500.html'), 500

# Template filters
@app.template_filter('as_datetime')
def as_datetime(date_string):
    try:
        return datetime.fromisoformat(date_string.replace(' ', 'T'))
    except:
        return datetime.now()

@app.template_filter('strftime')
def datetime_format(value, format='%d.%m.%Y %H:%M'):
    """Format a datetime object."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace(' ', 'T'))
        except:
            return value
    
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    return str(value)

@app.route('/focus-modes')
@login_required
def focus_modes():
    """Vis fokusmoduser"""
    users = dm.load_data('users')
    # Sikre at users er dict
    if isinstance(users, list):
        users_dict = {}
        for user in users:
            uid = user.get('id') or user.get('user_id') or str(uuid.uuid4())
            users_dict[uid] = user
        users = users_dict
    # Hent eller sett default fokusmodus
    current_mode = users.get(current_user.id, {}).get('focus_mode', 'normal')
    return render_template('focus_modes.html',
                         focus_modes=FocusModeManager.get_all_modes(),
                         current_mode=current_mode)

@app.route('/set-focus-mode', methods=['POST'])
@login_required
def set_focus_mode():
    focus_mode = request.form.get('focus_mode')
    if not focus_mode:
        flash('Fokusmodus er påkrevd', 'error')
        return redirect(url_for('focus_modes'))
    try:
        # Lagre fokusmodus på bruker i users.json
        users = dm.load_data('users')
        # Sikre at users er dict
        if isinstance(users, list):
            users_dict = {}
            for user in users:
                uid = user.get('id') or user.get('user_id') or str(uuid.uuid4())
                users_dict[uid] = user
            users = users_dict
        if current_user.id in users:
            users[current_user.id]['focus_mode'] = focus_mode
            dm.save_data('users', users)
            flash(f'Fokusmodus endret til: {FocusModeManager.get_mode_by_name(focus_mode).name}', 'success')
        else:
            flash('Fant ikke bruker for å lagre fokusmodus', 'error')
    except Exception as e:
        logger.error(f"Error setting focus mode: {e}")
        flash('Feil ved å endre fokusmodus', 'error')
    return redirect(url_for('focus_modes'))

@app.route('/email-settings')
@login_required
def email_settings():
    """Vis e-post innstillinger og statistikk"""
    try:
        stats = email_service.get_email_statistics()
        # Sikre at alle nødvendige nøkler finnes
        stats.setdefault('total_sent', 0)
        stats.setdefault('total_failed', 0)
        stats.setdefault('success_rate', 0)
        stats.setdefault('recent_emails', [])
        return render_template('email_settings.html', 
                             email_stats=stats,
                             current_user=current_user)
    except Exception as e:
        logger.error(f"Error loading email settings: {e}")
        flash('Feil ved lasting av e-post innstillinger', 'error')
        return render_template('email_settings.html', 
                             email_stats={'total_sent': 0, 'total_failed': 0, 'success_rate': 0, 'recent_emails': []},
                             current_user=current_user)

@app.route('/noteboards')
@login_required
def noteboards():
    """Vis alle tavler brukeren har tilgang til"""
    try:
        boards = noteboard_manager.get_user_boards(current_user.email)
        # Sikre at boards er en liste av objekter med nødvendige attributter
        if not boards:
            boards = []
        return render_template('noteboards.html', boards=boards)
    except Exception as e:
        logger.error(f"Error loading noteboards: {e}")
        flash('Feil ved lasting av tavler', 'error')
        return render_template('noteboards.html', boards=[])

@app.route('/create-board', methods=['POST'])
@login_required
def create_board():
    """Opprett ny delt tavle"""
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    if not title:
        flash('Tittel er påkrevd', 'error')
        return redirect(url_for('noteboards'))
    
    try:
        board = noteboard_manager.create_board(title, description, current_user.email)
        flash(f'Tavle "{title}" opprettet! Tilgangskode: {board.access_code}', 'success')
        return redirect(url_for('view_board', board_id=board.board_id))
    except Exception as e:
        logger.error(f"Error creating board: {e}")
        flash('Feil ved opprettelse av tavle', 'error')
        return redirect(url_for('noteboards'))

@app.route('/board/<board_id>')
@login_required
def view_board(board_id):
    """Vis spesifikk tavle"""
    try:
        board = noteboard_manager.get_board_by_id(board_id)
        
        if not board or current_user.email not in board.members:
            flash('Tavle ikke funnet eller ingen tilgang', 'error')
            return redirect(url_for('noteboards'))
        
        return render_template('noteboard.html', board=board)
    except Exception as e:
        logger.error(f"Error viewing board {board_id}: {e}")
        flash('Feil ved lasting av tavle', 'error')
        return redirect(url_for('noteboards'))

@app.route('/share-reminder', methods=['POST'])
@login_required
def share_reminder():
    """Del påminnelse med andre via e-post (også ikke-registrerte brukere)"""
    reminder_id = request.form.get('reminder_id')
    email_addresses = request.form.get('email_addresses', '').strip()
    personal_message = request.form.get('personal_message', '')
    
    if not reminder_id or not email_addresses:
        flash('Påminnelse ID og e-post adresser er påkrevd', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse email addresses
    emails = [email.strip() for email in email_addresses.replace(',', ' ').split() if '@' in email]
    
    if not emails:
        flash('Ingen gyldige e-post adresser funnet', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the reminder
    reminders = dm.load_data('reminders')
    reminder = None
    for r in reminders:
        if r['id'] == reminder_id and r['user_id'] == current_user.email:
            reminder = r
            break
    
    if not reminder:
        flash('Påminnelse ikke funnet', 'error')
        return redirect(url_for('dashboard'))
    
    # Send emails to all recipients
    successful_shares = 0
    for email in emails:
        try:
            # Create a shared reminder entry for tracking
            shared_reminder = {
                'id': str(uuid.uuid4()),
                'original_id': reminder_id,
                'shared_by': current_user.email,
                'shared_with': email,
                'title': reminder['title'],
                'description': reminder['description'],
                'datetime': reminder['datetime'],
                'priority': reminder['priority'],
                'category': reminder['category'],
                'completed': False,
                'created': datetime.now().isoformat(),
                'is_shared': True,
                'personal_message': personal_message
            }
            
            # Send email notification
            subject = f"Påminnelse delt med deg fra {current_user.email}"
            if send_email(email, subject, 'emails/shared_reminder.html', 
                         reminder=shared_reminder, 
                         shared_by=current_user.email,
                         personal_message=personal_message):
                
                # Save shared reminder for registered users
                users = dm.load_data('users')
                is_registered = any(user_data['email'] == email for user_data in users.values())
                
                if is_registered:
                    shared_reminders = dm.load_data('shared_reminders')
                    shared_reminders.append(shared_reminder)
                    dm.save_data('shared_reminders', shared_reminders)
                
                successful_shares += 1
            
        except Exception as e:
            logger.error(f"Error sharing reminder with {email}: {e}")
    
    if successful_shares > 0:
        flash(f'Påminnelse delt med {successful_shares} personer!', 'success')
    else:
        flash('Feil ved deling av påminnelse', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/email-settings', methods=['GET', 'POST'])
@login_required
def email_settings():
    if request.method == 'POST':
        # Handle email settings update
        email = request.form.get('email')
        if email:
            # Save email settings logic here
            flash('Email settings updated successfully!', 'success')
        else:
            flash('Email is required.', 'error')
    return render_template('email_settings.html')

@app.route('/test-email', methods=['POST'])
@login_required
def test_email():
    """Send test-e-post"""
    email = request.form.get('email', current_user.email)
    
    if email_service.send_test_email(email):
        flash(f'Test-e-post sendt til {email}!', 'success')
    else:
        flash(f'Feil ved sending av test-e-post til {email}', 'error')
    
    return redirect(url_for('email_settings'))

@app.route('/email-log')
@login_required
def email_log():
    """Vis e-post logg (kun for debugging)"""
    try:
        log_data = dm.load_data('email_log')
        # Sort by timestamp, newest first
        log_data.sort(key=lambda x: x.get('sent_at', ''), reverse=True)
        return jsonify({
            'success': True,
            'log': log_data[-50:]  # Last 50 entries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/join-board', methods=['POST'])
@login_required
def join_board():
    """Bli med på delt tavle via tilgangskode"""
    access_code = request.form.get('access_code')
    if not access_code:
        flash('Tilgangskode er påkrevd', 'error')
        return redirect(url_for('noteboards'))
    try:
        board = noteboard_manager.join_board(access_code, current_user.email)
        if board:
            flash(f'Du er nå medlem av tavlen "{board.title}"!', 'success')
            return redirect(url_for('view_board', board_id=board.board_id))
        else:
            flash('Ugyldig tilgangskode eller du er allerede medlem.', 'error')
            return redirect(url_for('noteboards'))
    except Exception as e:
        logger.error(f"Error joining board: {e}")
        flash('Feil ved å bli med på tavle', 'error')
        return redirect(url_for('noteboards'))

if __name__ == '__main__':
    app.run(debug=True)
