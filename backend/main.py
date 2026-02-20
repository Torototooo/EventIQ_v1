from flask import Flask
from models import db
import os
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth



app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config['GOOGLE_CLIENT_ID'] = 'Google client id'
app.config['GOOGLE_CLIENT_SECRET'] = 'Google client secret'

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mail'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'EventIQ '

mail = Mail(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///TechEvent.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "eventiq-secret-key-change-this"


UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads", "company_logos")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


db.init_app(app)

from models import User, Host, Event


with app.app_context():
    db.create_all()


from routes import *


if __name__ == "__main__":
    app.run(debug=True)
