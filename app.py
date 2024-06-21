from flask import Flask
from pymongo import MongoClient
from views import main
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Load environment variables from .env

    app = Flask(__name__)
    app.register_blueprint(main)

    # Configure the app using environment variables
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.config['ENV'] = 'development' if app.config['DEBUG'] else 'production'
    app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb+srv://sreeojcconsulting:QGkO89qCZ8jNqNZA@punchouttester.zwv1kcs.mongodb.net/?retryWrites=true&w=majority&appName=PunchoutTester')
    app.config['MONGO_DB'] = os.getenv('MONGODB_DB', 'PunchOut')

    # Initialize MongoDB client
    try:
        mongo_client = MongoClient(app.config['MONGO_URI'])
        app.db = mongo_client[app.config['MONGO_DB']]
    except Exception as e:
        app.logger.error(f"Error initializing MongoDB client: {e}")
        raise e

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
