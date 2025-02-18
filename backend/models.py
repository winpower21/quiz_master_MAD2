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
    attempts = db.relationship("Attempt", cascade="all,delete", backref="user")
    
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    
class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    
subject_chapter_association = db.Table("subject_chapter_association",
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), primary_key=True),
    db.Column("chapter_id", db.Integer, db.ForeignKey("chapter.id", ondelete="CASCADE"), primary_key=True))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String, nullable=False)
    chapters = db.relationship("Chapter", secondary=subject_chapter_association, back_populates="subjects")
    quizzes = db.relationship("Quiz", cascade = "all, delete", backref="subject")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    subjects = db.relationship("Subject", secondary=subject_chapter_association, back_populates="chapters")
    quizzes = db.relationship("Quiz", cascade = "all, delete", backref="chapter")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeighKey('subject.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    total_marks = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, nullable=True)
    questions = db.relationship("Question", cascade = "all, delete", backref="quiz")
    attempt = db.relationship("Attempt", cascade = "all, delete", backref="quiz")
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    statement = db.Column(db.Text, nullable=False)
    options = db.Column(JSON)
    range = db.Column(JSON)
    correct_answer = db.Column(JSON)
    marks = db.Column(db.Integer, nullable=False)
    responses = db.Column(db.Integer, cascade = "all,delete", backref = "question")
    
class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    attempt_number = db.Column(db.Integer, nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.now())
    score = db.Column(db.Integer, nullable=False)
    responses = db.relationship("Response", cascade="all,delete", backref="attempt")

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempt.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer = db.Column(JSON)
    is_correct = db.Column(db.Boolean, nullable=False)