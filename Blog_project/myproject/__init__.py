from flask import Flask
from .routes.routes import api

from .extensions import db, migrate,jwt


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '01d30bbff986007764fabbdf'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///////home/vaibhav/PycharmProjects/blog with blue print/Blog_project/myproject/blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # set up the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = "0ddf5597e02d981f8803c4cc11f015a4e52679d706edb29b595d9e466def5bcf95273a3053ab5d97ee893c23e4023b912daefaade316406a33b7685d4d223dfa"

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    app.register_blueprint(api)

    return app


'''STEPS TO RUN PROJECT:
1.export FLASK_APP=myproject
2.flask run
'''
