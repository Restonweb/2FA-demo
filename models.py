from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    @property
    def is_active(self):
        return True
        
    @property
    def is_authenticated(self):
        return True
        
    def get_id(self):
        return str(self.id)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TwoFactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    secret = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='two_factor')
