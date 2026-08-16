from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120), nullable = False)
    content = db.Column(db.Text, nullable = False)
    category = db.Column(db.String(50), default = 'Общие')
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

    def short_content(self, length=80):
        if len(self.content) <= length:
            return self.content
        return self.content[:length].strip() + '...'