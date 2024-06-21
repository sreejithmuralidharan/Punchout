from flask import Flask

def create_app():
    app = Flask(__name__)

    # Set a secret key for the session
    app.config['SECRET_KEY'] = '8f4b8a3df1294ab6b2c5e657d8329f7fbc32e1ab7b6dc2d8c0e64f3a2e1f3c9e'

    # Import and register blueprints
    from .views.main_routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
