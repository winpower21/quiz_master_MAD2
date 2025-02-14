from flask import current_app as app
from flask import render_template, request, jsonify
from flask_security.decorators import auth_required
from flask_security.utils import verify_password, hash_password
from .models import db
from flask_security.datastore import SQLAlchemyUserDatastore


datastore : SQLAlchemyUserDatastore = app.security.datastore # type: ignore

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/protected")
@auth_required('token')
def protected():
    return "<h1>only accessible by user</h1>"


@app.route("/login", methods=["POST"]) # type: ignore
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Invalid inputs"}), 400
    
    if email:
        user = datastore.find_user(email=email)
        if not user:
            return jsonify({"message": "Invalid Email"}), 400
        else:
            if verify_password(password=password, password_hash=user.password): # type: ignore
                return jsonify({"token": user.get_auth_token(), "email":user.email, "role":user.roles[0].name, "id":user.id}), 200
            else:
                return jsonify({"message": "Invalid Password"}), 400
            
            
@app.route("/register", methods=["POST"]) # type: ignore
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not email or not name or not password:
        return jsonify({"message": "Invalid inputs"}), 400
    if email:
        user = datastore.find_user(email=email)
        if user:
            return jsonify({"message": "Email already exists"}), 400
        try:
            datastore.create_user(name=name, email=email, password=hash_password(password), roles = ["user"])
            db.session.commit()
            return jsonify({"message": "User created successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating user: {e}"}), 400
