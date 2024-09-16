"""
Boiler plate code to initialize service.
"""
from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from flask_login import LoginManager
from auth import auth_bp
from files import files_bp
from permissions import permissions_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(files_bp, url_prefix='/files')
app.register_blueprint(permissions_bp, url_prefix='/permissions')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

if __name__ == '__main__':
    app.run(debug=True)
