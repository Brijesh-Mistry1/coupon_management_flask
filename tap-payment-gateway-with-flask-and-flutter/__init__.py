from flask import Flask, jsonify, redirect, url_for
from flask_mongoengine import MongoEngine
from .models.models import User
import json
import secrets
from flask_login import LoginManager
from decouple import config

DATABASE_NAME = config('DATABASE_NAME')
DATABASE_HOST = config('DATABASE_HOST')
DATABASE_PORT = config('DATABASE_PORT')
SECRET_KEY = config('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGODB_SETTINGS'] = {
    'db':DATABASE_NAME,
    'host':DATABASE_HOST,
    'port': int(DATABASE_PORT)
}

db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'


from .authentication.auth import auth as authblueprint
app.register_blueprint(authblueprint)

from .main.views import main as main_blueprint
app.register_blueprint(main_blueprint, url_prefix='/dashboard')

from .coupons.coupon import coupon as coupon_blueprint
app.register_blueprint(coupon_blueprint)

from .payments.payment import payment as payment_blueprint
app.register_blueprint(payment_blueprint)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except:
        return redirect(url_for('auth.signup'))


if __name__ == "__main__":
    app.run(debug=True)