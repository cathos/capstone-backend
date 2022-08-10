import os
from flask import Flask
from flask_cors import CORS
# from dotenv import load_dotenv

# load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # if test_config is None:
        # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        #     "SQLALCHEMY_DATABASE_URI")
    # else:
    #     app.config["TESTING"] = True
        # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        #     "SQLALCHEMY_TEST_DATABASE_URI")

    # Import models here for Alembic setup
    # from app.models.task import Task
    # from app.models.goal import Goal

    # db.init_app(app)
    # migrate.init_app(app, db)

    # Register Blueprints here
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    from .routes import roast_bp
    app.register_blueprint(roast_bp)

    return app