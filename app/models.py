from datetime import datetime
from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    courses = db.relationship('Course', backref='user', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_content = db.Column(db.String(500), nullable=False)
    back_content = db.Column(db.String(500), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    reviews = db.relationship('Review', backref='flashcard', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_date = db.Column(db.Date, nullable=False)
    easiness_factor = db.Column(db.Float, default=2.5)
    consecutive_correct_answers = db.Column(db.Integer, default=0)
    last_reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Zapisz zawartość fiszki w momencie recenzji
    front_content_at_review = db.Column(db.String(500))
    back_content_at_review = db.Column(db.String(500))
    # Dodatkowe pole do ewentualnych notatek czy komentarzy użytkownika
    user_notes = db.Column(db.String(1000), nullable=True)