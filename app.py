from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import pyotp
import os
import time
from models import User, TwoFactor
from extensions import db
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized!')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('Login successful!')
        
        # Check if 2FA is enabled
        if user.two_factor and len(user.two_factor) > 0 and user.two_factor[0].is_active:
            return redirect(url_for('verify_2fa'))
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('2fa_verified', None)
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Check if 2FA is enabled but not verified
    if current_user.two_factor and len(current_user.two_factor) > 0 and current_user.two_factor[0].is_active:
        if not session.get('2fa_verified', False):
            return redirect(url_for('verify_2fa'))
    
    current_code = None
    time_remaining = 0
    
    if current_user.two_factor and len(current_user.two_factor) > 0 and current_user.two_factor[0].is_active:
        totp = pyotp.TOTP(current_user.two_factor[0].secret)
        current_code = totp.now()
        time_remaining = totp.interval - int(time.time()) % totp.interval
    
    return render_template('dashboard.html', 
                         current_code=current_code,
                         time_remaining=time_remaining)

@app.route('/api/current_2fa_code')
@login_required
def current_2fa_code():
    if current_user.two_factor and len(current_user.two_factor) > 0 and current_user.two_factor[0].is_active:
        totp = pyotp.TOTP(current_user.two_factor[0].secret)
        current_code = totp.now()
        time_remaining = totp.interval - int(time.time()) % totp.interval
        return {
            'code': current_code,
            'time_remaining': time_remaining,
            'interval': totp.interval
        }
    return {'error': '2FA not enabled'}, 404

@app.route('/setup-2fa')
@login_required
def setup_2fa():
    # Generate a random secret key for the user
    secret = pyotp.random_base32()
    
    # Create or update user's 2FA record
    if len(current_user.two_factor) == 0:
        two_factor = TwoFactor(user_id=current_user.id, secret=secret)
        db.session.add(two_factor)
    else:
        current_user.two_factor[0].secret = secret
        current_user.two_factor[0].is_active = False
    
    db.session.commit()
    
    # Generate QR code
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.username,
        issuer_name='2FA Demo App'
    )
    
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_code = base64.b64encode(buf.getvalue()).decode('ascii')
    
    return render_template('setup_2fa.html', secret=secret, qr_code=qr_code)

@app.route('/verify-2fa', methods=['GET', 'POST'])
@login_required
def verify_2fa():
    if request.method == 'POST':
        token = request.form['token']
        
        if current_user.two_factor and len(current_user.two_factor) > 0 and current_user.two_factor[0].secret:
            totp = pyotp.TOTP(current_user.two_factor[0].secret)
            if totp.verify(token):
                current_user.two_factor[0].is_active = True
                db.session.commit()
                session['2fa_verified'] = True
                flash('2FA verification successful!')
                return redirect(url_for('dashboard'))
        
        flash('Invalid token')
        return redirect(url_for('verify_2fa'))
    
    return render_template('verify_2fa.html')

if __name__ == '__main__':
    app.run(debug=True)
