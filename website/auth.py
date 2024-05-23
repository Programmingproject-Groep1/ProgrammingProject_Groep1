from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

#Inlogpagina
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form.get('password')
        if any(char in email for char in ['<', '>', "'", '"']) or any(char in password for char in ['<', '>', "'", '"']):
            flash('Ongeldige invoer: verboden tekens', category='modalerror')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in succesfully!', category='modal')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again', category='modalerror')
            else:
                flash('Email does not exist.', category='modalerror')
    
    return render_template("login.html", user=current_user)

#Uitloggen
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


#Account aanmaken
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        userType = request.form.get('userType')
        if any(char in email for char in ['<', '>', "'", '"']) or any(char in first_name for char in ['<', '>', "'", '"']) or any(char in password1 for char in ['<', '>', "'", '"']) or any(char in password2 for char in ['<', '>', "'", '"']):
            flash('Ongeldige invoer: verboden tekens', category='modalerror')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='modalerror')
            elif len(email) < 4:
                flash('Email must be greater than 4 characters', category='modalerror')
            elif len(first_name) < 2:
                flash('First name must be greater than 1 character', category='modalerror')
            elif password1 != password2:
                flash('Passwords don\'t match', category='error')
            elif len(password1) < 7:
                flash('Password must be greater than 7 characters', category='modalerror')
            else:
                try:
                    new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256', salt_length= 16), type_id=userType)
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                    flash('Account created!', category='modal')
                    return redirect(url_for('views.home'))
                except Exception as e:
                    flash(f'Error creating account: {str(e)}', category='modalerror')
                    db.session.rollback()  # Rollback changes if an error occurs

            
           

    return render_template("signup.html", user=current_user)