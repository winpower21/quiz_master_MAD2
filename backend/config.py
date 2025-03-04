class Config():
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "my_precious_two"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Token"
    SECRET_KEY = "secret_key"
    WTF_CSRF_ENABLED = False
