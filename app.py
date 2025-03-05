from flask import Flask
from backend.config import Config
from backend.models import db, User, Role
from backend.resources import api
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_cors import CORS


def createApp():
    app = Flask(__name__, template_folder="frontend", static_folder="frontend")
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    api.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore=datastore, register_blueprint=False)  # type: ignore
    app.app_context().push()
    return app



app = createApp()

with app.app_context():
    db.create_all()
    userdatastore : SQLAlchemyUserDatastore = app.security.datastore # type: ignore
    userdatastore.find_or_create_role(name="admin", description="Administrator")
    userdatastore.find_or_create_role(name="user", description="Normal User")
    db.session.commit()
    if not userdatastore.find_user(email="admin@quizmaster.com"):
        userdatastore.create_user(name="Administrator", email="admin@quizmaster.com", password=hash_password("admin"), roles=["admin"])
    if not userdatastore.find_user(email="testuser@quizmaster.com"):
        userdatastore.create_user(name="Test User", email="testuser@quizmaster.com", password=hash_password("testuser"), roles=["user"])
    db.session.commit()

import backend.routes #noqa

if __name__ == "__main__":
    app.run(debug=True, port=8000)