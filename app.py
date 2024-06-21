from flask import Flask
from views import main
from pymongo import MongoClient

app = Flask(__name__)
app.register_blueprint(main)

# Configure the app with hardcoded values
app.config['DEBUG'] = True  # Set to False in production
app.config['ENV'] = 'development' if app.config['DEBUG'] else 'production'

# Initialize MongoDB client
mongo_client = MongoClient('mongodb+srv://sreeojcconsulting:QGkO89qCZ8jNqNZA@punchouttester.zwv1kcs.mongodb.net/?retryWrites=true&w=majority&appName=PunchoutTester')
app.db = mongo_client.get_database('PunchOut')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
