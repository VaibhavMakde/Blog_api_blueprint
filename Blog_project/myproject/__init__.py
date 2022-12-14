import logging
from flask import Flask

from .extensions import db, migrate, jwt, redis_cache


def create_app():
    #  logging Baisc Configurations

    logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s : %(message)s')

    app = Flask(__name__)

    # ////////////////////// app config ///////////////////////////////

    app.config['SECRET_KEY'] = '01d30bbff986007764fabbdf'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///////home/vaibhav/PycharmProjects/blog with blue print/Blog_project/myproject/blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # set up the Flask-JWT-Extended extension
    app.config[
        "JWT_SECRET_KEY"] = "0ddf5597e02d981f8803c4cc11f015a4e52679d706edb29b595d9e466def5bcf95273a3053ab5d97ee893c23e4023b912daefaade316406a33b7685d4d223dfa"
    app.debug = True

    # configure the redis
    app.config["REDIS_HOST"] = "localhost"
    app.config["REDIS_PASSWORD"] = "password"
    app.config["REDIS_PORT"] = 6379

    # register the API blueprints
    from .routes.routes import api
    app.register_blueprint(api)

    '''The init_app method exists so that the SQLite3 
        object can be instantiated without requiring an app object. '''
        
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    redis_cache.init_app(app)

    return app


'''STEPS TO RUN PROJECT:


1.export FLASK_APP=myproject
2. export FLASK_DEBUG=1
3.flask run
4.http://127.0.0.1:5000/

'''
