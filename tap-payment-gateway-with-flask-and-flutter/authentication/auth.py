from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from datetime import datetime
from ..models.models import User
import shortuuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user

auth = Blueprint('auth',__name__,template_folder='templates',static_folder='static', static_url_path='/assets')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.objects(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Store user ID in the session
            return redirect(url_for('main.get_coupons'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('All the fields are manadatory, please fill and try again')
            return redirect(url_for('auth.signup'))
        created_at = datetime.utcnow()
        user = User.objects(email=email).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('auth.signup'))
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256'),
            db_user_id=shortuuid.ShortUUID().random(length=24),
            created_at=created_at
            )
        new_user.save()
        return redirect(url_for('auth.login'))

    elif request.method == 'GET':
        return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
