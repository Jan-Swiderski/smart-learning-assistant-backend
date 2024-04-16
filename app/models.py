from datetime import datetime
from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(256), nullable=False)
    courses = db.relationship('Course', backref='user', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcards = db.relationship('Flashcard', backref='course', lazy=True)

flashcard_responses = db.Table('flashcard_responses',
    db.Column('response_direction_a_id', db.Integer, db.ForeignKey('flashcard.id'), primary_key=True),
    db.Column('response_direction_b_id', db.Integer, db.ForeignKey('flashcard.id'), primary_key=True)
    )    

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    responses = db.relationship('Flashcard', secondary='flashcard_responses',
                                primaryjoin=id==flashcard_responses.c.response_direction_a_id,
                                secondaryjoin=id==flashcard_responses.c.response_direction_b_id,
                                backref='response_to')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    easiness_factor = db.Column(db.Float, default=2.5)
    quality_of_review = db.Column(db.Integer, default=0)
    next_review_date = db.Column(db.DateTime)
    consecutive_correct_answers = db.Column(db.Integer, default=0)
    last_reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    front_content_at_review = db.Column(db.String(500))
    back_content_at_review = db.Column(db.String(500))
    user_notes = db.Column(db.String(1000), nullable=True)