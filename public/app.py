from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json
import uuid
import re
import os
import secrets
import logging
from pathlib import Path

try:
    import psycopg2
except ImportError:
    psycopg2 = None
    
# Bruk DATABASE_URL direkte
database_url = os.getenv('DATABASE_URL')

# Eller bygg den fra individuelle variabler
if not database_url:
    database_url = f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"

# Koble til database
conn = psycopg2.connect(database_url)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'din-hemmelighets-nøkkel-her')

# Generer eller hent SECRET_KEY
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError("SECRET_KEY must be set in production!")
    else:
        secret_key = secrets.token_hex(32)
        print(f"Generated SECRET_KEY for development: {secret_key}")

app.config['SECRET_KEY'] = secret_key

# Serve manifest.json fra rot
@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

# Serve service worker fra rot
@app.route('/sw.js')
def service_worker():
    return send_from_directory('.', 'sw.js')

# Serve ikoner
@app.route('/icons/<path:filename>')
def serve_icons(filename):
    return send_from_directory('static/icons', filename)
    
# E-post konfigurering
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# Påminnelse innstillinger
app.config['NOTIFICATION_ADVANCE_MINUTES'] = 30
app.config['REMINDER_CHECK_INTERVAL'] = 300

# Extensions
csrf = CSRFProtect(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vennligst logg inn for å få tilgang til denne siden.'
login_manager.login_message_category = 'info'

# 📊 Data Manager - VIKTIG: Må være definert før vi bruker den!
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
            return [] if filename in ['reminders', 'shared_reminders', 'notifications', 'email_log', 'shared_notes'] else {}
    
    def save_data(self, filename, data):
        """Lagre data til JSON-fil"""
        filepath = self.data_dir / f"{filename}.json"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Feil ved lagring av {filename}: {e}")
            raise

# Global data manager - MÅ DEFINERES FØR vi bruker den!
dm = DataManager()

# Database setup
def init_db():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("ADVARSEL: Ingen DATABASE_URL funnet - bruker JSON-lagring")
        return False
        
    if not psycopg2:
        print("psycopg2 ikke installert - kan ikke bruke database")
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
    if DATABASE_URL and psycopg2:
        try:
            return psycopg2.connect(DATABASE_URL)
        except:
            pass
    print("Ingen database tilkobling - bruker JSON filer")
    return None

# Scheduler for e-post notifikasjoner
scheduler = BackgroundScheduler()
scheduler.start()

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

class NoteForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired()])
    content = TextAreaField('Notat', validators=[DataRequired()])
    share_with = StringField('Del med (e-post)')
    submit = SubmitField('Lagre notat')

# 👤 User Class - Bruker dm som nå er definert først
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

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# E-post funksjoner
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

def send_shared_reminder_notification(reminder, shared_by, recipient_email):
    """Send notifikasjon om delt påminnelse"""
    subject = f"👥 Ny delt påminnelse fra {shared_by}: {reminder['title']}"
    
    try:
        return send_email(
            to=recipient_email,
            subject=subject,
            template='emails/shared_reminder.html',
            reminder=reminder,
            shared_by=shared_by
        )
    except Exception as e:
        logger.error(f"Feil ved sending av delt påminnelse: {e}")
        
        # Enkel HTML e-post som fallback
        html_body = f"""
        <h2>Ny delt påminnelse</h2>
        <p><strong>{shared_by}</strong> har delt en påminnelse med deg:</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3>{reminder['title']}</h3>
            <p><strong>Beskrivelse:</strong> {reminder.get('description', 'Ingen beskrivelse')}</p>
            <p><strong>Tid:</strong> {reminder['datetime']}</p>
            <p><strong>Prioritet:</strong> {reminder['priority']}</p>
        </div>
        """
        
        try:
            if app.config['MAIL_USERNAME']:
                msg = Message(
                    subject=subject,
                    recipients=[recipient_email],
                    html=html_body,
                    sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
                )
                mail.send(msg)
                return True
        except:
            pass
        
        return False

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
            # Test å sende e-post direkte uten template
            try:
                if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                    subject = f"🔔 Påminnelse: {reminder['title']}"
                    html_content = f"""
                    <h2>Påminnelse: {reminder['title']}</h2>
                    <p>Dette er en påminnelse om at du har en oppgave som snart forfaller.</p>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                        <h3>{reminder['title']}</h3>
                        <p><strong>Beskrivelse:</strong> {reminder.get('description', 'Ingen beskrivelse')}</p>
                        <p><strong>Tid:</strong> {reminder['datetime']}</p>
                        <p><strong>Prioritet:</strong> {reminder['priority']}</p>
                    </div>
                    """
                    
                    msg = Message(
                        subject=subject,
                        recipients=[recipient_email],
                        html=html_content,
                        sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
                    )
                    mail.send(msg)
                    
                    # Logg notifikasjon
                    notifications.append({
                        'reminder_id': reminder['id'],
                        'recipient': recipient_email,
                        'sent_at': now.isoformat(),
                        'type': 'reminder_notification'
                    })
                    print(f"Påminnelse sendt til {recipient_email}: {reminder['title']}")
            except Exception as e:
                print(f"Feil ved sending av påminnelse: {e}")
        
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
    id='check_reminders_for_notifications'
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
                         my_notes=my_notes,
                         shared_notes=shared_notes)

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

@app.route('/notes')
@login_required
def notes():
    notes = dm.load_data('shared_notes')
    my_notes = [n for n in notes if n.get('user_id') == current_user.email]
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
        
        flash('Notat opprettet!', 'success')
    
    return redirect(url_for('notes'))

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

@app.route('/health')
def health_check():
    """Health check endpoint for produksjon"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
