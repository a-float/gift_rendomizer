from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/already_logged_in')
@login_required
def already_logged_in():
    return render_template('already_logged_in.html')

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.already_logged_in'))
    else:
        return render_template('login.html', user_names = User.query.all())

@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        flash("Nie możesz się zarejestrować.")
        return redirect(url_for('auth.already_logged_in'))
    return render_template('signup.html', user_names = User.query.all())
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Wylogowano")
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['POST'])
def login_post():
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(name=name).first()

    if not user or user.password is None:
        flash('Zarejestruj się.')
        return redirect(url_for('auth.signup'))
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Złe dane, spróbuj ponownie.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(name=name).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        if user.password != None:
            flash('Ta prezentowiczka ustawiła już hasło')
            return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    print(f"{name} ustawiła hasło: {password}")
    user.password = password=generate_password_hash(password, method='sha256')
    # new_user = User(name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    # db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))
    