from . import db, bcrypt
from .models import Reader, Book, Author, book_author, user_books

from flask import Blueprint, jsonify, request
from flask_login import login_required, logout_user, current_user, login_user
from sqlalchemy.exc import IntegrityError

main = Blueprint('main', __name__)


"""BOOK STUFF"""
# DISCLAIMER!! Trying out if shit works. Stuff to modify later
# TODO: ADD complete, delete, update functionality


@main.route('/add_book', methods=['POST'])
def add_book():
    """
    Get's book and author data and creates relationship between the two
    """
    # TODO: make book-user relationship with login required
    # get book data
    overall_data = request.get_json()
    new_book = Book(title=overall_data['title'],
                    num_pages=overall_data['num_pages'])
    # get author data
    if 'second_name' in overall_data:
        new_author = Author(first_name=overall_data['first_name'],
                            last_name=overall_data['last_name'],
                            second_name=overall_data['second_name'])
    else:
        new_author = Author(first_name=overall_data['first_name'],
                            last_name=overall_data['last_name'])
    # add and commit to db
    db.session.add(new_book)
    db.session.add(new_author)
    db.session.commit()
    # add new_book and new_author to relationship table
    new_book.authored_by.append(new_author)
    db.session.commit()
    return 'Done', 200


@main.route('/books')
def books():
    book_list = Book.query.all()
    books = []

    for book in book_list:
        books.append({'title': book.title, 'num_pages': book.num_pages,
                      'date_started': book.date_started})

    return jsonify({'books': books})


# @main.route('/user_bs')
# def user_bs():
#     ub_list = db.session.query(user_books).all()
#     u_books = []
#     users = db.session.query(Reader).all()
#     for reader in users:
#         for book in reader.user_books:
#             data = {
#                 'title': book.title,
#                 'username': reader.username
#             }

#             u_books.append(data)
#     return jsonify({"u_books": u_books})

@main.route('/<int:reader_id>/user_bs')
def user_bs(reader_id):
    ub_list = user_books
    return jsonify({"ub_list": ub_list})

@main.route('/books_authors')
def books_authors():
    """returns json with books and their authors"""
    ba_list = db.session.query(book_author).all()
    books_authors = []
    authors = db.session.query(Author).all()
    # SAME AS BELOW
    # result = db.session.query(
    #     Book.title, 
    #     Author.first_name, 
    #     book_author)
    #     .filter(book_author.c.book_id == Book.id)
    #     .filter(book_author.c.author_id == Author.id)
    #     .all()
    for author in authors:
        for book in author.author_books:
            ba = {
                'title': book.title,
                'num_pages': book.num_pages,
                'date_started': book.date_started,
                'first_name': author.first_name,
                'last_name': author.last_name,
            }

            books_authors.append(ba)

    return jsonify({'books_authors': books_authors})


@main.route('/book/<int:book_id>', methods=['GET'])
def book(book_id):
    book = Book.query.get_or_404(book_id)
    print(author)
    book_json = {
        "title": book.title,
        "date_started": book.date_started,
        "num_pages": book.num_pages}
    return jsonify({'book_json': book_json})


"""USER STUFF"""
# TODO: add update account info shit


@main.route('/register', methods=['POST'])
def register():
    """
    Register new user and encrypt password
    Check if user already exists
    Encrypt password
    """
    # Get json data
    register_data = request.get_json()
    new_user = Reader(
        username=register_data['username'],
        email=register_data['email'],
        # encrypt password before db commit
        password=bcrypt.generate_password_hash(
            register_data['password']).decode('utf-8')
    )
    # commit to db
    try:
        # if user doesn't exist
        db.session.add(new_user)
        db.session.commit()
        return 'User {} has been registered'.format(new_user.username)
    except IntegrityError:
        # if user already exists
        return 'User with this email and/or username already exists'


@main.route('/login', methods=['GET', 'POST'])
def login():
    login_data = request.get_json()
    login_user = Reader(
        email=login_data['email'],
        password=login_data['password']
    )
    user = Reader.query.filter_by(email=login_user.email).first()
    if user and bcrypt.check_password_hash(user.password, login_user.password):
        # TODO: Grant logged in user access to site
        return '!!!!!!!!!!LOGOGOGOGOGOGGOOGOGOGOEDDDDDD INNNN!!!!!!'
    else:
        return '!!!!!!!NOOOOOOOOOOO!!!!!!!!'


@main.route('/account/update', methods=['GET', 'POST'])
def update_account():
    """Updates account info"""
    # Need further research
    pass


"""USER-BOOK STUFF"""
# TODO: show user books and stats and shit
