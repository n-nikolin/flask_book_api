from . import db, bcrypt
from .models import Reader, Book, Author, book_author
from .config import Config

from functools import wraps
import jwt
from datetime import datetime, timedelta
# import datetime
import uuid

from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint('main', __name__)


def token_required(f):
    """ checks if user is authenticated """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(
                token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = Reader.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# USER STUFF
"""
-get all - DONE
-get one - DONE
-create/register - DONE
-update account - !! DO IT LATER. CAN'T FIND A WAY TO UPDATE MULTIPLE COLUMNS
-delete account
-login - DONE
"""


@main.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # # THESE TWO LINES DO NOTHING
    # if not current_user:
    #     return jsonify({'message': 'You cannot perform that function'})

    user_list = Reader.query.all()
    users = []

    for user in user_list:
        users.append({
            'public_id': user.public_id,
            'username': user.username,
            'email': user.email,
            'password': user.password
        })

    return jsonify({'users': users})


@main.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    # THESE TWO LINES DO NOTHING
    if not current_user:
        return jsonify({'message': 'You cannot perform that function'})

    reader = Reader.query.filter_by(public_id=public_id).first()
    if not reader:
        return jsonify({"message": "No user found!"})

    reader_data = {
        "public_id": reader.public_id,
        "username": reader.username,
        "email": reader.email,
        "password": reader.password
    }

    return jsonify({'user': reader_data})


@main.route('/user', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Reader(
        public_id=str(uuid.uuid4()),
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})


@main.route('/login', methods=["GET", "POST"])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    reader = Reader.query.filter_by(email=auth.username).first()

    if not reader:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="No user found!"'})

    if check_password_hash(reader.password, auth.password):
        token = jwt.encode({'public_id': reader.public_id, 'exp': datetime.now(
        ) + timedelta(minutes=60)}, Config.SECRET_KEY)

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Invalid password!"'})


@main.route('/user/<public_id>', methods=['POST'])
def update_account(public_id):
    # it's shit and doesn't work
    # .update and .merge methods don't work
    # # making many if statements is stupid and won't work
    # user = Reader.query.filter_by(public_id=public_id).first()
    # if not user:
    #     return jsonify({'message': 'user not found'})
    # data = request.get_json()
    # print(data)
    # # insert for loop to go through json data and update user info
    # return jsonify({'message': 'user info updated'})
    pass


@main.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    pass


# BOOK STUFF

@main.route('/book', methods=['POST'])
@token_required
def add_book(current_user):
    """
    Adds book with reader_id to book table
    Adds author to author table
    Adds book and author ids to association table
    """
    data = request.get_json()
    # get book data
    new_book = Book(
        title=data['title'], num_pages=data['num_pages'], reader_id=current_user.id)
    # get author data
    if 'second_name' in data:
        new_author = Author(
            first_name=data['first_name'], last_name=data['last_name'], second_name=data['second_name'])
    else:
        new_author = Author(
            first_name=data['first_name'], last_name=data['last_name'])
    # add and commit to db
    db.session.add(new_book)
    db.session.add(new_author)
    db.session.commit()
    # add new_book and new_author to association table
    new_book.authored_by.append(new_author)
    db.session.commit()
    return 'Done', 200


@main.route('/<public_id>/books', methods=['GET'])
@token_required
def get_reader_books(current_user, public_id):
    """
    get user books with authors
    """
    # check if other users books return in current user query --DONE
    books = db.session.query(Book, Author, book_author).filter_by(reader_id=current_user.id).filter(
        Book.id == book_author.c.book_id).filter(Author.id == book_author.c.author_id).all()
    print(books)
    output = []
    for book in books:
        # TODO: deal with second_name bug
        # api returns second name as 'null'
        book_data = {
            'title': book.Book.title,
            'num_pages': book.Book.num_pages,
            'first_name': book.Author.first_name,
            'second_name': book.Author.second_name,
            'last_name': book.Author.last_name
        }
        output.append(book_data)

    return jsonify({current_user.username: output})

@main.route('/book/<int:book_id>', methods=['PUT'])
@token_required
def complete_book(current_user, book_id):
    book = Book.query.filter_by(id=book_id, reader_id=current_user.id).first()
    if book.reader_id != current_user.id:
        return jsonify({'message': 'not authorized'}), 401
    else:
        book.date_finished = datetime.now()
        book.complete = True
        book.reading_time = book.date_finished - book.date_started
        db.session.commit()
    
    return jsonify({'message': "'{}' marked as finished".format(book.title)})
