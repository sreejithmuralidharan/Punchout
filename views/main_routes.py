from flask import Blueprint, render_template, request, current_app

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return_url = request.args.get('return_url', '')
    current_app.logger.info(f"Index - Return URL: {return_url}")
    return render_template('index.html', return_url=return_url)
