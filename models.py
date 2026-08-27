from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Note(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120), nullable = False)
    content = db.Column(db.Text, nullable = False)
    category = db.Column(db.String(50), default = 'Общие')
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

    def short_content(self, length=80):
        if len(self.content) <= length:
            return self.content
        return self.content[:length].strip() + '...'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, orig_password):
        self.password_hash = generate_password_hash(orig_password)

    def check_password(self, orig_password):
        return check_password_hash(self.password_hash, orig_password)