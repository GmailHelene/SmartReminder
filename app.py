from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms.widgets import CheckboxInput, ListWidget
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
from pathlib import Path
from config import config
import psycopg2
import json
import hashlib
import uuid
import os
import logging


# Database setup
def init_db():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("ADVARSEL: Ingen DATABASE_URL funnet - bruker JSON-lagring")
        return False
        
    try:
        # Test connection
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Opprett users-tabell
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database tabeller initialisert!")
        return True
    except Exception as e:
        print(f"Databasefeil: {e}")
        return False

# Kall denne funksjonen når appen starter
use_db = init_db()

def get_db_connection():
    """Få databaseforbindelse"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return None
        
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)

# Database oppsett
DATABASE_URL = os.environ.get('DATABASE_URL')
def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return None

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Ingen database tilkobling - bruker JSON filer")
        return False
        
    cur = conn.cursor()
    
    # Opprett users tabell
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Opprett andre tabeller...
    
    conn.commit()
    cur.close()
    conn.close()
    return True

# Kall denne ved oppstart
init_db()

#class User(UserMixin):
    def __init__(self, user_id, username, email, password_hash=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get(user_id):
        # Prøv database først hvis tilgjengelig
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id, username, email, password_hash FROM users WHERE id = %s', (user_id,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user:
                    return User(user[0], user[1], user[2], user[3])
            except Exception as e:
                print(f"Database error: {e}")
        
        # Fallback til JSON
        users = dm.load_data('users')
        if user_id in users:
            user_data = users[user_id]
            return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
        return None
    
    @staticmethod
    def get_by_email(email):
        # Prøv database først hvis tilgjengelig
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id, username, email, password_hash FROM users WHERE email = %s', (email,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user:
                    return User(user[0], user[1], user[2], user[3])
            except Exception as e:
                print(f"Database error: {e}")
        
        # Fallback til JSON
        users = dm.load_data('users')
        for user_id, user_data in users.items():
            if user_data['email'] == email:
                return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
        return None

    def save(self):
        """Lagre bruker til database og JSON"""
        # Lagre til database hvis tilgjengelig
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    'INSERT INTO users (id, username, email, password_hash) VALUES (%s, %s, %s, %s) ON CONFLICT (email) DO NOTHING',
                    (self.id, self.username, self.email, self.password_hash)
                )
                conn.commit()
                cur.close()
                conn.close()
                print(f"Bruker {self.email} lagret i database")
                return True
            except Exception as e:
                print(f"Databasefeil ved lagring av bruker: {e}")
        
        # Alltid lagre til JSON også (backup)
        users = dm.load_data('users')
        users[self.id] = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created': datetime.now().isoformat()
        }
        dm.save_data('users', users)
        print(f"Bruker {self.email} lagret i JSON")
        return True
        
# Konfigurasjon
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Extensions
csrf = CSRFProtect(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vennligst logg inn for å få tilgang til denne siden.'
login_manager.login_message_category = 'info'

# Scheduler for e-post notifikasjoner
scheduler = BackgroundScheduler()
scheduler.start()

# Erstatt DataManager klassen med database funksjoner
def get_db_connection():
    """Få database tilkobling"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway PostgreSQL
        conn = psycopg2.connect(database_url)
    else:
        # Fallback til JSON filer for development
        return None
    return conn

def init_database():
    """Initialiser database tabeller"""
    conn = get_db_connection()
    if not conn:
        return  # Bruk JSON filer
    
    cursor = conn.cursor()
    
    # Opprett users tabell
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Opprett reminders tabell
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            datetime VARCHAR(255) NOT NULL,
            priority VARCHAR(50),
            category VARCHAR(50),
            completed BOOLEAN DEFAULT FALSE,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    # Opprett shared_reminders tabell
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_reminders (
            id VARCHAR(255) PRIMARY KEY,
            original_id VARCHAR(255),
            shared_by VARCHAR(255) NOT NULL,
            shared_with VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            datetime VARCHAR(255) NOT NULL,
            priority VARCHAR(50),
            category VARCHAR(50),
            completed BOOLEAN DEFAULT FALSE,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_shared BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Kall denne funksjonen når appen starter
init_database()
# 📊 Data Manager (forbedret)
class DataManager:
    def __init__(self):
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Sørg for at alle data-filer eksisterer"""
        files = ['users', 'reminders', 'shared_reminders', 'notifications', 'email_log', 'shared_notes']
        for filename in files:
            filepath = self.data_dir / f"{filename}.json"
            if not filepath.exists():
                initial_data = [] if filename in ['reminders', 'shared_reminders', 'notifications', 'email_log', 'shared_notes'] else {}
                self.save_data(filename, initial_data)
    
    def load_data(self, filename):
        """Last inn data fra JSON-fil med error handling"""
        filepath = self.data_dir / f"{filename}.json"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Feil ved lasting av {filename}: {e}")
            return [] if filename in ['reminders', 'shared_reminders', 'notifications', 'email_log'] else {}
    
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

# Legg til NoteForm her
class NoteForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired()])
    content = TextAreaField('Notat', validators=[DataRequired()])
    share_with = StringField('Del med (e-post)')
    submit = SubmitField('Lagre notat')

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
        conn = get_db_connection()
        if not conn:
            # Fallback til JSON
            users = dm.load_data('users')
            if user_id in users:
                user_data = users[user_id]
                return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
            return None
        
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash FROM users WHERE id = %s', (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        return None
    
    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        if not conn:
            # Fallback til JSON
            users = dm.load_data('users')
            for user_id, user_data in users.items():
                if user_data['email'] == email:
                    return User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
            return None
        
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        return None
    
    def save(self):
        """Lagre bruker til database"""
        conn = get_db_connection()
        if not conn:
            # Fallback til JSON
            users = dm.load_data('users')
            users[self.id] = {
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'created': datetime.now().isoformat()
            }
            dm.save_data('users', users)
            return
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', (self.id, self.username, self.email, self.password_hash))
        conn.commit()
        cursor.close()
        conn.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# 📧 E-post funksjoner
def send_email(to, subject, template, **kwargs):
    """Send e-post med template"""
    try:
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            logger.warning(f"E-post ble ikke sendt: Mangler MAIL_USERNAME eller MAIL_PASSWORD")
            return False
            
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=render_template(template, **kwargs),
            sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
        )
        mail.send(msg)
        logger.info(f"E-post sendt til {to}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Feil ved sending av e-post til {to}: {e}")
        return False
        
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
        
# E-post konfigurering
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

def send_reminder_notification(reminder, recipient_email):
    """Send påminnelse-notifikasjon via e-post"""
    subject = f"🔔 Påminnelse: {reminder['title']}"
    
    send_email(
        to=recipient_email,
        subject=subject,
        template='emails/reminder_notification.html',
        reminder=reminder,
        recipient=recipient_email
    )

def send_shared_reminder_notification(reminder, shared_by, recipient_email):
    """Send notifikasjon om delt påminnelse"""
    subject = f"👥 Ny delt påminnelse fra {shared_by}: {reminder['title']}"
    
    send_email(
        to=recipient_email,
        subject=subject,
        template='emails/shared_reminder.html',
        reminder=reminder,
        shared_by=shared_by,
        recipient=recipient_email
    )

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

# Planlegg automatisk sjekking av påminnelser
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
        
        # Opprett og lagre bruker
        user = User(user_id, form.username.data, form.username.data, password_hash)
        user.save()  # Nå bruker vi den forbedrede save-metoden
        
        # Logg inn bruker
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
    
    # Hent notater - NYTT
    notes = dm.load_data('shared_notes')
    my_notes = [n for n in notes if n.get('user_id') == current_user.email][:3]
    shared_notes = [n for n in notes if current_user.email in n.get('shared_with', [])][:3]
    
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
                         current_time=datetime.now(),
                         my_notes=my_notes,        # NYTT
                         shared_notes=shared_notes) # NYTT
@app.route('/notes')
@login_required
def notes():
    notes = dm.load_data('shared_notes')
    my_notes = [n for n in notes if n['user_id'] == current_user.email]
    shared_with_me = [n for n in notes if current_user.email in n.get('shared_with', [])]
    
    form = NoteForm()
    
    return render_template('notes.html', 
                          form=form,
                          my_notes=my_notes,
                          shared_notes=shared_with_me)

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    form = NoteForm()
    
    if form.validate_on_submit():
        # Del opp e-poster
        share_with = []
        if form.share_with.data:
            share_with = [email.strip() for email in form.share_with.data.split(',')]
        
        note_id = str(uuid.uuid4())
        new_note = {
            'id': note_id,
            'user_id': current_user.email,
            'title': form.title.data,
            'content': form.content.data,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'shared_with': share_with
        }
        
        # Lagre notat
        notes = dm.load_data('shared_notes')
        notes.append(new_note)
        dm.save_data('shared_notes', notes)
        
        # Send e-post hvis delt
        if share_with:
            for email in share_with:
                try:
                    send_note_shared_notification(new_note, current_user.email, email)
                except:
                    pass
            
            flash(f'Notat opprettet og delt med {len(share_with)} personer!', 'success')
        else:
            flash('Notat opprettet!', 'success')
    
    return redirect(url_for('notes'))
        
@app.route('/add_reminder', methods=['POST'])
@login_required
def add_reminder():
    form = ReminderForm()
    
    if form.validate_on_submit():
        # Hent deling-data fra request
        share_with = request.form.getlist('share_with')
        # Fjern tomme verdier og duplikater
        share_with = list(set([email.strip() for email in share_with if email.strip()]))
        
        # Valider e-postadresser
        import re
        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        valid_emails = [email for email in share_with if email_pattern.match(email)]
        
        if len(valid_emails) < len(share_with):
            flash('Noen e-postadresser var ugyldige og ble ikke lagt til.', 'warning')
        
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
            'shared_with': valid_emails
        }
        
        # Lagre påminnelse
        reminders = dm.load_data('reminders')
        reminders.append(new_reminder)
        dm.save_data('reminders', reminders)
        
        # Opprett delte påminnelser og send notifikasjoner
        if valid_emails:
            shared_reminders = dm.load_data('shared_reminders')
            
            for recipient in valid_emails:
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
                try:
                    send_shared_reminder_notification(shared_reminder, current_user.email, recipient)
                except Exception as e:
                    logger.error(f"Kunne ikke sende e-post til {recipient}: {e}")
            
            dm.save_data('shared_reminders', shared_reminders)
            flash(f'Påminnelse "{form.title.data}" opprettet og delt med {len(valid_emails)} personer!', 'success')
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

@app.route('/health')
def health_check():
    """Health check endpoint for produksjon"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# 🚨 Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# Template filters
@app.template_filter('as_datetime')
def as_datetime(date_string):
    try:
        return datetime.fromisoformat(date_string.replace(' ', 'T'))
    except:
        return datetime.now()
# Legg til disse rutene i app.py
@app.route('/shared_notes')
@login_required
def shared_notes():
    """Vis oversikt over alle felles notater brukeren har tilgang til"""
    all_notes = dm.load_data('shared_notes')
    
    # Filtrer notater brukeren har tilgang til
    user_notes = []
    for note in all_notes:
        for member in note.get('members', []):
            if member['email'] == current_user.email:
                user_notes.append(note)
                break
    
    return render_template('shared_notes.html', notes=user_notes)

@app.route('/create_shared_note', methods=['GET', 'POST'])
@login_required
def create_shared_note():
    """Opprett et nytt felles notat"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content', '')
        
        if not title:
            flash('Tittel er påkrevd', 'error')
            return redirect(url_for('create_shared_note'))
        
        # Generer unik ID og tilgangskode
        note_id = str(uuid.uuid4())
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        new_note = {
            'id': note_id,
            'title': title,
            'content': content,
            'created_by': current_user.email,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'access_code': access_code,
            'members': [
                {
                    'email': current_user.email,
                    'role': 'owner',
                    'joined_at': datetime.now().isoformat()
                }
            ],
            'messages': []
        }
        
        # Lagre notatet
        notes = dm.load_data('shared_notes')
        notes.append(new_note)
        dm.save_data('shared_notes', notes)
        
        flash(f'Notat "{title}" opprettet! Tilgangskode: {access_code}', 'success')
        return redirect(url_for('view_shared_note', note_id=note_id))
    
    return render_template('create_shared_note.html')

@app.route('/shared_note/<note_id>')
@login_required
def view_shared_note(note_id):
    """Vis et felles notat"""
    notes = dm.load_data('shared_notes')
    
    # Finn notatet
    note = None
    for n in notes:
        if n['id'] == note_id:
            note = n
            break
    
    if not note:
        flash('Notatet ble ikke funnet', 'error')
        return redirect(url_for('shared_notes'))
    
    # Sjekk tilgang
    has_access = False
    for member in note.get('members', []):
        if member['email'] == current_user.email:
            has_access = True
            break
    
    if not has_access:
        flash('Du har ikke tilgang til dette notatet', 'error')
        return redirect(url_for('shared_notes'))
    
    return render_template('view_shared_note.html', note=note)

@app.route('/update_shared_note/<note_id>', methods=['POST'])
@login_required
def update_shared_note(note_id):
    """Oppdater innholdet i et felles notat"""
    notes = dm.load_data('shared_notes')
    
    # Finn notatet og sjekk tilgang
    note_index = None
    for i, note in enumerate(notes):
        if note['id'] == note_id:
            has_access = False
            for member in note.get('members', []):
                if member['email'] == current_user.email:
                    has_access = True
                    break
            
            if has_access:
                note_index = i
            break
    
    if note_index is None:
        flash('Notatet ble ikke funnet eller du har ikke tilgang', 'error')
        return redirect(url_for('shared_notes'))
    
    # Oppdater innholdet
    content = request.form.get('content', '')
    notes[note_index]['content'] = content
    notes[note_index]['updated_at'] = datetime.now().isoformat()
    
    # Lagre endringer
    dm.save_data('shared_notes', notes)
    
    flash('Notatet ble oppdatert', 'success')
    return redirect(url_for('view_shared_note', note_id=note_id))

@app.route('/join_shared_note', methods=['GET', 'POST'])
@login_required
def join_shared_note():
    """Bli med i et eksisterende notat via tilgangskode"""
    if request.method == 'POST':
        access_code = request.form.get('access_code')
        
        if not access_code:
            flash('Tilgangskode er påkrevd', 'error')
            return redirect(url_for('join_shared_note'))
        
        notes = dm.load_data('shared_notes')
        
        # Finn notatet med tilgangskoden
        note_index = None
        for i, note in enumerate(notes):
            if note.get('access_code') == access_code:
                note_index = i
                break
        
        if note_index is None:
            flash('Ingen notat funnet med denne tilgangskoden', 'error')
            return redirect(url_for('join_shared_note'))
        
        # Sjekk om brukeren allerede er medlem
        for member in notes[note_index].get('members', []):
            if member['email'] == current_user.email:
                flash('Du er allerede medlem av dette notatet', 'info')
                return redirect(url_for('view_shared_note', note_id=notes[note_index]['id']))
        
        # Legg til brukeren som medlem
        notes[note_index]['members'].append({
            'email': current_user.email,
            'role': 'editor',
            'joined_at': datetime.now().isoformat()
        })
        
        # Lagre endringer
        dm.save_data('shared_notes', notes)
        
        flash(f'Du har blitt med i notatet "{notes[note_index]["title"]}"', 'success')
        return redirect(url_for('view_shared_note', note_id=notes[note_index]['id']))
    
    return render_template('join_shared_note.html')

@app.route('/test-email')
def test_email():
    if current_user.is_authenticated:
        recipient = current_user.email
    else:
        recipient = request.args.get('email')
        
    if not recipient:
        return "Mangler e-postadresse", 400
        
    # Test sending av e-post
    success = send_email(
        to=recipient,
        subject="Test fra Smart Påminner Pro",
        template='emails/test_email.html',
        name=current_user.username if current_user.is_authenticated else "Test"
    )
    
    return f"E-post {'sendt' if success else 'FEILET'} til {recipient}"
        
@app.route('/add_message_to_note/<note_id>', methods=['POST'])
@login_required
def add_message_to_note(note_id):
    """Legg til en chatmelding i notatet"""
    message = request.form.get('message')
    
    if not message:
        flash('Meldingen kan ikke være tom', 'error')
        return redirect(url_for('view_shared_note', note_id=note_id))
    
    notes = dm.load_data('shared_notes')
    
    # Finn notatet og sjekk tilgang
    note_index = None
    for i, note in enumerate(notes):
        if note['id'] == note_id:
            has_access = False
            for member in note.get('members', []):
                if member['email'] == current_user.email:
                    has_access = True
                    break
            
            if has_access:
                note_index = i
            break
    
    if note_index is None:
        flash('Notatet ble ikke funnet eller du har ikke tilgang', 'error')
        return redirect(url_for('shared_notes'))
    
    # Legg til meldingen
    message_id = str(uuid.uuid4())
    notes[note_index]['messages'].append({
        'id': message_id,
        'sender': current_user.email,
        'sender_name': current_user.username,
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Lagre endringer
    dm.save_data('shared_notes', notes)
    
    return redirect(url_for('view_shared_note', note_id=note_id))
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
