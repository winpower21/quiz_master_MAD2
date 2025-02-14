from flask_restful import Api, Resource, fields, marshal_with
from flask import jsonify, request, make_response
from .models import Subject, Chapter, Quiz, Question, db
from flask_security.decorators import auth_required

api = Api(prefix="/api")


question_fields = {
    'id': fields.Integer,
    'question': fields.String,
    'options': fields.List(fields.String),
    'correct_options': fields.List(fields.Integer),
    'marks': fields.Integer
}

quiz_fields = {
    'id': fields.Integer,
    'chapter_id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'questions': fields.List(fields.Nested(question_fields))
}

chapter_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'quizzes': fields.List(fields.Nested(quiz_fields))
}

subject_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'image_url': fields.String,
    'chapters': fields.List(fields.Nested(chapter_fields))
}


class SubjectAPI(Resource):
    @marshal_with(subject_fields)
    @auth_required('token')
    def get(self): # Get list of all subjects
        subjects = Subject.query.all()
        if not subjects:
            return make_response(jsonify({"message": "No subjects found"}), 400)
        return subjects
    
    @auth_required('token')
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        image_url = data.get('image_url')
        if not name or not description or not image_url:
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        subject = Subject(name=name, description=description, image_url=image_url) # type: ignore 
        try:
            db.session.add(subject)
            db.session.commit()
            return make_response(jsonify({'message': 'Subject created successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating subject: {e}"}, 401

class SubjectIdAPI(Resource):
    @marshal_with(subject_fields)
    @auth_required('token')
    def get(self, id):
        subject = Subject.query.get(id)
        if not subject:
            return make_response(jsonify({'message': 'Subject not found'}), 400)
        return subject
    
    @auth_required('token')
    def delete(self,id):
        subject = Subject.query.get(id)
        if not subject:
            return make_response(jsonify({'message': 'Subject does not exist'}), 400)
        try:
            db.session.delete(subject)
            db.session.commit()
            return make_response(jsonify({'message': 'Subject deleted successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error deleting subject: {e}"}, 401


class ChapterAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self): # Get list of all subjects
        chapters = Chapter.query.all()
        if not chapters:
            return make_response(jsonify({"message": "No subjects found"}), 400)
        return chapters
    
    @auth_required('token')
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        subject_id = data.get('subject_id')
        if not name or not description:
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        chapter = Chapter(name=name, description=description) # type: ignore
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            return make_response(jsonify({'message': 'Subject not found'}), 400)
        try:
            db.session.add(chapter)
            subject.chapters.extend([chapter])
            db.session.commit()
            return make_response(jsonify({'message': 'Chapter created successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating chapter: {e}"}, 401

class ChapterIdAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self, id):
        chapter = Chapter.query.get(id)
        if not chapter:
            return make_response(jsonify({'message': 'Chapter not found'}), 400)
        return chapter
    
    @auth_required('token')
    def delete(self,id):
        chapter = Chapter().query.get(id)
        if not chapter:
            return make_response(jsonify({'message': 'Chapter does not exist'}), 400)
        try:
            db.session.delete(chapter)
            db.session.commit()
            return make_response(jsonify({'message': 'Chapter deleted successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error deleting chapter: {e}"}, 401

class SubjectChaptersAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self, id):
        subject = Subject.query.filter_by(id=id).first()
        if not subject:
            print('Not Done')
            return make_response(jsonify({'message': 'Subject does not exist'}), 400)
        else:
            chapters = subject.chapters
            print('Done')
            return chapters
    
class QuizAPI(Resource):
    @marshal_with(quiz_fields)
    @auth_required('token')
    def get(self):
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        if not chapter_id:
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            return make_response(jsonify({'message': 'Chapter does not exist'}), 400)
        quizzes = chapter.quizzes
        if not quizzes:
            return make_response(jsonify({'message': 'No quizzes for this chapter'}),400)
        return quizzes

    @auth_required('token')
    def post(self):
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        name = data.get('name')
        description = data.get('description')
        total_marks = data.get('total_marks')
        if not chapter_id or not name or not description or not total_marks:
            print('fail1')
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            print('fail2')
            return make_response(jsonify({'message': 'Chapter not found'}), 400)
        try:
            print('done3')
            quiz = Quiz(chapter_id = chapter_id, name=name, description=description, total_marks=total_marks) # type: ignore
            db.session.add(quiz)
            chapter.quizzes.extend([quiz])
            db.session.commit()
            return make_response(jsonify({'message': 'Quiz created successfully'}), 200)
        except Exception as e:
            print('fail4')
            db.session.rollback()
            return {"message": f"Error creating quiz: {e}"}, 401
        

class QuizIdAPI(Resource):
    @marshal_with(quiz_fields)
    @auth_required('token')
    def get(self, id):
        quiz = Quiz.query.get(id)
        if not quiz:
            return make_response(jsonify({'message': 'Quiz does not exist'}),400)
        return quiz
    
    @auth_required('token')
    def delete(self, id):
        quiz = Quiz.query.get(id)
        if not quiz:
            return make_response(jsonify({'message': 'Quiz does not exist'}),400)
        try:
            db.session.delete(quiz)
            db.session.commit()
            return make_response(jsonify({'message': 'Quiz deleted successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': f'Error deleting quiz {e}'}), 401)

class QuestionsAPI(Resource):
    @marshal_with(question_fields)
    @auth_required('token')
    def get(self):
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        if not quiz_id:
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return make_response(jsonify({'message': 'Chapter does not exist'}), 400)
        questions = quiz.questions
        return questions
    
    @auth_required('token')
    def post(self):
        data = request.get_json()
        question_statement = data.get('question_statement')
        options = data.get('options')
        correct_options = data.get('correct_options')
        marks = data.get('marks')
        quiz_id = data.get('quiz_id')
        if not question_statement or options or correct_options or marks or quiz_id:
            return make_response(jsonify({'message': 'Invalid inputs'}), 400)
        quiz = Quiz.query.get(quiz_id)
        try: 
            question = Question(question_statement=question_statement, options=options, correct_options=correct_options, marks=marks) # type: ignore
            db.session.add(question)
            quiz.questions.extend([question]) # type: ignore
            db.session.commit()
            return make_response(jsonify({'message': 'Question created successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': f'Error creating question {e}'}), 401)
        
class QuestionIdAPI(Resource):
    @marshal_with(question_fields)
    @auth_required('token')
    def get(self, question_id):
        question = Question.query.get(question_id)
        if not question:
            return make_response(jsonify({'message': 'Question does not exist'}), 400)
        return question
                
    @auth_required('token')
    def delete(self, question_id):
        question = Question.query.get(question_id)
        if not question:
            return make_response(jsonify({'message': 'Question does not exist'}), 400)
        try:
            db.session.delete(question)
            db.session.commit()
            return make_response(jsonify({'message': 'Question deleted succeessfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': f'Error deleting question {e}'}), 401)
        
        
api.add_resource(SubjectAPI, "/subjects") # Get list of all subjects or create a new subject
api.add_resource(SubjectIdAPI, '/subjects/<int:id>') 
api.add_resource(ChapterAPI, '/chapters')
api.add_resource(ChapterIdAPI, '/chapters/<int:id>')
api.add_resource(SubjectChaptersAPI, '/subjects/chapters/<int:id>')
api.add_resource(QuizAPI, '/quizzes')
api.add_resource(QuizIdAPI, '/quizzes/<int:id>')
api.add_resource(QuestionsAPI, '/questions')
api.add_resource(QuestionIdAPI, '/questions/<int:id>')
