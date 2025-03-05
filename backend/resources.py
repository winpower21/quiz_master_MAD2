from flask_restful import Api, Resource, fields, marshal_with, abort
from flask import request
from .models import Subject, Chapter, Quiz, Question, Attempt, Response, db, subject_chapter_association
from flask_security.decorators import auth_required, roles_required, roles_accepted

api = Api(prefix="/api")

response_fields = {
    "id": fields.Integer,
    "question_id": fields.Integer,
    "attempt_id": fields.Integer,
    "answer": fields.String,
    "is_correct": fields.Boolean
}

attempts_fields = {
    "student_id": fields.Integer,
    "quiz_id":fields.Integer,
    "attempt_number":fields.Integer,
    "attempt_date":fields.DateTime,
    "score":fields.Integer
}


question_fields = {
    "id": fields.Integer,
    "quiz_id":fields.Integer,
    "question_statement": fields.String,
    "ans_type": fields.String,
    "options": fields.List(fields.String),
    "marks": fields.Integer
}

quiz_fields_with_questions = {
    "id": fields.Integer,
    "chapter_id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "total_marks": fields.Integer,
    "time_limit": fields.Integer,
    "questions": fields.List(fields.Nested(question_fields))
}
quiz_fields = {
    "id": fields.Integer,
    "chapter_id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "total_marks": fields.Integer,
    "time_limit": fields.Integer,
}

chapter_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "quizzes": fields.List(fields.Nested(quiz_fields))
}

subject_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "image_url": fields.String,
    "chapters": fields.List(fields.Nested(chapter_fields))
}

def sendResponse(status=200, message="", data=None):
    sendResponse={"message":message}
    if data:
        sendResponse["data"]=data
    return sendResponse, status


class SubjectAPI(Resource):
    # GET ALL SUBJECTS
    @marshal_with(subject_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self): 
        subjects = Subject.query.all()
        if not subjects:
            abort(404, message="No subjects found")
        return subjects
    
    # CREATE NEW SUBJECT
    @auth_required("token")
    @roles_required("admin")
    def post(self):
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        image_url = data.get("image_url")
        if not name or not description or not image_url:
            abort(400, message="Invalid inputs")
            #return jsonify({"message": "Invalid inputs"}), 400
        existing_subject = Subject.query.filter_by(name=name).first()
        if not existing_subject:
            subject = Subject(name=name, description=description, image_url=image_url) # type: ignore 
            try:
                db.session.add(subject)
                db.session.commit()
                return sendResponse(201, message="Subject created successfully")
                #return jsonify({"message": "Subject created successfully"}), 201
            except Exception as e:
                db.session.rollback()
                abort(500, message=f"Error creating subject: {e}")
                #return jsonify({"message": f"Error creating subject: {e}"}), 500
        else:
            abort(409, message=f"Subject with name: {existing_subject.name}, already exists.")

class SubjectIdAPI(Resource):
    # GET A SUBJECT BY ID
    @marshal_with(subject_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            abort(404, message="Subject not found")
            #return jsonify({"message": "Subject not found"}), 404
        return subject
    
    # DELETE A SUBJECT BY ID
    @auth_required("token")
    @roles_required("admin")
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            abort(404, message="Subject does not exist")
            #return jsonify({"message": "Subject does not exist"}), 404
        try:
            db.session.delete(subject)
            db.session.commit()
            return sendResponse(200, message=f"Subject '{subject.name}' deleted successfully")
            #return jsonify({"message": "Subject deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error deleting subject: {e}")
            #return jsonify({"message": f"Error deleting subject: {e}"}), 500


class ChapterAPI(Resource):
    # GET ALL CHAPTERS (TEMPORARY FOR TESTING)
    @marshal_with(chapter_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self): 
        chapters = Chapter.query.all()
        if not chapters:
            abort(404, message="No subjects found")
            #return jsonify({"message": "No subjects found"}), 404
        return chapters
    
    # CREATE NEW SUBJECT
    @auth_required("token")
    @roles_required("admin")
    def post(self):
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        subject_id = data.get("subject_id")
        if not name or not description or not subject_id:
            abort(400, message="Invalid inputs")
            #return jsonify({"message": "Invalid inputs"}), 400
        
        subject = Subject.query.filter_by(id=subject_id).first()
        if not subject:
            return sendResponse(404, message="Subject not found")
            #return jsonify({"message": "Subject not found"}), 404
        existing_chapter = db.session.query(Chapter.id).join(subject_chapter_association).join(Subject).filter(Subject.id == subject.id , Chapter.name == name).first()
        if not existing_chapter:
            chapter = Chapter(name=name, description=description) # type: ignore
            try:
                db.session.add(chapter)
                subject.chapters.extend([chapter])
                db.session.commit()
                return sendResponse(201, message="Chapter created successfully")
                #return jsonify({"message": "Chapter created successfully"}), 201
            except Exception as e:
                db.session.rollback()
                abort(500, message=f"Error creating chapter: {e}")
                #return {"message": f"Error creating chapter: {e}"}, 500
        else:
            abort(409, message=f"Chapter with name: '{name}', already exists.")

class ChapterIdAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required("token")
    def get(self, chapter_id):      
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            abort(404, message="Chapter not found")
            #return jsonify({"message": "Chapter not found"}), 404
        return chapter
    
    @auth_required("token")
    @roles_required("admin")
    def delete(self, chapter_id):
        chapter = Chapter().query.get(chapter_id)
        if not chapter:
            abort(404, message="Chapter does not exist")
        try:
            db.session.delete(chapter)
            db.session.commit()
            return sendResponse(201, message=f"Chapter '{chapter.id}: {chapter.name}' deleted successfully")
            #return jsonify({"message": "Chapter deleted successfully"}), 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error deleting chapter: {e}")
            #return {"message": f"Error deleting chapter: {e}"}, 500

class SubjectChaptersAPI(Resource):
    # GET CHAPTERS FOR A SUBJECT
    @marshal_with(chapter_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            abort(404, message="Subject does not exist")
            #return jsonify({"message": "Subject does not exist"}), 404
        else:
            chapters = subject.chapters
            return chapters
    
class ChapterQuizAPI(Resource):
    # GET QUIZZES FOR A CHAPTER
    @marshal_with(quiz_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self, chapter_id):
        chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not chapter:
            abort(400, message="Chapter does not exist")
            #return jsonify({"message": "Chapter does not exist"}), 400
        quizzes = chapter.quizzes
        if not quizzes:
            abort(400, message="No quizzes for this chapter")
            #return jsonify({"message": "No quizzes for this chapter"}),400
        return quizzes

class QuizAPI(Resource):
    # GET ALL QUIZZES (TEMPORARY FOR TESTING)
    @marshal_with(quiz_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self):
        quizzes = Quiz.query.all()
        if not quizzes:
            abort(404, message="No quizzes created")
            #return jsonify({"message":"No quizzes created"}), 404
        return quizzes
        

    # CREATE NEW QUIZ
#{
#   "name": "Sample Quiz",
#   "description": "A test quiz on math",
#   "chapter_id": 5,
#   "questions": [
#     {
#       "text": "What is 2+2?",
#       "type": "single_choice",
#       "options": ["2", "3", "4", "5"],
#       "correct_answers": [2]
#     },
#     {
#       "text": "Select prime numbers",
#       "type": "multiple_choice",
#       "options": ["2", "3", "4", "5"],
#       "correct_answers": [0, 1, 3]
#     },
#     {
#       "text": "What is the value of π (approx)?",
#       "type": "numerical",
#       "correct_range": [3.14, 3.15]
#     }
#   ]
# }
    @auth_required("token")
    @roles_required("admin")
    @roles_accepted("admin")
    def post(self):
        data = request.get_json()
        # Validate required fields
        required_fields = ["name", "description", "chapter_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            abort(404,message=f"Missing requrired fields: {", ".join(missing_fields)}")
            #return jsonify({"message":f"Missing requrired fields: {", ".join(missing_fields)}"}), 404
        if not data.get("questions"):
            abort(404, message="Quiz must have atleast one question.")
            #return jsonify({"message":"Quiz must have atleast one question."}), 400
        
        try:
            with db.session.begin_nested():
                quiz = Quiz(
                    name = data["name"],
                    description = data["description"],
                    chapter_id = data["chapter_id"],
                    total_marks=data["total_marks"],
                    time_limit=data.get("time_limit")
                )
                db.session.add(quiz)
                db.session.flush()

                for q in data["questions"]:
                    question = Question(
                        quiz_id = quiz.id,
                        question_statement = q.get("question_statement"),
                        ans_type = q.get("type"),
                        options = q.get("options"),
                        correct_min = q.get("correct_min"),
                        correct_max = q.get("correct_max"),
                        correct_options = q.get("correct_ans"),
                        marks = q.get("marks")
                    )
                    db.session.add(question)
                db.session.commit()
            return sendResponse(201, message="Quiz created successfully")
            #return jsonify({"message":"Quiz created successfully."}), 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error creating quiz {str(e)}")
            #return jsonify({"message":f"Error creating quiz {str(e)}"})

class QuizChapterAPI(Resource):
    @marshal_with(quiz_fields)
    @auth_required('token')
    @roles_accepted('user', 'admin')
    def get(self, chapter_id):
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            abort(404, message="Chapter does not exist.")
        quizzes = chapter.quizzes
        if not quizzes:
            abort(404, message="Currently no quiz exists for this chapter.")
        return quizzes
        
        
class QuizIdAPI(Resource):
    @marshal_with(quiz_fields_with_questions)
    @auth_required("token")
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            abort(404, message="Quiz does not exist")
            #return jsonify({"message": "Quiz does not exist"}),404
        return quiz
    
    @auth_required("token")
    @roles_required("admin")
    def delete(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            abort(404, message="Quiz does not exist")
            #return jsonify({"message": "Quiz does not exist"}), 404
        try:
            db.session.delete(quiz)
            db.session.commit()
            return sendResponse(200, message="Quiz deleted successfully")
            #return jsonify({"message": "Quiz deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error deleting quiz {e}")
            #return jsonify({"message": f"Error deleting quiz {e}"}), 500




class QuestionsAPI(Resource):
    # GET QUSTIONS FOR A QUIZ
    @marshal_with(question_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            abort(400, message="Chapter does not exist")
            #return jsonify({"message": "Chapter does not exist"}), 400
        questions = quiz.questions
        return questions
    
    # Incorrect Implementation
    # # CREATE A QUESTION
    # @auth_required("token")
    # @roles_required("admin")
    # def post(self):
    #     data = request.get_json()
    #     question_statement = data.get("question_statement")
    #     options = data.get("options")
    #     correct_options = data.get("correct_options")
    #     marks = data.get("marks")
    #     quiz_id = data.get("quiz_id")
    #     if not question_statement or options or correct_options or marks or quiz_id:
    #         return jsonify({"message": "Invalid inputs"}), 404
    #     quiz = Quiz.query.get(quiz_id)
    #     try: 
    #         question = Question(question_statement=question_statement, options=options, correct_options=correct_options, marks=marks) # type: ignore
    #         db.session.add(question)
    #         quiz.questions.extend([question]) # type: ignore
    #         db.session.commit()
    #         return jsonify({"message": "Question created successfully"}), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({"message": f"Error creating question {e}"}), 500
        
class QuestionIdAPI(Resource):
    # # Not required
    # @marshal_with(question_fields)
    # @auth_required("token")
    # @roles_accepted("admin","user")
    # def get(self, question_id):
    #     question = Question.query.get(question_id)
    #     if not question:
    #         return jsonify({"message": "Question does not exist"}), 400
    #     return question
                
    @auth_required("token")
    @roles_required("admin")
    def delete(self, question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(400, message="Question does not exist")
            #return jsonify({"message": "Question does not exist"}), 400
        try:
            db.session.delete(question)
            db.session.commit()
            return sendResponse(200, message="Question deleted succeessfully")
            #return jsonify({"message": "Question deleted succeessfully"}), 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error deleting question {e}")
            
class AttemptsAPI(Resource):
    @auth_required("token")
    @roles_accepted("user", "admin")
    @marshal_with(attempts_fields)
    def get(self, user_id, quiz_id):
        attempts = Attempt.query.filter_by(student_id = user_id, quiz_id = quiz_id).order_by(Attempt.attempt_number.desc()).all()
        if not attempts:
            abort(404, message="User has not attempt this quiz before")
        return attempts


class ResponseAPI(Resource):
    @auth_required("token")
    @roles_accepted("admin","user")
    def post(self, quiz_id):
        data = request.get_json()
        user_id = data.get("user_id")
        response = data.get("responses")
        
        if not response or not user_id:
            abort(400, message="Missing student id or responses")
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            abort(404, message="No quiz corresponding to given quiz id")
        try:
            prev_attempt = Attempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).order_by(Attempt.attempt_number.desc()).first()
            new_attempt_number = (prev_attempt.attempt_number+1) if prev_attempt else 1
            new_attempt = Attempt(student_id=user_id, quiz_id=quiz_id, attempt_number=new_attempt_number)
            db.session.add(new_attempt)
            db.session.flush()
            for answer in response:
                attempt_id = new_attempt.id
                question_id = int(answer["question_id"])
                answer = (answer.get("answer") if answer.get("answer") != [] else None)
                res = Response(attempt_id=attempt_id, question_id=question_id, answer=answer)
                db.session.add(res)
            db.session.commit()
            ## Grading process to come later.
            return sendResponse(201, message="Responses recorded successfully.")
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error in recording responses: {e}")
    
    @marshal_with(response_fields)
    @auth_required("token")
    @roles_accepted("admin","user")
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            abort(404, message="No quiz corresponding to given quiz id")
        attempt = Attempt.query.filter_by(quiz_id=quiz_id).first()
        responses = attempt.responses
        return responses

api.add_resource(SubjectAPI, "/subject") # Get list of all subjects or create a new subject
api.add_resource(SubjectIdAPI, "/subject/<int:subject_id>") 
api.add_resource(ChapterAPI, "/chapter")
api.add_resource(ChapterIdAPI, "/chapter/<int:chapter_id>")
api.add_resource(SubjectChaptersAPI, "/subject/<int:subject_id>/chapter")
api.add_resource(QuizChapterAPI, "/chapter/<int:chapter_id>/quiz")
api.add_resource(QuizAPI, "/quiz")
api.add_resource(QuizIdAPI, "/quiz/<int:quiz_id>")
api.add_resource(QuestionsAPI, "/question")
api.add_resource(QuestionIdAPI, "/question/<int:question_id>")
api.add_resource(ResponseAPI, "/quiz/<int:quiz_id>/response")
api.add_resource(AttemptsAPI, "/quiz/<int:user_id>/<int:quiz_id>/attempts")

