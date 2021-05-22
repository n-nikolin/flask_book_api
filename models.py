from . import db
from datetime import datetime, timedelta

# user_books = db.Table('user_books',
#                       db.Column('reader_id', db.Integer, db.ForeignKey(
#                           'reader.id'), primary_key=True),
#                       db.Column('book_id', db.Integer, db.ForeignKey(
#                           'book.id'), primary_key=True)
#                       )


book_author = db.Table('book_author',
                       db.Column('author_id', db.Integer, db.ForeignKey(
                           'author.id'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey(
                           'book.id'), primary_key=True)
                       )


class Reader(db.Model):
    __tablename__ = 'reader'
    # table columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    # relationship columns
    user_books = db.relationship('Book', backref='reader_books')


class Author(db.Model):
    __tablename__ = 'author'
    # table columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    second_name = db.Column(db.String(30), nullable=True)
    # relationship columns
    author_books = db.relationship(
        'Book', secondary=book_author, backref=db.backref('authored_by', lazy='dynamic'))

class Book(db.Model):
    __tablename__ = 'book'
    # table columns
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    num_pages = db.Column(db.Integer, nullable=False)
    date_started = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    date_finished = db.Column(db.DateTime, nullable=True)
    reading_time = db.Column(db.Interval, nullable=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('reader.id'))
    complete = db.Column(db.Boolean, default=False, nullable=False)
