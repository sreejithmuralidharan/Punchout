from flask import Flask
from views import main
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.register_blueprint(main)

# Configure the app using environment variables
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
app.config['ENV'] = 'development' if app.config['DEBUG'] else 'production'

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv('MONGODB_URI'))
app.db = mongo_client.get_database(os.getenv('MONGODB_DB'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
