from flask import Flask
from views.main_routes import main
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.register_blueprint(main)

# Configure the app using environment variables
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
app.config['ENV'] = 'development' if app.config['DEBUG'] else 'production'
app.config['SECRET_KEY'] = '8f4b8a3df1294ab6b2c5e657d8329f7fbc32e1ab7b6dc2d8c0e64f3a2e1f3c9e'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
