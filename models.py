from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    children = db.relationship('Child', backref='parent', lazy=True)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Drawing(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50))  # ✅ Add this line

    image_data = db.Column(db.Text, nullable=False)         # base64 image
    result = db.Column(db.Text, nullable=False)             # AI analysis result
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)

    child = db.relationship('Child', backref='drawings')

