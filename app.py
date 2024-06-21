from flask import Flask
from views import main
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.register_blueprint(main)

# Configure the app using environment variables
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
app.config['ENV'] = 'development' if app.config['DEBUG'] else 'production'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
