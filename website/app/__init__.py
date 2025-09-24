from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .routes import bp
    app.register_blueprint(bp)

    return app
