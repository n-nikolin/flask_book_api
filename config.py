class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/book_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret'