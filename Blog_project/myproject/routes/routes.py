import uuid
from ast import literal_eval

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db, redis_cache
from ..models.models import User, Blog, Comment, CommentSchema, BlogSchema, UserSchema
from flask import current_app as app

from ..constants import USER_LIST, BLOG_LIST, COMMENT_LIST

api = Blueprint('api', __name__)


@api.route("/hello")
def hello():
    return jsonify({'message': 'New user created!'})


login_manager = LoginManager()

'''
Flask-login also requires you to define a “user_loader” function which,
given a user ID, returns the associated user object.
The @login_manager.user_loader
piece tells Flask-login how to load users given an id.'''


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@api.route('/signup', methods=['POST'])
def signup():
    username = request.json.get("username", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    username_exists = User.query.filter_by(username=username).first()
    if username_exists:
        app.logger.info("Username already exits")
        return jsonify({'message': 'Username already exits !'})

    email_exists = User.query.filter_by(email=email).first()
    if email_exists:
        app.logger.info("email already exits !")
        return jsonify({'message': 'email already exits !'})

    hashed_password = generate_password_hash(password=password, method='sha256')
    print(hashed_password)
    new_user = User(public_id=str(uuid.uuid4()), username=username, email=email, password=hashed_password,
                    admin=False)
    db.session.add(new_user)
    db.session.commit()
    app.logger.info("New User Created")
    return jsonify({'message': 'New user created!'})


@api.route('/login', methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            print(access_token)
            return jsonify(access_token=access_token)
            app.logger.info("Logged in successfully!")
            return jsonify({'message': 'Logged in successfully!'})

        else:
            app.logger.info("Incorrect Password!")
            return jsonify({'message': 'Incorrect Password !'})

    else:
        app.logger.info("User does not exits !!!")
        return jsonify({'message': "User does not exits !!!"})


#
# @api.route('/user', methods=['GET'])
# @jwt_required()
# def get_all_users():
#
#     users = User.query.all()
#
#     if users:
#         # marshmallow serialization on user
#         user_schema = UserSchema(many=True)
#         output = user_schema.dump(users)
#         # if redis_client.exits()
#
#         app.logger.info("Users : %s", users)
#         return jsonify({'users': output})
#     else:
#         app.logger.info("No user found !!!")
#         return jsonify({'message': 'No user found'})


@api.route('/user', methods=['GET'])
@jwt_required()
def get_all_users():
    if redis_cache.exists(USER_LIST):
        print("Getting User Data from redis Cache")
        users = redis_cache.get(USER_LIST)
        '''UTF8 Decoder is a variable-length character
         decoding that can make any Unicode character readable.
         Safely evaluate an expression node or a string containing
         a Python  expression. '''
        users = literal_eval(users.decode('utf8'))
        app.logger.info("User : %s", users)
        return jsonify({'users': users})
    else:
        print("Getting User Data from Sqlite")
        users = User.query.all()
        user_schema = UserSchema(many=True)
        users = user_schema.dump(users)
        users = str(users)
        redis_cache.set(USER_LIST, users)
        print("User cache set")
        app.logger.info("User : %s", users)
        return jsonify({'users': users})


@api.route('/user/<public_id>', methods=['GET'])
@jwt_required()
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        app.logger.info("No user found !!!")
        return jsonify({'message': 'No user found!'})

    user_schema = UserSchema()
    output = user_schema.dump(user)
    app.logger.info("User : %s", output)

    return jsonify({'user': output})


# promoting user to admin
@api.route('/user/<public_id>', methods=['PUT'])
@jwt_required()
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        app.logger.info("No user found !!!")
        return jsonify({'message': 'No user found!'})

    user.admin = True
    db.session.commit()
    app.logger.info('The user has been promoted!')
    return jsonify({'message': 'The user has been promoted!'})


@api.route('/user/<public_id>', methods=['DELETE'])
@jwt_required()
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        app.logger.info("No user found !!!")
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()
    app.logger.info("'The user has been deleted!'!!!")
    return jsonify({'message': 'The user has been deleted!'})


@api.route('/blog', methods=['GET'])
@jwt_required()
def get_all_blog():
    if redis_cache.exists(BLOG_LIST):
        print("Getting Blog Data from redis Cache")
        blogs = redis_cache.get(BLOG_LIST)
        blogs = literal_eval(blogs.decode('utf8'))
        return jsonify({'users': blogs})
    else:
        print("Getting Blog Data from Sqlite")
        blogs = Blog.query.all()

        # Blog serialization using marshmallow
        blog_schema = BlogSchema(many=True)
        blogs = blog_schema.dump(blogs)
        blogs = str(blogs)
        # setting the redis cache
        redis_cache.set(BLOG_LIST, blogs)
        print("User cache set")

        return jsonify({'Blogs': blogs})


@api.route('/blog/<blog_id>', methods=['GET'])
@jwt_required()
def get_one_blog(blog_id):
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    blog = Blog.query.filter_by(id=blog_id).first()

    if not blog:
        app.logger.info("No Blog found!")
        return jsonify({'message': 'No Blog found!'})

    # Blog serialization using marshmallow
    blog_schema = BlogSchema()
    output = blog_schema.dump(blog)
    app.logger.info("Blog : %s!", output)
    return jsonify(output)


@api.route('/blog/search', methods=['POST'])
@jwt_required()
def search():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()

    try:
        if data['title']:
            search_by_title = data['title']
            blog = Blog.query.filter_by(title=search_by_title).first()
    except:
        pass

    try:
        if data['author']:
            search_by_author = data['author']
            blog = Blog.query.filter_by(author=search_by_author).first()
    except:
        pass

    try:
        if data['blog']:
            search_by_blog = data['blog']
            blog = Blog.query.filter_by(blog=search_by_blog).first()
    except:
        pass

    if not blog:
        app.logger.info("No Blog found!")
        return jsonify({'message': 'No Blog found!'})

    # Blog serialization using marshmallow
    blog_schema = BlogSchema()
    output = blog_schema.dump(blog)
    app.logger.info("Output : %s", output)
    return jsonify(output)


@api.route('/blog', methods=['POST'])
@jwt_required()
def create_blog():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    title = request.json.get("title", None)
    blog = request.json.get("blog", None)

    if title and blog:
        new_blog = Blog(title=title, blog=blog, author=current_user)
        db.session.add(new_blog)
        db.session.commit()
        app.logger.info("Blog created  !!!")
        return jsonify({'message': "Blog created!"})
    else:
        app.logger.info("Blog does not created! missing some fields")
        return jsonify({'message': "Blog does not created! missing some fields"})


@api.route('/blog/<blog_id>', methods=['DELETE'])
@jwt_required()
def delete_blog(blog_id):
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    blog = Blog.query.filter_by(id=blog_id, author=current_user).first()
    if blog:
        db.session.delete(blog)
        db.session.commit()
        app.logger.info('BLog item deleted!')
        return jsonify({'message': 'BLog item deleted!'})
    else:
        app.logger.info("No Blog found!")
        return jsonify({'message': 'No Blog found!'})


@api.route('/blog/<blog_id>/comment', methods=['GET'])
@jwt_required()
def get_all_comment(blog_id):
    if redis_cache.exists(COMMENT_LIST + blog_id):
        print(COMMENT_LIST + blog_id)
        print("Getting Comment Data from redis Cache")
        comments = redis_cache.get(COMMENT_LIST + blog_id)
        comments = literal_eval(comments.decode('utf8'))
        return jsonify({'comments': comments})

    else:
        print("Getting User Data from Sqlite")
        comments = Comment.query.filter_by(post_id=blog_id).all()
        if comments:
            comment_schema = CommentSchema(many=True)
            comments = comment_schema.dump(comments)
            comments = str(comments)
            redis_cache.set(COMMENT_LIST + blog_id, comments)
            print("Comment cache set")

            return jsonify({'comments': comments})
        else:
            return jsonify({'message': "No Comments Found"})


@api.route('/blog/<blog_id>/comment/<comment_id>', methods=['GET'])
@jwt_required()
def get_one_comment(blog_id, comment_id):
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    comment = Comment.query.filter_by(id=comment_id).first()
    blog = Blog.query.filter_by(id=blog_id).first()
    print(comment)
    print(blog)

    if comment and blog:
        comment_schema = CommentSchema()
        comment_data = comment_schema.dump(comment)
        comment_data['Blog'] = blog.blog
        comment_data['Blog Title'] = blog.title
        app.logger.info("Comment Data : %s", comment_data)
        return jsonify(comment_data)

    else:
        app.logger.info("No comment Found !!!")

        return jsonify({"message": "No comment Found !!!"})


@api.route('/blog/<blog_id>/comment', methods=['POST'])
@jwt_required()
def create_comment(blog_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    new_comment = Comment(text=data['text'], author=current_user, post_id=blog_id)

    db.session.add(new_comment)
    db.session.commit()
    app.logger.info("Commented on Blog!")

    return jsonify({'message': "Commented on Blog!"})


@api.route('/blog/<blog_id>/comment/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(blog_id, comment_id):
    current_user = get_jwt_identity()

    comment = Comment.query.filter_by(id=comment_id, author=current_user).first()

    if not comment:
        app.logger.info('No Comment found by User!')
        return jsonify({'message': 'This comment comment belong to other user!'})

    db.session.delete(comment)
    db.session.commit()
    app.logger.info('Comment  deleted!')

    return jsonify({'message': 'Comment  deleted!'})
