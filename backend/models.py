from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security.core import UserMixin, RoleMixin
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index = True)
    password = db.Column(db.String, nullable=False)
    fs_uniquifier= db.Column(db.String, unique = True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship("Role", backref="bearers", secondary="user_roles") # type: ignore
    attempts = db.relationship("Attempt", cascade="all, delete-orphan", backref="user")
    
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    
class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id", ondelete='CASCADE'))
    
subject_chapter_association = db.Table("subject_chapter_association",
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), primary_key=True),
    db.Column("chapter_id", db.Integer, db.ForeignKey("chapter.id", ondelete="CASCADE"), primary_key=True))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String, nullable=False)
    chapters = db.relationship("Chapter", secondary=subject_chapter_association, back_populates="subjects")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    subjects = db.relationship("Subject", secondary=subject_chapter_association, back_populates="chapters")
    quizzes = db.relationship("Quiz", cascade = "all, delete-orphan", backref="chapter")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    total_marks = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, default=30)
    questions = db.relationship("Question", cascade = "all, delete-orphan", backref="quiz")
    attempt = db.relationship("Attempt", cascade = "all, delete-orphan", backref="quiz")
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'))
    question_statement = db.Column(db.Text, nullable=False)
    ans_type = db.Column(db.String, nullable=False)  # 'single', 'multiple', 'numeric'
    options = db.Column(db.JSON, nullable=True)  # Only for single/multiple-choice questions
    correct_options = db.Column(db.JSON, nullable=True)  # Only for single/multiple-choice questions
    correct_min = db.Column(db.Float, nullable=True)  # Only for numerical answers
    correct_max = db.Column(db.Float, nullable=True)  # Only for numerical answers
    marks = db.Column(db.Integer, nullable=False)
    responses = db.relationship("Response", cascade = "all,delete-orphan", backref = "question")


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'))
    attempt_number = db.Column(db.Integer, nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.now())
    score = db.Column(db.Integer, default=0)
    responses = db.relationship('Response', backref='attempt', cascade='all, delete-orphan')
    
    

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempt.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    answer = db.Column(db.JSON)  # Can store multiple selected options or numeric input
    is_correct = db.Column(db.Boolean, default=False)