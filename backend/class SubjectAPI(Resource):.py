class SubjectAPI(Resource):
    # Get list of all subjects
    @marshal_with(subject_fields)
    @auth_required('token')
    def get(self):
        subjects = Subject.query.all()
        if not subjects:
            return {"message": "No subjects found"}, 404
        return subjects

    # Create a new subject
    @auth_required('token')
    def post(self):
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        image_url = data.get("image_url")
        if not name or not description:
            return {"message": "Invalid inputs"}, 400
        subject = Subject(name=name, description=description, image_url=image_url) # type: ignore
        try:
            db.session.add(subject)
            db.session.commit()            
            return {"message": "Subject created successfully"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating subject: {e}"}, 400

class IdSubjectAPI(Resource):
    # Get a specific subject by ID
    @marshal_with(subject_fields)
    @auth_required('token')
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message":"Subject not found"}, 404
        return subject
    
    # Deleete a specific subject by ID
    @auth_required('token')
    def delete(self, subject_id):
        subject  = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        try:
            db.session.delete(subject)
            db.session.commit()
            return {"message": "Subject updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error updating subject: {e}"}, 400
    
    
class ChapterAPI(Resource):
    # Get list of all chapters
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self):
        data = request.get_json()
        sub = data.get("subject")
        subject = Subject.query.filter_by(name=sub).first()
        chapters = subject.chapters # type: ignore
        if not chapters:
            return {"message": "No chapters found"}, 404
        print(chapters)
        return chapters
    
    @auth_required('token')
    def post(self):
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        subject = data.get("subject")
        if not name or not description or not subject:
            return {"message": "Invalid inputs"}, 400
        chapter = Chapter(name=name, description=description) # type: ignore
        subject = Subject.query.filter_by(name=subject).first()
        if not subject:
            return {"message": "Subject not found"}, 404
        try:
            db.session.add(chapter)
            subject.chapters.extend([chapter])
            db.session.commit()
            return {"message": "Chapter created successfully"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating chapter: {e}"}, 400
        
class IdChapterAPI(Resource):
    @marshal_with(chapter_fields)
    @auth_required('token')
    def get(self, id):
api.add_resource(IdQuestionAPI, "/questions/<int:id>") # Get a specific question by ID or delete a specific question by ID or modify a specific question by ID
        chapter = Chapter.query.get(id)
        if not chapter:
            return {"message": "Subject not found"}, 404
        return chapter

    @auth_required('token')
    def delete(self, id):
        chapter = Chapter.query.get(id)
        if not chapter:
            return {"message": "Subject not found"}, 404
        
        db.session.delete(chapter)
        try:
            db.session.commit()
            return {"message": "Subject deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error deleting subject: {e}"}, 400
    

api.add_resource(SubjectAPI, "/subjects") # Get list of all subjects or create a new subject
api.add_resource(IdSubjectAPI, '/subjects/<int:subject_id>') # Get a specific subject by ID or delete a specific subject by ID or modify a specific subject by ID
api.add_resource(ChapterAPI, "/chapters") # Get list of all chapters or create a new chapter
api.add_resource(IdChapterAPI, "/chapters/<int:id>") # Get a specific chapter by ID or delete a specific chapter by ID or modify a specific chapter by ID
api.add_resource(QuizAPI, "/quiz") # Get list of all quizzes or create a new quiz
api.add_resource(IdQuizAPI, "/quiz/<int:id>") # Get a specific quiz by ID or delete a specific quiz by ID or modify a specific quiz by ID
api.add_resource(QuestionAPI, "/questions") # Get list of all questions or create a new question
api.add_resource(IdQuestionAPI, "/questions/<int:id>") # Get a specific question by ID or delete a specific question by ID or modify a specific question by ID
api.add_resource(AnswerAPI, "/answers") # Get list of all answers or create a new answer