from flask_restful import Api, Resource, fields, marshal_with
from flask import jsonify, request
from .models import Subject, Chapter, Quiz, Question, db
from flask_security.decorators import auth_required, roles_required, roles_accepted

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
    # GET ALL SUBJECTS
    @marshal_with(subject_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self): 
        subjects = Subject.query.all()
        if not subjects:
            return jsonify({"message": "No subjects found"}), 404
        return subjects
    
    # CREATE NEW SUBJECT
    @auth_required('token')
    @roles_required('admin')
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        image_url = data.get('image_url')
        if not name or not description or not image_url:
            return jsonify({'message': 'Invalid inputs'}), 400
        subject = Subject(name=name, description=description, image_url=image_url) # type: ignore 
        try:
            db.session.add(subject)
            db.session.commit()
            return jsonify({'message': 'Subject created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating subject: {e}"}), 500

class SubjectIdAPI(Resource):
    # GET A SUBJECT BY ID
    @marshal_with(subject_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
        return subject
    
    # DELETE A SUBJECT BY ID
    @auth_required('token')
    @roles_required('admin')
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject does not exist'}), 404
        try:
            db.session.delete(subject)
            db.session.commit()
            return jsonify({'message': 'Subject deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error deleting subject: {e}"}), 500


class ChapterAPI(Resource):
    # GET ALL CHAPTERS (TEMPORARY FOR TESTING)
    @marshal_with(chapter_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self): 
        chapters = Chapter.query.all()
        if not chapters:
            return jsonify({"message": "No subjects found"}), 404
        return chapters
    
    # CREATE NEW SUBJECT
    @auth_required('token')
    @roles_required('admin')
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        subject_id = data.get('subject_id')
        if not name or not description:
            return jsonify({'message': 'Invalid inputs'}), 400
        chapter = Chapter(name=name, description=description) # type: ignore
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
        try:
            db.session.add(chapter)
            subject.chapters.extend([chapter])
            db.session.commit()
            return jsonify({'message': 'Chapter created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating chapter: {e}"}, 500

class ChapterIdAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self, chapter_id):      
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
        return chapter
    
    @auth_required('token')
    @roles_required('admin')
    def delete(self, chapter_id):
        chapter = Chapter().query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter does not exist'}), 404
        try:
            db.session.delete(chapter)
            db.session.commit()
            return jsonify({'message': 'Chapter deleted successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error deleting chapter: {e}"}, 500

class SubjectChaptersAPI(Resource):
    # GET CHAPTERS FOR A SUBJECT
    @marshal_with(chapter_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject does not exist'}), 404
        else:
            chapters = subject.chapters
            return chapters
    
class ChapterQuizAPI(Resource):
    # GET QUIZZES FOR A CHAPTER
    @marshal_with(quiz_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self, chapter_id):
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            return jsonify({'message': 'Chapter does not exist'}), 400
        quizzes = chapter.quizzes
        if not quizzes:
            return jsonify({'message': 'No quizzes for this chapter'}),400
        return quizzes

class QuizAPI(Resource):
    # GET ALL QUIZZES (TEMPORARY FOR TESTING)
    @marshal_with(quiz_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self):
        quizzes = Quiz.query.all()
        if not quizzes:
            return jsonify({'message':'No quizzes created'}), 404
        return quizzes
        

    # CREATE NEW QUIZ
    @auth_required('token')
    @roles_required('admin')
    @roles_accepted('admin')
    def post(self):
        data = request.get_json()
        # Validate required fields
        required_fields = ["name", "description", "chapter_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"message":f"Missing requrired fields: {', '.join(missing_fields)}"}), 404
        
        if not data.get("questions"):
            return jsonify({"message":"Quiz must have atleast one question."}), 400
        
        try:
            with db.session.begin_nested():
                quiz = Quiz(
                    name = data["name"],
                    desscription = data["description"],
                    chapter_id = data["chapter_id"]
                )
                db.session.add(quiz)
                db.session.flush()

                for q in data["questions"]:
                    question = Question(
                        quiz_id = quiz.id,
                        question_statement = q.get("question_statement"),
                        ans_type = q.get("type"),
                        options = q.get("options"),
                        correct_range = q.get("correct_num_range"),
                        correct_ans = q.get("correct_ans"),
                        marks = q.get("marks")
                    )
                    db.session.add(question)
                db.session.commit()
            return jsonify({"message":"Quiz created successfully."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message":f"Error creating quiz {str(e)}"})



class QuizIdAPI(Resource):
    @marshal_with(quiz_fields)
    @auth_required('token')
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz does not exist'}),404
        return quiz
    
    @auth_required('token')
    @roles_required('admin')
    def delete(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz does not exist'}), 404
        try:
            db.session.delete(quiz)
            db.session.commit()
            return jsonify({'message': 'Quiz deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error deleting quiz {e}'}), 500




class QuestionsAPI(Resource):
    # GET QUSTIONS FOR A QUIZ
    @marshal_with(question_fields)
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Chapter does not exist'}), 400
        questions = quiz.questions
        return questions
    
    # Incorrect Implementation
    # # CREATE A QUESTION
    # @auth_required('token')
    # @roles_required('admin')
    # def post(self):
    #     data = request.get_json()
    #     question_statement = data.get('question_statement')
    #     options = data.get('options')
    #     correct_options = data.get('correct_options')
    #     marks = data.get('marks')
    #     quiz_id = data.get('quiz_id')
    #     if not question_statement or options or correct_options or marks or quiz_id:
    #         return jsonify({'message': 'Invalid inputs'}), 404
    #     quiz = Quiz.query.get(quiz_id)
    #     try: 
    #         question = Question(question_statement=question_statement, options=options, correct_options=correct_options, marks=marks) # type: ignore
    #         db.session.add(question)
    #         quiz.questions.extend([question]) # type: ignore
    #         db.session.commit()
    #         return jsonify({'message': 'Question created successfully'}), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({'message': f'Error creating question {e}'}), 500
        
class QuestionIdAPI(Resource):
    # # Not required
    # @marshal_with(question_fields)
    # @auth_required('token')
    # @roles_accepted('admin','user')
    # def get(self, question_id):
    #     question = Question.query.get(question_id)
    #     if not question:
    #         return jsonify({'message': 'Question does not exist'}), 400
    #     return question
                
    @auth_required('token')
    @roles_required('admin')
    def delete(self, question_id):
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Question does not exist'}), 400
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'message': 'Question deleted succeessfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error deleting question {e}'}), 401
        
        
api.add_resource(SubjectAPI, "/subject") # Get list of all subjects or create a new subject
api.add_resource(SubjectIdAPI, '/subject/<int:subject_id>') 
api.add_resource(ChapterAPI, '/chapter')
api.add_resource(ChapterIdAPI, '/chapter/<int:chapter_id>')
api.add_resource(SubjectChaptersAPI, '/subject/<int:subject_id>/chapter')
api.add_resource(QuizAPI, '/quiz')
api.add_resource(QuizIdAPI, '/quiz/<int:quiz_id>')
api.add_resource(QuestionsAPI, '/question')
api.add_resource(QuestionIdAPI, '/question/<int:question_id>')
